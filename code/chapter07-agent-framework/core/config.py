# -*- coding: utf-8 -*-
"""配置管理（7.3.2）—— 手写实现。

教程参考：docs/chapter7/第七章.md 7.3.2 节

设计要点：
- 配置项按逻辑分组（LLM 配置 / 系统配置）
- 每项都有默认值，保证零配置可用
- from_env() 支持环境变量覆盖默认值（部署友好）
"""

import os
from typing import Optional

from pydantic import BaseModel


class Config(BaseModel):
    """HelloAgents 配置类"""

    # TODO 1: LLM 配置
    # - default_model: str = "gpt-3.5-turbo"
    # - default_provider: str = "openai"
    # - temperature: float = 0.7
    # - max_tokens: Optional[int] = None
    ...

    # TODO 2: 系统配置
    # - debug: bool = False
    # - log_level: str = "INFO"
    ...

    # TODO 3: 其他配置
    # - max_history_length: int = 100
    ...

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置。

        TODO:
        - DEBUG -> debug（"true"/"false" 转 bool）
        - LOG_LEVEL -> log_level
        - TEMPERATURE -> temperature
        - MAX_TOKENS -> max_tokens（存在才设置）
        """
        raise NotImplementedError

    def to_dict(self):
        """转换为字典"""
        # TODO: return self.dict() 或 self.model_dump()
        raise NotImplementedError
