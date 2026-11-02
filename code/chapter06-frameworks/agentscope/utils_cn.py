# -*- coding: utf-8 -*-
"""三国狼人杀通用工具函数与游戏主持人。

对应教程：hello-agents/code/chapter6/AgentScopeDemo/utils_cn.py
"""

import random
from collections import Counter
from typing import Any, Dict, List, Optional

from agentscope.agent import AgentBase
from agentscope.message import Msg

# 游戏常量（与教程一致；调试时可临时调小省 token）
MAX_GAME_ROUND = 10
MAX_DISCUSSION_ROUND = 3

CHINESE_NAMES = [
    "刘备", "关羽", "张飞", "诸葛亮", "赵云",
    "曹操", "司马懿", "典韦", "许褚", "夏侯惇",
    "孙权", "周瑜", "陆逊", "甘宁", "太史慈",
    "吕布", "貂蝉", "董卓", "袁绍", "袁术",
]


def get_chinese_name(character: Optional[str] = None) -> str:
    """获取中文角色名：指定人物在池中则直接用，否则随机选择。"""
    if character and character in CHINESE_NAMES:
        return character
    return random.choice(CHINESE_NAMES)


def format_player_list(players: List[AgentBase], show_roles: bool = False) -> str:
    """格式化玩家列表为中文显示。"""
    if not players:
        return "无玩家"
    if show_roles:
        return "、".join(f"{p.name}({getattr(p, 'role', '未知')})" for p in players)
    return "、".join(p.name for p in players)


def majority_vote_cn(votes: Dict[str, Optional[str]]) -> tuple[str, int]:
    """中文版多数投票统计。无效票（None）先过滤，避免"弃票"当选。"""
    valid_votes = {voter: target for voter, target in votes.items() if target}
    if not valid_votes:
        return "无人", 0
    vote_counts = Counter(valid_votes.values())
    most_voted, count = vote_counts.most_common(1)[0]
    return most_voted, count


def check_winning_cn(
    alive_players: List[AgentBase], roles: Dict[str, str]
) -> Optional[str]:
    """检查中文版游戏胜利条件。

    Returns:
        胜利描述；游戏未结束返回 None。
    """
    alive_roles = [roles.get(p.name, "村民") for p in alive_players]
    werewolf_count = alive_roles.count("狼人")
    villager_count = len(alive_roles) - werewolf_count

    if werewolf_count == 0:
        return "好人阵营胜利！所有狼人已被淘汰！"
    elif werewolf_count >= villager_count:
        return "狼人阵营胜利！狼人数量已达到或超过好人！"
    return None


class GameModerator(AgentBase):
    """中文版游戏主持人：不调用大模型，只发布公告。"""

    def __init__(self) -> None:
        super().__init__()
        self.name = "游戏主持人"
        self.game_log: List[str] = []

    async def observe(self, msg) -> None:
        """主持人只记录消息，不需要维护记忆。"""

    async def reply(self, *args: Any, **kwargs: Any) -> Msg:
        raise NotImplementedError("主持人不参与模型回复")

    async def announce(self, content: str) -> Msg:
        """发布游戏公告并返回消息对象。"""
        msg = Msg(name=self.name, content=f"📢 {content}", role="system")
        self.game_log.append(content)
        await self.print(msg)
        return msg

    async def night_announcement(self, round_num: int) -> Msg:
        """夜晚阶段公告"""
        return await self.announce(f"🌙 第{round_num}夜降临，天黑请闭眼...")

    async def day_announcement(self, round_num: int) -> Msg:
        """白天阶段公告"""
        return await self.announce(f"☀️ 第{round_num}天天亮了，请大家睁眼...")

    async def death_announcement(self, dead_players: List[Optional[str]]) -> Msg:
        """死亡公告"""
        dead = [name for name in dead_players if name]
        if not dead:
            content = "昨夜平安无事，无人死亡。"
        else:
            content = f"昨夜，{'、'.join(dead)}不幸遇害。"
        return await self.announce(content)

    async def vote_result_announcement(self, voted_out: str, vote_count: int) -> Msg:
        """投票结果公告"""
        return await self.announce(f"投票结果：{voted_out}以{vote_count}票被淘汰出局。")

    async def game_over_announcement(self, winner: str) -> Msg:
        """游戏结束公告"""
        return await self.announce(f"🎉 游戏结束！{winner}")
