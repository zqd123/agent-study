# -*- coding: utf-8 -*-
"""7.2.3 自动检测机制测试。

只测 provider 检测逻辑（_auto_detect_provider / _resolve_credentials），
不发真实 API 请求，通过临时修改环境变量覆盖所有优先级分支。

运行：.venv/bin/python tests/test_llm_detect.py
（在 chapter07-agent-framework 目录下）
"""
import os
import sys
from pathlib import Path

# 保证可导入 core 包，并加载根目录 .env
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from core.llm import HelloAgentsLLM

PASS = "✅"
FAIL = "❌"
results = []


def check(name, actual, expected):
    ok = actual == expected
    results.append(ok)
    print(f"{PASS if ok else FAIL} {name}: 期望 {expected!r}, 实际 {actual!r}")


def with_env(**env):
    """临时设置/清除环境变量的装饰器，测完恢复，避免污染 .env 值。"""
    def decorator(fn):
        def wrapper():
            saved = {k: os.environ.get(k) for k in env}
            os.environ.update(env)
            try:
                fn()
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v
        return wrapper
    return decorator


# ---------- 第 1 级优先级：特定环境变量 ----------

@with_env(MODELSCOPE_API_KEY="ms-test", LLM_API_KEY="", LLM_BASE_URL="")
def test_env_modelscope():
    llm = HelloAgentsLLM()
    check("MODELSCOPE_API_KEY 存在", llm.provider, "modelscope")

@with_env(OPENAI_API_KEY="sk-test", LLM_API_KEY="", LLM_BASE_URL="")
def test_env_openai():
    llm = HelloAgentsLLM()
    check("OPENAI_API_KEY 存在", llm.provider, "openai")

@with_env(ZHIPU_API_KEY="z-test", LLM_API_KEY="", LLM_BASE_URL="")
def test_env_zhipu():
    llm = HelloAgentsLLM()
    check("ZHIPU_API_KEY 存在", llm.provider, "zhipu")

# ---------- 第 2 级优先级：解析 base_url ----------

@with_env(MODELSCOPE_API_KEY="", OPENAI_API_KEY="", ZHIPU_API_KEY="",
          LLM_API_KEY="k", LLM_BASE_URL="https://api-inference.modelscope.cn/v1/")
def test_url_modelscope():
    llm = HelloAgentsLLM()
    check("modelscope 域名", llm.provider, "modelscope")

@with_env(MODELSCOPE_API_KEY="", OPENAI_API_KEY="", ZHIPU_API_KEY="",
          LLM_API_KEY="k", LLM_BASE_URL="http://localhost:11434/v1")
def test_url_ollama():
    llm = HelloAgentsLLM()
    check("localhost:11434", llm.provider, "ollama")

@with_env(MODELSCOPE_API_KEY="", OPENAI_API_KEY="", ZHIPU_API_KEY="",
          LLM_API_KEY="k", LLM_BASE_URL="http://127.0.0.1:8000/v1")
def test_url_vllm():
    llm = HelloAgentsLLM()
    check("127.0.0.1:8000", llm.provider, "vllm")

@with_env(MODELSCOPE_API_KEY="", OPENAI_API_KEY="", ZHIPU_API_KEY="",
          LLM_API_KEY="k", LLM_BASE_URL="http://localhost:9999/v1")
def test_url_local():
    llm = HelloAgentsLLM()
    check("localhost 其他端口", llm.provider, "local")

# ---------- 第 3 级：密钥前缀 + 默认 auto ----------

@with_env(MODELSCOPE_API_KEY="", OPENAI_API_KEY="", ZHIPU_API_KEY="",
          LLM_API_KEY="ms-abc123", LLM_BASE_URL="")
def test_key_prefix():
    llm = HelloAgentsLLM()
    check("ms- 前缀密钥", llm.provider, "modelscope")

def test_auto_default():
    # 不设任何特定变量，用仓库真实 .env（digiwin URL 不匹配任何特征）
    llm = HelloAgentsLLM()
    check("真实 .env 兜底", llm.provider, "auto")

# ---------- _resolve_credentials：provider 决定默认 base_url ----------

@with_env(MODELSCOPE_API_KEY="ms-test", LLM_API_KEY="", LLM_BASE_URL="")
def test_resolve_modelscope_url():
    llm = HelloAgentsLLM()
    check("modelscope 默认地址", llm.base_url, "https://api-inference.modelscope.cn/v1/")

@with_env(OPENAI_API_KEY="sk-test", LLM_API_KEY="", LLM_BASE_URL="")
def test_resolve_openai_url():
    llm = HelloAgentsLLM()
    check("openai 默认地址", llm.base_url, "https://api.openai.com/v1")


if __name__ == "__main__":
    test_env_modelscope()
    test_env_openai()
    test_env_zhipu()
    test_url_modelscope()
    test_url_ollama()
    test_url_vllm()
    test_url_local()
    test_key_prefix()
    test_auto_default()
    test_resolve_modelscope_url()
    test_resolve_openai_url()

    passed = sum(results)
    print(f"\n{'='*40}\n结果: {passed}/{len(results)} 通过")
    sys.exit(0 if passed == len(results) else 1)
