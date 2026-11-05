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

# 定义消息角色的类型，限制其取值
MessageRole = Literal["user","assistant","system","tool"]

# 定义了框架内统一的消息格式，确保了智能体与模型之间信息传递的标准化。
class Message(BaseModel):
    """消息类"""

    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, content: str, role: MessageRole, **kwargs):
        # TODO 3: 调用 super().__init__，填充 timestamp 和 metadata 默认值
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get('timestamp',datetime.now()),
            metadata=kwargs.get('metadata',{})
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（OpenAI API 格式）。
        """
        return {
            "role":self.role,
            "content":self.content,
        }

    def __str__(self) -> str:
       return f"[{self.role}] {self.content}"
