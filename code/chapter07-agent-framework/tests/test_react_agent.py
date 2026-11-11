# -*- coding: utf-8 -*-
"""test_react_agent.py —— 对应教程 7.4.2 的验收测试。

与教程 test_react_agent.py 一致：
1. test_react_agent：数学计算 / 信息搜索 / 复合推理 三个问题
2. test_custom_prompt：自定义提示词模板 + max_steps=3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / ".env")  # 仓库根目录 .env

from hello_agents import HelloAgentsLLM, ToolRegistry, calculate, search
from agents.my_react_agent import MyReActAgent


def test_react_agent():
    """测试 MyReActAgent 的功能"""
    llm = HelloAgentsLLM()
    tool_registry = ToolRegistry()

    print("🔧 注册测试工具...")
    tool_registry.register_function("calculate", "执行数学计算，支持基本的四则运算", calculate)
    print("✅ 计算器工具注册成功")
    tool_registry.register_function("search", "搜索互联网信息", search)
    print("✅ 搜索工具注册成功")

    agent = MyReActAgent(
        name="我的推理行动助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=5,
    )

    print("\n" + "=" * 60)
    print("开始测试 MyReActAgent")
    print("=" * 60)

    # 测试1：数学计算问题
    print("\n📊 测试1：数学计算问题")
    result1 = agent.run("请帮我计算：(25 + 15) * 3 - 8 的结果是多少？")
    print(f"\n🎯 测试1结果: {result1}")

    # 测试2：需要搜索的问题
    print("\n🔍 测试2：信息搜索问题")
    result2 = agent.run("Python编程语言是什么时候发布的？请告诉我具体的年份。")
    print(f"\n🎯 测试2结果: {result2}")

    # 测试3：复合问题（需要多步推理）
    print("\n🧠 测试3：复合推理问题")
    result3 = agent.run("如果一个班级有30个学生，其中60%是女生，那么男生有多少人？请先计算女生人数，再计算男生人数。")
    print(f"\n🎯 测试3结果: {result3}")

    print(f"\n📝 对话历史记录: {len(agent.get_history())} 条消息")
    print(f"\n🛠️ 已注册工具: {list(tool_registry._tools.keys())}")


def test_custom_prompt():
    """测试自定义提示词的 ReActAgent"""
    print("\n" + "=" * 60)
    print("测试自定义提示词的 MyReActAgent")
    print("=" * 60)

    llm = HelloAgentsLLM()
    tool_registry = ToolRegistry()
    tool_registry.register_function("calculate", "数学计算工具", calculate)

    custom_prompt = """你是一个数学专家AI助手。

可用工具：{tools}

请按以下格式回应：
Thought: [你的思考]
Action: [tool_name[input] 或 Finish[答案]]

问题：{question}
历史：{history}

开始："""

    custom_agent = MyReActAgent(
        name="数学专家助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=3,
        custom_prompt=custom_prompt,
    )

    result = custom_agent.run("计算 15 × 8 + 32 ÷ 4 的结果")
    print(f"\n🎯 自定义提示词测试结果: {result}")


if __name__ == "__main__":
    test_react_agent()
    test_custom_prompt()
    print("\n✨ 所有测试完成！")
