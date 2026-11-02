# -*- coding: utf-8 -*-
"""三国狼人杀 - 基于 AgentScope 的中文版狼人杀游戏。

对应教程：hello-agents/code/chapter6/AgentScopeDemo/main_cn.py

适配说明：教程使用 DashScopeChatModel（需要 DASHSCOPE_API_KEY），
本项目复用仓库根目录 .env 的 OpenAI 兼容配置
（LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_ID），
因此改用 OpenAIChatModel + OpenAIMultiAgentFormatter。

游戏流程：
    夜晚: 狼人 MsgHub 讨论并投票击杀 -> 预言家查验 -> 女巫救人/毒人
    白天: 全员 MsgHub 讨论 -> 全员投票 -> 猎人开枪
    胜负: 狼人全灭 -> 好人胜利；狼人数量 >= 好人 -> 狼人胜利
"""

import asyncio
import os
import random
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OpenAIMultiAgentFormatter
from agentscope.pipeline import MsgHub, sequential_pipeline, fanout_pipeline

from prompt_cn import ChinesePrompts
from game_roles import GameRoles
from structured_output_cn import (
    DiscussionModelCN,
    get_vote_model_cn,
    WitchActionModelCN,
    get_seer_model_cn,
    get_hunter_model_cn,
    WerewolfKillModelCN,
)
from utils_cn import (
    check_winning_cn,
    majority_vote_cn,
    get_chinese_name,
    format_player_list,
    GameModerator,
    MAX_GAME_ROUND,
    MAX_DISCUSSION_ROUND,
)

# 仓库根目录：code/chapter06-frameworks/agentscope -> 向上 3 级
ROOT_DIR = Path(__file__).resolve().parents[3]


class ThreeKingdomsWerewolfGame:
    """三国狼人杀游戏主类（游戏控制层）。

    统一维护游戏状态：
    - self.players: 所有玩家 Agent 字典（name -> ReActAgent）
    - self.roles: 每个玩家对应的游戏角色
    - self.alive_players: 当前存活的 Agent 列表
    - self.werewolves / self.villagers / self.seer / self.witch / self.hunter: 分阵营列表
    - self.witch_has_antidote / self.witch_has_poison: 女巫道具状态
    """

    def __init__(self) -> None:
        self.players: Dict[str, ReActAgent] = {}
        self.roles: Dict[str, str] = {}
        self.moderator = GameModerator()
        self.alive_players: List[ReActAgent] = []
        self.werewolves: List[ReActAgent] = []
        self.villagers: List[ReActAgent] = []
        self.seer: List[ReActAgent] = []
        self.witch: List[ReActAgent] = []
        self.hunter: List[ReActAgent] = []

        # 女巫道具状态
        self.witch_has_antidote = True
        self.witch_has_poison = True

    def _create_model(self) -> OpenAIChatModel:
        """创建 OpenAI 兼容模型客户端（所有玩家共用同一配置）。"""
        return OpenAIChatModel(
            model_name=os.environ["LLM_MODEL_ID"],
            api_key=os.environ["LLM_API_KEY"],
            client_args={
                "base_url": os.environ["LLM_BASE_URL"],
                "timeout": float(os.environ.get("LLM_TIMEOUT", "60")),
            },
        )

    async def create_player(self, role: str, character: str) -> ReActAgent:
        """创建具有三国背景的玩家 Agent（角色建模层）。"""
        name = get_chinese_name(character)
        self.roles[name] = role

        agent = ReActAgent(
            name=name,
            sys_prompt=ChinesePrompts.get_role_prompt(role, character),
            model=self._create_model(),
            formatter=OpenAIMultiAgentFormatter(),
        )

        # 角色身份确认：点对点注入，不进入公共频道
        await agent.observe(
            await self.moderator.announce(
                f"【{name}】你在这场三国狼人杀中扮演{GameRoles.get_role_desc(role)}，"
                f"你的角色是{character}。{GameRoles.get_role_ability(role)}"
            )
        )

        self.players[name] = agent
        return agent

    async def setup_game(self, player_count: int = 6) -> None:
        """设置游戏：随机分配角色并创建所有玩家。"""
        print("🎮 开始设置三国狼人杀游戏...")

        roles = GameRoles.get_standard_setup(player_count)
        characters = random.sample(
            ["刘备", "关羽", "张飞", "诸葛亮", "赵云", "曹操", "司马懿", "周瑜", "孙权"],
            player_count,
        )

        for role, character in zip(roles, characters):
            agent = await self.create_player(role, character)
            self.alive_players.append(agent)
            if role == "狼人":
                self.werewolves.append(agent)
            elif role == "预言家":
                self.seer.append(agent)
            elif role == "女巫":
                self.witch.append(agent)
            elif role == "猎人":
                self.hunter.append(agent)
            else:
                self.villagers.append(agent)

        await self.moderator.announce(
            f"三国狼人杀游戏开始！参与者：{format_player_list(self.alive_players)}"
        )
        print(f"✅ 游戏设置完成，共{len(self.alive_players)}名玩家")

    async def werewolf_phase(self, round_num: int) -> Optional[str]:
        """狼人阶段：MsgHub 私密频道讨论 + 投票击杀。"""
        if not self.werewolves:
            return None

        await self.moderator.announce("🐺 狼人请睁眼，选择今晚要击杀的目标...")

        # MsgHub 建立狼人专属私密通信频道
        async with MsgHub(
            self.werewolves,
            enable_auto_broadcast=True,
            announcement=await self.moderator.announce(
                f"狼人们，请讨论今晚的击杀目标。存活玩家：{format_player_list(self.alive_players)}"
            ),
        ) as werewolves_hub:
            # 讨论阶段：每轮每只狼人发言一次，自动广播给狼队友
            for _ in range(MAX_DISCUSSION_ROUND):
                for wolf in self.werewolves:
                    await wolf(structured_model=DiscussionModelCN)

            # 投票阶段：关闭自动广播，并行收集击杀决策
            werewolves_hub.set_auto_broadcast(False)
            kill_votes_msgs = await fanout_pipeline(
                self.werewolves,
                msg=await self.moderator.announce("请选择击杀目标"),
                structured_model=WerewolfKillModelCN,
                enable_gather=False,
            )

            # 解析投票，无效则随机选一个非狼人目标（教程容错逻辑）
            votes: Dict[str, Optional[str]] = {}
            for i, vote_msg in enumerate(kill_votes_msgs):
                if vote_msg is not None and getattr(vote_msg, "metadata", None) is not None:
                    votes[self.werewolves[i].name] = vote_msg.metadata.get("target")
                else:
                    print(f"⚠️ {self.werewolves[i].name} 的击杀投票无效,随机选择目标")
                    targets = [
                        p.name for p in self.alive_players
                        if p.name not in {w.name for w in self.werewolves}
                    ]
                    votes[self.werewolves[i].name] = (
                        random.choice(targets) if targets else None
                    )

            killed_player, _ = majority_vote_cn(votes)
            return killed_player

    async def seer_phase(self) -> None:
        """预言家阶段：查验一名玩家的真实身份。"""
        if not self.seer:
            return

        seer_agent = self.seer[0]
        await self.moderator.announce("🔮 预言家请睁眼，选择要查验的玩家...")

        check_result = await seer_agent(
            structured_model=get_seer_model_cn(self.alive_players)
        )
        if check_result is None or getattr(check_result, "metadata", None) is None:
            print("⚠️ 预言家查验失败,跳过此阶段")
            return

        target_name = check_result.metadata.get("target")
        if not target_name:
            print("⚠️ 预言家未选择查验目标,跳过此阶段")
            return

        target_role = self.roles.get(target_name, "村民")
        result_msg = f"查验结果：{target_name}是{'狼人' if target_role == '狼人' else '好人'}"
        # 查验结果只让预言家本人知道（点对点，不进公共频道）
        await seer_agent.observe(await self.moderator.announce(result_msg))

    async def witch_phase(self, killed_player: Optional[str]):
        """女巫阶段：决定是否用解药救人或用毒药杀人。"""
        if not self.witch:
            return killed_player, None

        witch_agent = self.witch[0]
        await self.moderator.announce("🧙‍♀️ 女巫请睁眼...")

        # 告知女巫今晚的击杀信息（点对点）
        death_info = (
            f"今晚{killed_player}被狼人击杀" if killed_player else "今晚平安无事"
        )
        await witch_agent.observe(await self.moderator.announce(death_info))

        witch_action = await witch_agent(structured_model=WitchActionModelCN)

        saved_player = None
        poisoned_player = None
        if witch_action is None or getattr(witch_action, "metadata", None) is None:
            print("⚠️ 女巫行动失败,视为不使用技能")
        else:
            if witch_action.metadata.get("use_antidote") and self.witch_has_antidote:
                if killed_player:
                    saved_player = killed_player
                    self.witch_has_antidote = False
                    await witch_agent.observe(
                        await self.moderator.announce(f"你使用解药救了{killed_player}")
                    )

            if witch_action.metadata.get("use_poison") and self.witch_has_poison:
                poisoned_player = witch_action.metadata.get("target_name")
                if poisoned_player:
                    self.witch_has_poison = False
                    await witch_agent.observe(
                        await self.moderator.announce(
                            f"你使用毒药毒杀了{poisoned_player}"
                        )
                    )

        # 解药生效则被击杀者不死
        final_killed = None if saved_player else killed_player
        return final_killed, poisoned_player

    async def hunter_phase(self, shot_by_hunter: Optional[str]) -> Optional[str]:
        """猎人阶段：猎人被投票出局时可以开枪带走一名玩家。"""
        if not self.hunter:
            return None

        hunter_agent = self.hunter[0]
        if hunter_agent.name == shot_by_hunter:
            await self.moderator.announce("🏹 猎人发动技能，可以带走一名玩家...")

            hunter_action = await hunter_agent(
                structured_model=get_hunter_model_cn(self.alive_players)
            )
            if hunter_action is None or getattr(hunter_action, "metadata", None) is None:
                print("⚠️ 猎人技能使用失败,视为放弃开枪")
                return None

            if hunter_action.metadata.get("shoot"):
                target = hunter_action.metadata.get("target")
                if target:
                    await self.moderator.announce(
                        f"猎人{hunter_agent.name}开枪带走了{target}"
                    )
                    return target
                print("⚠️ 猎人选择开枪但未指定目标,视为放弃")
        return None

    def update_alive_players(self, dead_players: List[Optional[str]]) -> None:
        """更新存活玩家列表和各阵营列表。"""
        for dead_name in dead_players:
            if not dead_name:
                continue
            self.alive_players = [p for p in self.alive_players if p.name != dead_name]
            self.werewolves = [p for p in self.werewolves if p.name != dead_name]
            self.villagers = [p for p in self.villagers if p.name != dead_name]
            self.seer = [p for p in self.seer if p.name != dead_name]
            self.witch = [p for p in self.witch if p.name != dead_name]
            self.hunter = [p for p in self.hunter if p.name != dead_name]

    async def day_phase(self, round_num: int) -> Optional[str]:
        """白天阶段：全员讨论 + 全员投票。"""
        await self.moderator.day_announcement(round_num)

        # MsgHub 建立全员公共频道
        async with MsgHub(
            self.alive_players,
            enable_auto_broadcast=True,
            announcement=await self.moderator.announce(
                f"现在开始自由讨论。存活玩家：{format_player_list(self.alive_players)}"
            ),
        ) as all_hub:
            # 每人依次发言一轮，上一人的发言自动广播给所有人
            await sequential_pipeline(self.alive_players)

            # 投票阶段：关闭广播，并行收票（模拟同时亮票）
            all_hub.set_auto_broadcast(False)
            vote_msgs = await fanout_pipeline(
                self.alive_players,
                msg=await self.moderator.announce("请投票选择要淘汰的玩家"),
                structured_model=get_vote_model_cn(self.alive_players),
                enable_gather=False,
            )

            votes: Dict[str, Optional[str]] = {}
            for i, vote_msg in enumerate(vote_msgs):
                if vote_msg is not None and getattr(vote_msg, "metadata", None) is not None:
                    votes[self.alive_players[i].name] = vote_msg.metadata.get("vote")
                else:
                    print(f"⚠️ {self.alive_players[i].name} 的投票无效,视为弃票")
                    votes[self.alive_players[i].name] = None

            voted_out, vote_count = majority_vote_cn(votes)
            await self.moderator.vote_result_announcement(voted_out, vote_count)
            return voted_out

    async def run_game(self) -> None:
        """游戏主循环。"""
        try:
            await self.setup_game()

            for round_num in range(1, MAX_GAME_ROUND + 1):
                print(f"\n🌙 === 第{round_num}轮游戏开始 ===")
                await self.moderator.night_announcement(round_num)

                # 夜晚：击杀 -> 查验 -> 女巫
                killed_player = await self.werewolf_phase(round_num)
                await self.seer_phase()
                final_killed, poisoned_player = await self.witch_phase(killed_player)

                night_deaths = [p for p in (final_killed, poisoned_player) if p]
                self.update_alive_players(night_deaths)
                await self.moderator.death_announcement(night_deaths)

                winner = check_winning_cn(self.alive_players, self.roles)
                if winner:
                    await self.moderator.game_over_announcement(winner)
                    return

                # 白天：讨论 -> 投票 -> 猎人
                voted_out = await self.day_phase(round_num)
                hunter_shot = await self.hunter_phase(voted_out)

                day_deaths = [p for p in (voted_out, hunter_shot) if p]
                self.update_alive_players(day_deaths)

                winner = check_winning_cn(self.alive_players, self.roles)
                if winner:
                    await self.moderator.game_over_announcement(winner)
                    return

                print(
                    f"第{round_num}轮结束，存活玩家：{format_player_list(self.alive_players)}"
                )

        except Exception as e:
            print(f"❌ 游戏运行出错：{e}")
            import traceback
            traceback.print_exc()


async def main() -> None:
    """主函数：加载 .env -> 检查配置 -> 启动游戏。"""
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")

    required = ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL_ID")
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"❌ 缺少环境变量：{missing}，请检查仓库根目录 .env")
        return

    print("🎮 欢迎来到三国狼人杀！")
    game = ThreeKingdomsWerewolfGame()
    await game.run_game()


if __name__ == "__main__":
    asyncio.run(main())
