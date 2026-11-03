# -*- coding: utf-8 -*-
"""Agent 抽象基类（7.3.3）—— 手写实现。

教程参考：docs/chapter7/第七章.md 7.3.3 节

设计要点：
- 继承 ABC，run() 用 @abstractmethod 强制子类实现
- 构造函数定义 Agent 的核心依赖：name / llm / system_prompt / config
- 提供统一的历史记录管理（与 Message 协同）
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .config import Config
from .llm import HelloAgentsLLM
from .message import Message


class Agent(ABC):
    """Agent 抽象基类：所有具体智能体的统一接口。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> None:
        # TODO 1: 保存 name / llm / system_prompt
        # TODO 2: self.config = config or Config()
        # TODO 3: self._history: List[Message] = []
        ...

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行 Agent —— 子类必须实现。"""
        ...

    def add_message(self, message: Message) -> None:
        """添加消息到历史记录。"""
        # TODO: self._history.append(message)
        raise NotImplementedError

    def clear_history(self) -> None:
        """清空历史记录。"""
        # TODO: self._history.clear()
        raise NotImplementedError

    def get_history(self) -> List[Message]:
        """获取历史记录（返回副本，防止外部修改内部状态）。"""
        # TODO: return self._history.copy()
        raise NotImplementedError

    def __str__(self) -> str:
        # TODO: return f"Agent(name={self.name}, provider={self.llm.provider})"
        raise NotImplementedError
