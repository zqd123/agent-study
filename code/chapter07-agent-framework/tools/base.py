"""工具基类与注册机制 —— 对应教程 7.5.1

按教程实现三个部分：
1. ToolParameter：工具参数定义（pydantic BaseModel）
2. Tool：工具抽象基类（ABC），子类实现 run() 和 get_parameters()
3. ToolRegistry：注册表，管理 Tool 对象和普通函数两类工具

提示词中用到的接口：
- registry.get_tools_description() -> str   给 Agent 提示词用
- registry.execute_tool(name, input_data) -> str   ReAct 循环里执行工具
- registry.list_tools() -> list
- registry.register_function(name, description, func)
- registry.register_tool(tool)
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

from pydantic import BaseModel


class ToolParameter(BaseModel):
    """工具参数定义

    TODO(7.5.1): 按教程补全字段
      - name: str          参数名
      - type: str          参数类型，如 "string"
      - description: str   参数描述
      - required: bool = True
      - default: Any = None
    """
    pass


class Tool(ABC):
    """工具基类

    TODO(7.5.1):
      - __init__(self, name: str, description: str) 保存 name / description
      - @abstractmethod run(self, parameters: Dict[str, Any]) -> str
      - @abstractmethod get_parameters(self) -> List[ToolParameter]
    """
    pass


class ToolRegistry:
    """HelloAgents 工具注册表

    TODO(7.5.1): 内部维护两个字典
      - self._tools: dict[str, Tool]            Tool 对象注册
      - self._functions: dict[str, dict]        函数工具注册，值含 description 和 func

    需实现的方法：
      - register_tool(tool: Tool)               重名时打印覆盖警告
      - register_function(name, description, func)   func 签名 (str) -> str
      - get_tools_description() -> str          格式 "- {name}: {description}"，每行一个
      - execute_tool(tool_name: str, input_data: str) -> str
          先查 _tools（调用 tool.run），再查 _functions（调用 func(input_data)），
          都没有时返回错误提示字符串（不要抛异常，让 Agent 循环能继续）
      - list_tools() -> list                    返回所有工具名
    """

    def __init__(self):
        # TODO: 初始化 self._tools 和 self._functions
        raise NotImplementedError("按教程 7.5.1 实现 ToolRegistry")
