# -*- coding: utf-8 -*-
"""7.2.3 自动检测机制 —— 手写 HelloAgentsLLM（教程 7.2 升级版）。

对应教程 7.2.1 多提供商 + 7.2.3 自动检测。

两个核心辅助方法：
- _auto_detect_provider(api_key, base_url) -> str
    1. 特定环境变量（MODELSCOPE_API_KEY / OPENAI_API_KEY / ZHIPU_API_KEY）
    2. base_url 特征（域名/端口）
    3. 密钥格式（ms- 前缀）
    4. 兜底 "auto"
- _resolve_credentials(api_key, base_url) -> tuple[str, str]
    按 provider 解析凭证与默认地址。
"""
import os
from typing import Any, Dict, Generator, List, Optional, Tuple

from openai import OpenAI


class HelloAgentsLLM:
    """统一 LLM 客户端（支持多提供商 + 自动检测）。"""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = "auto",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 60,
        **kwargs: Any,
    ) -> None:
        # TODO 1: 解析 provider（显式传入优先，否则自动检测）
        if provider and provider != "auto":
            self.provider = provider
        else:
            self.provider = self._auto_detect_provider(api_key, base_url)

        # TODO 2: 解析凭证
        self.api_key, self.base_url = self._resolve_credentials(api_key, base_url)

        # TODO 3: 校验（本地部署无需密钥）
        if self.provider not in ("ollama", "vllm", "local") and not self.api_key:
            raise ValueError(
                f"未找到 {self.provider} 的 API 密钥，请设置对应环境变量或 LLM_API_KEY"
            )

        # TODO 4: 解析模型
        self.model = model or os.getenv("LLM_MODEL_ID")

        # TODO 5: 保存参数并创建客户端
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    # ---------------------------------------------------------------
    # 核心辅助方法（教程 7.2.3）
    # ---------------------------------------------------------------

    def _auto_detect_provider(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
    ) -> str:
        """按三级优先级自动检测 provider，返回字符串。"""
        # 1.检查特定提供商的环境变量（最高优先级）
        if os.getenv("MODELSCOPE_API_KEY"): return "modelscope"
        if os.getenv("OPENAI_API_KEY"): return "openai"
        if os.getenv("ZHIPU_API_KEY"): return "zhipu"

        # 获取通用的环境变量
        actual_api_key = api_key or os.getenv("LLM_API_KEY")
        actual_base_url = base_url or os.getenv("LLM_BASE_URL")

        # 2.根据base_url判断
        if actual_base_url:
            base_url_lower = actual_base_url.lower()
            if "api-inference.modelscope.cn" in base_url_lower: return "modelscope"
            if "open.bigmodel.cn" in base_url_lower: return "zhipu"
            if "localhost" in base_url_lower or "127.0.0.1" in base_url_lower:
                if ":11434" in base_url_lower: return "ollama"
                if ":8000" in base_url_lower: return "vllm"
                return "local"  # 其他本地端口

        # 3. 根据API密钥格式辅助判断
        if actual_api_key:
            if actual_api_key.startswith("ms-"): return "modelscope"

        # 4. 兜底
        return "auto"

    def _resolve_credentials(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
    ) -> Tuple[str, str]:
        """根据provider解析API密钥和base_url"""
        if self.provider == "openai":
            resolved_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            resolved_base_url = base_url or os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
            return resolved_api_key, resolved_base_url

        elif self.provider == "modelscope":
            resolved_api_key = api_key or os.getenv("MODELSCOPE_API_KEY") or os.getenv("LLM_API_KEY")
            resolved_base_url = base_url or os.getenv("LLM_BASE_URL") or "https://api-inference.modelscope.cn/v1/"
            return resolved_api_key, resolved_base_url

        elif self.provider == "zhipu":
            resolved_api_key = api_key or os.getenv("ZHIPU_API_KEY") or os.getenv("LLM_API_KEY")
            resolved_base_url = base_url or os.getenv("LLM_BASE_URL") or "https://open.bigmodel.cn/api/paas/v4/"
            return resolved_api_key, resolved_base_url

        elif self.provider in ("ollama", "vllm", "local"):
            # 本地部署无需密钥
            resolved_api_key = api_key or os.getenv("LLM_API_KEY") or "ollama"
            if self.provider == "ollama":
                resolved_base_url = base_url or "http://localhost:11434/v1"
            elif self.provider == "vllm":
                resolved_base_url = base_url or "http://localhost:8000/v1"
            else:
                resolved_base_url = base_url or os.getenv("LLM_BASE_URL")
            return resolved_api_key, resolved_base_url

        else:  # auto：通用配置，无默认地址（使用 .env 的）
            resolved_api_key = api_key or os.getenv("LLM_API_KEY")
            resolved_base_url = base_url or os.getenv("LLM_BASE_URL")
            return resolved_api_key, resolved_base_url

    # ---------------------------------------------------------------
    # 调用接口（与 pip 包保持同名同签名，便于互换）
    # ---------------------------------------------------------------

    def invoke(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """同步非流式调用，返回完整文本。"""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        return response.choices[0].message.content

    def think(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """流式调用，逐段 yield 文本。"""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
