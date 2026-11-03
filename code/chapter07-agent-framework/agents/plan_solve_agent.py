# -*- coding: utf-8 -*-
"""PlanAndSolveAgent（7.4.4）—— 计划与执行范式，手写实现。

教程参考：docs/chapter7/第七章.md 7.4.4 节

核心逻辑：
1. 规划器：把复杂问题拆解为有序步骤
2. 执行器：逐步执行每个步骤（携带历史步骤结果）
3. 汇总：输出最终答案
"""

from typing import Optional

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM

# TODO 1: 定义规划器和执行器提示词模板（参考教程 7.4.4 节）
PLANNER_PROMPT = None
EXECUTOR_PROMPT = None


class PlanAndSolveAgent(Agent):
    """Plan-and-Solve Agent：先规划后执行。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        planner_prompt: Optional[str] = None,
        executor_prompt: Optional[str] = None,
    ) -> None:
        super().__init__(name, llm, system_prompt, config)
        # TODO 2: 保存两个提示词模板
        ...

    def _create_plan(self, question: str) -> str:
        """生成完整计划（有序步骤列表）。"""
        # TODO: 用 PLANNER_PROMPT 调用 llm
        raise NotImplementedError

    def _execute_step(self, question: str, plan: str, history: str, step: str) -> str:
        """执行单个步骤。"""
        # TODO: 用 EXECUTOR_PROMPT 调用 llm
        raise NotImplementedError

    def run(self, input_text: str, **kwargs) -> str:
        """Plan-and-Solve 主循环。

        TODO:
        1. plan = self._create_plan(input_text)
        2. 解析计划中的每个步骤（按行拆分，带编号的行）
        3. 逐步执行，把每步结果追加到历史
        4. 最后一步的结果作为最终答案返回
        """
        raise NotImplementedError
