# -*- coding: utf-8 -*-
"""MyReActAgent（7.4.2）—— 严格按教程：继承 pip 包 ReActAgent 重写增强。

对应教程 my_react_agent.py。与教程完全一致：
- 继承 hello_agents.ReActAgent（pip 包），不改库源码
- 自定义 MY_REACT_PROMPT 提示词模板（{tools} {question} {history} 三个占位符）
- 重写 run()：Thought -> Action -> Observation 多步循环
- 解析辅助方法直接复用 pip 基类的 _parse_output / _parse_action / _parse_action_input
"""
import re
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from hello_agents import ReActAgent, HelloAgentsLLM, Config, Message, ToolRegistry

# TODO 1: 定义 MY_REACT_PROMPT 提示词模板（教程原文，一字不差）
#   必须包含三个占位符：{tools}（工具描述）、{question}（当前任务）、{history}（执行历史）
#   核心格式约束：
#     Thought: 思考过程
#     Action: tool_name[tool_input] 或 Finish[最终答案]
#   为什么不用 pip 包内置 DEFAULT_REACT_PROMPT：
#     实测坑——内置模板让模型输出 markdown 加粗 **Action:**，而解析正则只认裸 "Action: "，
#     会导致 _parse_output 解析失败。MY_REACT_PROMPT 明确要求裸格式，规避此坑。

MY_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么行动。
Action: 选择一个行动，格式必须是以下之一:
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循:工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动:
"""

class MyReActAgent(ReActAgent):
    """重写的 ReAct Agent —— 推理与行动结合的智能体。
    name： Agent的名称。
    llm： HelloAgentsLLM的实例，负责与大语言模型通信。
    tool_registry： ToolRegistry的实例，用于管理和执行Agent可用的工具。
    system_prompt： 系统提示词，用于设定Agent的角色和行为准则。
    config： 配置对象，用于传递框架级的设置。
    max_steps： ReAct循环的最大执行步数，防止无限循环。
    custom_prompt： 自定义的提示词模板，用于替换默认的ReAct提示词。
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: str | None = None,
        config: Config | None = None,
        max_steps: int = 5,
        custom_prompt: str | None = None,
    ) -> None:
        # TODO 2: 调 super().__init__(name, llm, system_prompt, config)
        super().__init__(name,llm,system_prompt,config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history:list[str] = []
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT
        print(f"✅ {name} 初始化完成，最大步数: {max_steps}")

    # TODO 3: run(input_text, **kwargs) -> str —— 核心循环（教程原样）
    def run(self,input_text:str,**kwargs)->str:
        """运行ReAct Agent"""
        self.current_history = []
        current_step = 0

        print(f"\n🤖 {self.name} 开始处理问题: {input_text}")

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第{current_step} 步 ---")

            # 1. 构建提示词
            tools_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=input_text,
                history=history_str
            )

            # 2. 调用LLM
            message = [{"role":"user","content":prompt}]
            response_text = self.llm.invoke(message,**kwargs) #调用执行

            # 3. 解析输出
            thought, action = self._parse_output(response_text)

            # 4.检查完成条件
            if action and action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                self.add_message(Message(input_text, "user"))
                self.add_message(Message(final_answer,"assistant"))
                return final_answer

            # 5.执行工具调用
            if action:
                tool_name,tool_input = self._parse_action(action)
                observation = self.tool_registry.execute_tool(tool_name,tool_input)
                self.current_history.append(f"Action: {action}")
                self.current_history.append(f"Observation : {observation}")

        # 达到最大步数
        final_answer = "抱歉，我无法在限定步数内完成这个任务。"
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer,"assistant"))
        return final_answer

if __name__ == '__main__':
    react_agent = MyReActAgent()
