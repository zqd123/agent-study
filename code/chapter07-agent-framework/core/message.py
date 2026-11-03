# -*- coding: utf-8 -*-
"""消息系统（7.3.1）—— 手写实现。

教程参考：docs/chapter7/第七章.md 7.3.1 节

设计要点：
- MessageRole 用 Literal 限定为 "user"/"assistant"/"system"/"tool"，对应 OpenAI API 规范
- "对内丰富，对外兼容"：内部带 timestamp/metadata，to_dict() 输出 OpenAI 兼容格式
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

# TODO 1: 定义消息角色类型（Literal）
MessageRole = None  # 替换为 Literal[...]


class Message(BaseModel):
    """消息类"""

    # TODO 2: 定义字段
    # - content: str
    # - role: MessageRole
    # - timestamp: datetime（默认当前时间）
    # - metadata: Optional[Dict[str, Any]]（默认空字典）
    ...

    def __init__(self, content: str, role: MessageRole, **kwargs):
        # TODO 3: 调用 super().__init__，填充 timestamp 和 metadata 默认值
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（OpenAI API 格式）。

        TODO: 只返回 {"role": ..., "content": ...}
        """
        raise NotImplementedError

    def __str__(self) -> str:
        # TODO: 返回 f"[{self.role}] {self.content}"
        raise NotImplementedError
