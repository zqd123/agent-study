# -*- coding: utf-8 -*-
"""三国狼人杀的结构化输出模型。

对应教程：hello-agents/code/chapter6/AgentScopeDemo/structured_output_cn.py
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from agentscope.agent import AgentBase


class DiscussionModelCN(BaseModel):
    """中文版讨论输出格式"""

    reach_agreement: bool = Field(description="是否已达成一致意见")
    confidence_level: int = Field(description="对当前推理的信心程度(1-10)", ge=1, le=10)
    key_evidence: Optional[str] = Field(
        description="支持你观点的关键证据", default=None
    )


def get_vote_model_cn(agents: list[AgentBase]) -> type[BaseModel]:
    """动态生成投票模型：只能投给当前存活的玩家。"""
    names = tuple(agent.name for agent in agents)

    class VoteModelCN(BaseModel):
        """中文版投票输出格式"""

        vote: Literal[names] = Field(description="你要投票淘汰的玩家姓名")
        reason: str = Field(description="投票理由，简要说明为什么选择此人")
        suspicion_level: int = Field(description="对被投票者的怀疑程度(1-10)", ge=1, le=10)

    return VoteModelCN


class WitchActionModelCN(BaseModel):
    """中文版女巫行动模型"""

    use_antidote: bool = Field(description="是否使用解药救人", default=False)
    use_poison: bool = Field(description="是否使用毒药杀人", default=False)
    target_name: Optional[str] = Field(
        description="目标玩家姓名（毒杀的对象）", default=None
    )
    action_reason: Optional[str] = Field(description="行动理由", default=None)


def get_seer_model_cn(agents: list[AgentBase]) -> type[BaseModel]:
    """动态生成预言家查验模型：只能查验存活玩家。"""
    names = tuple(agent.name for agent in agents)

    class SeerModelCN(BaseModel):
        """中文版预言家查验格式"""

        target: Literal[names] = Field(description="要查验的玩家姓名")
        check_reason: str = Field(description="查验此人的原因")
        priority_level: int = Field(description="查验优先级(1-10)", ge=1, le=10)

    return SeerModelCN


def get_hunter_model_cn(agents: list[AgentBase]) -> type[BaseModel]:
    """动态生成猎人开枪模型：只能射杀存活玩家。"""
    names = tuple(agent.name for agent in agents)

    class HunterModelCN(BaseModel):
        """中文版猎人开枪格式"""

        shoot: bool = Field(description="是否使用开枪技能")
        target: Optional[Literal[names]] = Field(
            description="开枪目标玩家姓名", default=None
        )
        shoot_reason: Optional[str] = Field(description="开枪理由", default=None)

    return HunterModelCN


class WerewolfKillModelCN(BaseModel):
    """中文版狼人击杀模型"""

    target: str = Field(description="要击杀的玩家姓名")
    kill_strategy: str = Field(description="击杀策略说明")
    team_coordination: Optional[str] = Field(
        description="与狼队友的配合计划", default=None
    )


class GameAnalysisModelCN(BaseModel):
    """中文版游戏分析模型（教程扩展模型，主流程暂未使用）"""

    suspected_werewolves: List[str] = Field(
        default_factory=list, description="怀疑的狼人名单"
    )
    trusted_players: List[str] = Field(
        default_factory=list, description="信任的玩家名单"
    )
    key_clues: List[str] = Field(default_factory=list, description="关键线索列表")
    next_strategy: str = Field(description="下一步策略")
