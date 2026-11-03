# -*- coding: utf-8 -*-
"""体验框架内置的 ReActAgent + 工具系统。

对应教程 test_react_agent.py / 7.5.1 工具注册机制。

⚠️ 实测坑：内置 DEFAULT_REACT_PROMPT 要求模型输出 "**Action:**"（markdown 加粗），
但包内解析正则只认裸的 "Action: "，GLM 这类模型会输出加粗格式导致解析失败。
教程 my_react_agent.py 的解法是自定义 MY_REACT_PROMPT 去掉加粗，这里照做。

运行：python experience/02_react_agent.py
"""
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

from hello_agents import (
    HelloAgentsLLM,
    ReActAgent,
    ToolRegistry,
    calculate,
)

# 与教程 my_react_agent.py 一致的自定义提示词（无 markdown 加粗）
MY_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]，不要使用markdown加粗或代码块包裹
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动：
"""


def main() -> None:
    llm = HelloAgentsLLM()

    # 创建工具注册表并注册内置计算器函数
    tool_registry = ToolRegistry()
    tool_registry.register_function(
        "calculate", "执行数学计算，支持基本的四则运算", calculate
    )
    print("🔧 已注册工具:", tool_registry.list_tools())

    # 创建内置 ReActAgent，传入自定义提示词规避 markdown 解析问题
    agent = ReActAgent(
        name="推理行动助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=5,
        custom_prompt=MY_REACT_PROMPT,
    )

    question = "请帮我计算 (128 + 72) * 3 - 100 的结果"
    print(f"\n❓ 问题: {question}\n")
    answer = agent.run(question)
    print(f"\n✅ 最终答案: {answer}")


if __name__ == "__main__":
    main()
