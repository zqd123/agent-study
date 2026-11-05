# -*- coding: utf-8 -*-
"""test_simple_agent.py —— 对应教程 7.4.1 的 4 个验收场景。

与教程 test_simple_agent.py 一致：
1. 基础对话（无工具）
2. 工具增强对话（CalculatorTool，15*8+32）
3. 流式响应
4. 动态工具管理
"""
import sys
from pathlib import Path

# 支持直接运行：把 chapter07 目录加入 sys.path 以便导入 agents 包
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / ".env")  # 仓库根目录 .env

from hello_agents import HelloAgentsLLM, ToolRegistry
from hello_agents.core.exceptions import HelloAgentsException
from hello_agents.tools import CalculatorTool
from agents.my_simple_agent import MySimpleAgent

# 创建 LLM 实例
llm = HelloAgentsLLM()

# ===== 测试 1：基础对话 Agent（无工具）=====
print("=== 测试1：基础对话 ===")
basic_agent = MySimpleAgent(
    name="基础助手",
    llm=llm,
    system_prompt="你是一个友好的AI助手，请用简洁明了的方式回答问题。",
    enable_tool_calling=False,
)
response1 = basic_agent.run("你好，请介绍一下自己")
print(f"基础对话响应: {response1}\n")

# ===== 测试 2：带工具的 Agent =====
print("=== 测试2：工具增强对话 ===")
tool_registry = ToolRegistry()
calculator = CalculatorTool()
tool_registry.register_tool(calculator)

enhanced_agent = MySimpleAgent(
    name="增强助手",
    llm=llm,
    system_prompt="你是一个智能助手，可以使用工具来帮助用户。",
    tool_registry=tool_registry,
    enable_tool_calling=True,
)
response2 = enhanced_agent.run("请帮我计算 15 * 8 + 32")
print(f"工具增强响应: {response2}\n")

# ===== 测试 3：流式响应 =====
print("=== 测试3：流式响应 ===")
print("流式响应: ", end="")
try:
    for chunk in basic_agent.stream_run("请解释什么是人工智能"):
        pass  # 内容已在 stream_run 中实时打印
except HelloAgentsException as e:
    # pip 包 bug：think() 未保护末尾 usage-only chunk（choices 为空列表），
    # 内容已完整流出，此处吞掉异常即可
    print(f"\n[已知 pip 包流式末尾 chunk 崩溃，已捕获: {e}]")

# ===== 测试 4：动态添加工具 =====
print("\n=== 测试4：动态工具管理 ===")
print(f"添加工具前: {basic_agent.has_tools()}")
basic_agent.add_tool(CalculatorTool())
print(f"添加工具后: {basic_agent.has_tools()}")
print(f"可用工具: {basic_agent.list_tools()}")

# 查看对话历史
print(f"\n对话历史: {len(basic_agent.get_history())} 条消息")
