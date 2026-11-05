# -*- coding: utf-8 -*-
"""MySimpleAgent（7.4.1）—— 严格按教程实现。

教程路径是继承 pip 包的 SimpleAgent 重写增强；本仓库走深度式路径，
继承手写 core/agent.py 的 Agent 基类，但功能与教程 7.4.1 完全对齐：
- 基础对话 + 历史管理
- 可选工具调用：[TOOL_CALL:工具名:参数] 格式，_run_with_tools 多轮迭代
- enable_tool_calling 开关
- stream_run 流式响应
- add_tool / has_tools / remove_tool / list_tools 便利方法
"""
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM
from core.message import Message

try:
    from tools.base import ToolRegistry
except ImportError:
    ToolRegistry = None


class MySimpleAgent(Agent):
    """重写的简单对话 Agent：基础对话 + 可选工具调用。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional["ToolRegistry"] = None,
        enable_tool_calling: bool = True,
    ) -> None:
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        state = "启用" if self.enable_tool_calling else "禁用"
        print(f"✅ {name} 初始化完成，工具调用: {state}")

    # TODO 1: run(input_text, max_tool_iterations=3, **kwargs) -> str
    #   按教程实现：
    #   1. print(f"🤖 {self.name} 正在处理: {input_text}")
    # 2. messages 构建：
    #    - system 消息用 self._get_enhanced_system_prompt() 的返回值
    #    - for msg in self._history: {"role": msg.role, "content": msg.content}
    #    - {"role": "user", "content": input_text}
    # 3. 未启用工具调用 → invoke + 存历史 + return
    # 4. 启用 → return self._run_with_tools(messages, input_text, max_tool_iterations, **kwargs)

    # TODO 2: _get_enhanced_system_prompt() -> str
    #   基础提示词 = self.system_prompt or "你是一个有用的AI助手。"
    #   有工具时追加：
    #     "## 可用工具" 段（registry.get_tools_description()）
    #     "## 工具调用格式" 段：[TOOL_CALL:{tool_name}:{parameters}]，含示例
    #   注意教程的判断：tools_description == "暂无可用工具" 时返回基础提示词

    # TODO 3: _run_with_tools(messages, input_text, max_tool_iterations, **kwargs)
    #   教程逻辑（多轮迭代）：
    #   for i in range(max_tool_iterations):
    #       response = self.llm.invoke(messages)
    #       匹配 r"\[TOOL_CALL:(\w+):(.+?)\]"，未匹配 → 存历史 + return response
    #       匹配到 → execute_tool(name, input) → 把结果以 "TOOL_RESULT:..." 拼回 messages
    #                继续下一轮让模型基于结果回答
    #   超过次数 → 最后一次 response 存历史并返回

    # TODO 4: _parse_tool_parameters(tool_name, parameters) -> Dict[str, Any]
    #   教程参数解析：key=value 多对（逗号分隔）/ 单参数 / 无 = 时按工具名智能推断

    # TODO 5: stream_run(input_text, **kwargs) -> Iterator[str]
    #   流式版：self.llm.think(messages) 逐段 yield，累计 full_response 后存历史
    #   （教程用 pip 包的 stream_invoke，我们手写 llm 的对应方法是 think）

    # TODO 6: 便利方法 add_tool(tool) / has_tools() / remove_tool(name) / list_tools()
    #   注意 add_tool 在 registry 不存在时要现场创建 ToolRegistry 并启用开关
