# -*- coding: utf-8 -*-
"""7.2.1 多提供商(provider)支持 —— 继承扩展 pip 包的 HelloAgentsLLM。

对应教程 my_llm.py：不改库源码，通过继承增加 ModelScope 支持。

核心思想：
- 拦截 provider="modelscope" 的情况，自己解析凭证并创建客户端
- 其他 provider 交还 super().__init__()，保留框架原有功能
- think() / invoke() 等方法直接继承，无需重写

"""
from operator import itemgetter
from typing import Optional

from hello_agents import HelloAgentsLLM
import os

from openai import OpenAI


class MyLLM(HelloAgentsLLM):
    # MyLLM 类中重写 __init__ 方法。我们的目标是：当用户传入 provider="modelscope" 时，执行我们自定义的逻辑；
    # 否则，就调用父类 HelloAgentsLLM 的原始逻辑，使其能够继续支持 OpenAI 等其他内置的供应商。
    def __init__(
        self,
        model:Optional[str]=None,
        api_key:Optional[str]=None,
        base_url:Optional[str]=None,
        provider:Optional[str]=None,
        **kwargs
    ):
        # 步骤1: if provider == "modelscope":
        if provider == "modelscope":
            print("正在使用自定义的ModelScope Provider")
            self.provider = "modelscope"

            # 解析ModelScope的凭证
            self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = base_url or "https://api-inference.modelscope.cn/v1/"

            # 验证凭证是否存在
            if not self.api_key:
                raise ValueError("找不到 ModelScope API 密钥。请设置MODELSCOPE_API_KEY环境变量。")

            # 设置默认模型和其他参数
            # 模型id
            self.model = model or os.getenv("LLM_MODEL_ID") or "Qwen/Qwen2.5-VL-72B-Instruct"
            # 温度（大模型生成时的**随机度参数**，一般取值范围：**0 ~ 2**）
            # temperature 越低，回答越确定；越高，越发散。
            self.temperature = kwargs.get("temperature", 0.7)
            # 限制模型这一轮最多能输出多少 token
            self.max_tokens = kwargs.get("max_tokens")
            # 超时
            self.timeout = kwargs.get("timeout", 60)

            # 使用获取的参数创建OpenAI客户端实例
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url,timeout=self.timeout)
        else:
            # 如果不是 modelscope，则完全使用父类的原始逻辑来处理
            super().__init__(model=model,api_key=api_key,base_url=base_url,provider=provider,**kwargs)

if __name__ == '__main__':
    llm = MyLLM()
