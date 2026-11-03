# -*- coding: utf-8 -*-
"""ReflectionAgent（7.4.3）—— 反思改进范式，手写实现。

教程参考：docs/chapter7/第七章.md 7.4.3 节

核心逻辑：
1. 生成器：根据原始任务生成初始回答
2. 反思器：对当前回答给出反馈意见
3. 改进器：结合原始任务 + 上一轮回答 + 反馈，生成改进回答
4. 循环 max_iterations 轮（或达到满意为止）
"""

from typing import Optional

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM

# TODO 1: 定义三个提示词模板（生成器/反思器/改进器）
# 可参考教程 7.4.3 节的提示词，也支持自定义传入
GENERATOR_PROMPT = None
REFLECTION_PROMPT = None
IMPROVER_PROMPT = None


class ReflectionAgent(Agent):
    """反思 Agent：生成 -> 反思 -> 改进 循环。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_iterations: int = 3,
        generator_prompt: Optional[str] = None,
        reflection_prompt: Optional[str] = None,
        improver_prompt: Optional[str] = None,
    ) -> None:
        super().__init__(name, llm, system_prompt, config)
        # TODO 2: 保存 max_iterations 和三个提示词模板（自定义优先，默认兜底）
        ...

    def _generate(self, task: str) -> str:
        """生成初始回答。"""
        # TODO: llm.invoke([{"role": "user", "content": GENERATOR_PROMPT.format(task=task)}])
        raise NotImplementedError

    def _reflect(self, task: str, answer: str) -> str:
        """对当前回答给出反馈意见。"""
        # TODO: 用 REFLECTION_PROMPT 组装消息并调用 llm
        raise NotImplementedError

    def _improve(self, task: str, answer: str, feedback: str) -> str:
        """结合反馈改进回答。"""
        # TODO: 用 IMPROVER_PROMPT 组装消息并调用 llm
        raise NotImplementedError

    def run(self, input_text: str, **kwargs) -> str:
        """反思主循环。

        TODO:
        1. answer = self._generate(input_text)
        2. for _ in range(self.max_iterations):
           - feedback = self._reflect(input_text, answer)
           - answer = self._improve(input_text, answer, feedback)
        3. 返回最终 answer
        """
        raise NotImplementedError
