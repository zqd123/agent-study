# -*- coding: utf-8 -*-
"""LLM 统一接口（7.2）—— 手写实现（基于 OpenAI 兼容 API）。

教程参考：docs/chapter7/第七章.md 7.2 节

说明：
- 教程用 pip 包的 HelloAgentsLLM 做扩展（支持 modelscope/zhipu/ollama 等）
- 本文件是手写简化版：只支持 OpenAI 兼容接口，复用根目录 .env
- 体验阶段可直接用 pip 包的 HelloAgentsLLM，两套可互换
"""

import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[2]


class HelloAgentsLLM:
    """统一 LLM 客户端（简化版）。

    自动检测逻辑（简化）：
    1. 显式传入 api_key/base_url 优先
    2. 否则读取环境变量 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_ID
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 60,
        **kwargs: Any,
    ) -> None:
        # TODO 1: 解析配置（参数优先，环境变量兜底）
        # - self.api_key = api_key or os.getenv("LLM_API_KEY")
        # - self.base_url = base_url or os.getenv("LLM_BASE_URL")
        # - self.model = model or os.getenv("LLM_MODEL_ID")
        # 校验 api_key 必须存在，否则抛 ValueError
        ...

        # TODO 2: 创建 OpenAI 客户端
        # self._client = OpenAI(api_key=..., base_url=..., timeout=timeout)
        ...

        # TODO 3: 保存 temperature / max_tokens / provider 标识
        ...

    def invoke(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """同步调用，返回完整文本。

        TODO:
        1. self._client.chat.completions.create(model=..., messages=..., ...)
        2. 返回 response.choices[0].message.content
        """
        raise NotImplementedError

    def think(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """流式调用，逐段 yield 文本。

        TODO:
        1. create(..., stream=True)
        2. for chunk in response: yield chunk.choices[0].delta.content
        （注意跳过 content 为 None 的 chunk）
        """
        raise NotImplementedError

    def think_raw(self, messages: List[Dict[str, str]], **kwargs: Any):
        """返回原始流式响应对象（供需要更细控制的场景）。"""
        # TODO: return self._client.chat.completions.create(..., stream=True, ...)
        raise NotImplementedError
