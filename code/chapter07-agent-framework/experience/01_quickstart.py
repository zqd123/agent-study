# -*- coding: utf-8 -*-
"""30 秒体验 HelloAgents 框架：SimpleAgent 基础对话。

对应教程 7.1.3 快速开始示例。

运行：python experience/01_quickstart.py
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

# 仓库根目录 .env（LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_ID）
ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

from hello_agents import HelloAgentsLLM, SimpleAgent


def main() -> None:
    # 创建 LLM 实例 —— 框架自动检测 provider（供应商）（基于 LLM_BASE_URL/LLM_API_KEY）
    llm = HelloAgentsLLM()
    print(f"🔎 检测到的 provider（供应商）: {llm.provider}")

    # 创建简单的对话Agent： SimpleAgent
    agent = SimpleAgent(
        name="AI助手",
        llm=llm,
        system_prompt="你是一个有用的AI助手，请用中文简洁回答",
    )

    # 基础对话
    print("\n--- 对话 1 ---")
    response = agent.run("你好！请用一句话介绍你自己")
    print(f"回复: {response}")

    # 带上下文的对话（验证历史记忆）
    print("\n--- 对话 2（验证记忆）---")
    response = agent.run("我上一句话问了你什么？")
    print(f"回复: {response}")

    # 查看对话历史
    print(f"\n📜 历史消息数: {len(agent.get_history())}")
    for msg in agent.get_history():
        print(f"  {msg}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        sys.exit(1)
