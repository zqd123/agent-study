# -*- coding: utf-8 -*-
"""FunctionCallAgent（7.4.5）—— 基于原生 Function Calling 的 Agent，手写实现。

教程参考：docs/chapter7/第七章.md 7.4.5 节

与 ReActAgent 的区别：
- ReAct：靠提示词约定 "tool[参数]" 文本格式，自己解析
- FunctionCall：用 OpenAI 原生 tools 参数 + tool_calls 响应，API 层面约束
"""

from typing import Any, Dict, List, Optional

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM
from tools.base import ToolRegistry


class FunctionCallAgent(Agent):
    """Function Calling Agent：使用 OpenAI 原生函数调用。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
    ) -> None:
        super().__init__(name, llm, system_prompt, config)
        # TODO 1: 保存 tool_registry / max_steps
        ...

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """把注册表中的工具转换为 OpenAI tools 参数格式。

        TODO: 遍历 tool_registry.get_all_tools()，
        构造 [{"type": "function", "function": {"name":..., "description":..., "parameters":...}}]
        """
        raise NotImplementedError

    def run(self, input_text: str, **kwargs) -> str:
        """Function Call 主循环。

        TODO:
        1. 组装 messages（system + user）
        2. 循环调用 llm（带 tools 参数）：
           - 响应带 tool_calls：执行工具，把结果以 {"role": "tool", ...} 追加，继续循环
           - 响应无 tool_calls：返回最终 content
        3. 超过 max_steps 返回兜底话术
        """
        raise NotImplementedError
