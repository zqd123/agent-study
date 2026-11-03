# -*- coding: utf-8 -*-
"""ReActAgent（7.4.2）—— 推理与行动范式，手写实现。

教程参考：docs/chapter7/第七章.md 7.4.2 节
          hello-agents/code/chapter7/my_react_agent.py

核心循环（对比第四章手写版，重点体会框架化差异）：
    while 步数 < max_steps:
        1. 构建提示词（工具描述 + 任务 + 执行历史）
        2. 调用 LLM
        3. 解析输出 -> (thought, action)
        4. Finish[...] -> 返回最终答案
        5. tool[...] -> 执行工具，Observation 追加进历史
"""

import re
from typing import List, Optional, Tuple

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM
from core.message import Message
from tools.base import ToolRegistry

# TODO 1: 定义 ReAct 提示词模板（参考教程 my_react_agent.py 的 MY_REACT_PROMPT）
# 占位符：{tools} {question} {history}
MY_REACT_PROMPT = None  # 替换为完整模板字符串


class ReActAgent(Agent):
    """ReAct Agent：Thought -> Action -> Observation 循环。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
        custom_prompt: Optional[str] = None,
    ) -> None:
        super().__init__(name, llm, system_prompt, config)
        # TODO 2: 保存 tool_registry / max_steps / current_history / prompt_template
        ...

    def _parse_output(self, response_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析 LLM 输出为 (thought, action)。

        TODO: 用正则提取 Thought: 和 Action: 两部分
        """
        raise NotImplementedError

    def _parse_action(self, action: str) -> Tuple[str, str]:
        """解析 action 为 (tool_name, tool_input)。

        TODO: 匹配 "tool_name[tool_input]" 格式
        """
        raise NotImplementedError

    def _parse_action_input(self, action: str) -> str:
        """提取 Finish[...] 或 tool[...] 中的内容。

        TODO: 提取方括号内的文本
        """
        raise NotImplementedError

    def run(self, input_text: str, **kwargs) -> str:
        """ReAct 主循环。

        TODO（按教程 my_react_agent.py 的 run 实现）:
        1. self.current_history = []
        2. while current_step < self.max_steps:
           - 构建提示词（tools_desc + question + history）
           - llm.invoke(messages)
           - _parse_output -> thought, action
           - action 以 "Finish" 开头 -> 写入历史并返回最终答案
           - 否则解析工具名和参数 -> tool_registry.execute_tool()
             -> Observation 追加进 current_history
        3. 超过最大步数返回兜底话术
        """
        raise NotImplementedError
