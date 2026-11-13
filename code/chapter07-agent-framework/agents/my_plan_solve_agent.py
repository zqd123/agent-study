# -*- coding: utf-8 -*-
"""MyPlanAndSolveAgent（7.4.4）—— 严格按教程：继承 pip 包 PlanAndSolveAgent 重写。

对应教程 7.4.4 节。教程只给出提示词模板与测试代码，要求自行设计实现。
设计要点（本节学习重点）：
- 强制 Planner 以 Python 列表格式输出计划，用 ast.literal_eval 解析
- 完整异常处理：解析失败返回空列表，任务安全终止
- Planner / Executor 职责分离：规划一次，逐步执行
- 继承 hello_agents.PlanAndSolveAgent（pip 包）
"""
import ast
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from hello_agents import PlanAndSolveAgent, HelloAgentsLLM, Config, Message

# TODO 1: 定义两个默认提示词模板（教程 7.4.4 原文，一字不差）
#   - DEFAULT_PLANNER_PROMPT：占位符 {question}，输出必须是 ```python ["步骤1", ...] ``` 列表
#   - DEFAULT_EXECUTOR_PROMPT：占位符 {question} {plan} {history} {current_step}
# 默认规划器提示词模板
DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


class MyPlanner:
    """规划器 —— 将复杂问题分解为简单步骤列表。"""

    def __init__(self, llm_client: HelloAgentsLLM, prompt_template: Optional[str] = None) -> None:
        self.llm_client = llm_client
        self.prompt_template = prompt_template if prompt_template else DEFAULT_PLANNER_PROMPT

    # TODO 2: plan(question, **kwargs) -> List[str] —— 教程式解析与异常处理
    #   1. prompt = self.prompt_template.format(question=question)
    #      messages = [{"role": "user", "content": prompt}]
    #      print("--- 正在生成计划 ---")
    #      response_text = self.llm_client.invoke(messages, **kwargs) or ""
    #      print(f"✅ 计划已生成:\n{response_text}")
    #   2. try 提取并解析：
    #      plan_str = response_text.split("```python")[1].split("```")[0].strip()
    #      plan = ast.literal_eval(plan_str)      # 安全解析，不要用 eval
    #      return plan if isinstance(plan, list) else []
    #   3. 异常处理（教程强调的稳定性机制）：
    #      - (ValueError, SyntaxError, IndexError) → 打印错误 + 原始响应，return []
    #      - Exception → 打印未知错误，return []
    def plan(self, question: str, **kwargs) -> List[str]:
        prompt = self.prompt_template.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        print("--- 正在生成计划 ---")
        response_text = self.llm_client.invoke(messages, **kwargs) or ""
        print(f"✅ 计划已生成:\n{response_text}")
        # 提取并解析：
        try:
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_str)  # 安全解析，不要用 eval
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []


class MyExecutor:
    """执行器 —— 按计划逐步执行并维护历史。"""

    def __init__(self, llm_client: HelloAgentsLLM, prompt_template: Optional[str] = None) -> None:
        self.llm_client = llm_client
        self.prompt_template = prompt_template if prompt_template else DEFAULT_EXECUTOR_PROMPT

    # TODO 3: execute(question, plan, **kwargs) -> str —— 逐步执行循环
    #   history = ""；final_answer = ""
    #   print("--- 正在执行计划 ---")
    #   for i, step in enumerate(plan, 1):
    #       print(f"\n-> 正在执行步骤 {i}/{len(plan)}: {step}")
    #       prompt = self.prompt_template.format(
    #           question=question, plan=plan,
    #           history=history if history else "无",
    #           current_step=step)
    #       response_text = self.llm_client.invoke([...], **kwargs) or ""
    #       history += f"步骤 {i}: {step}\n结果: {response_text}\n\n"
    #       final_answer = response_text   # 最后一步的结果就是最终答案
    #       print(f"✅ 步骤 {i} 已完成，结果: {final_answer}")
    #   return final_answer
    def execute(self, question: str, plan: List[str], **kwargs) -> str:
        history = ""
        final_answer = ""
        print("--- 正在执行计划 ---")
        for i, step in enumerate(plan, 1):
            print(f"\n-> 正在执行步骤 {i}/{len(plan)}: {step}")
            prompt = self.prompt_template.format(
                question=question, plan=plan,
                history=history if history else "无",
                current_step=step)
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.invoke(messages, **kwargs) or ""
            history += f"步骤 {i}: {step}\n结果: {response_text}\n\n"
            final_answer = response_text   # 最后一步的结果就是最终答案
            print(f"✅ 步骤 {i} 已完成，结果: {final_answer}")
        return final_answer


class MyPlanAndSolveAgent(PlanAndSolveAgent):
    """重写的规划执行 Agent —— 先规划分解，再逐步执行。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        custom_prompts: Optional[Dict[str, str]] = None,
    ) -> None:
        # TODO 4: 调 super().__init__(name, llm, system_prompt, config)
        #   然后构建自己的规划器与执行器：
        #   if custom_prompts:
        #       planner_prompt = custom_prompts.get("planner")
        #       executor_prompt = custom_prompts.get("executor")
        #   else:
        #       planner_prompt = None；executor_prompt = None
        #   self.planner = MyPlanner(self.llm, planner_prompt)
        #   self.executor = MyExecutor(self.llm, executor_prompt)
        #   print(f"✅ {name} 初始化完成")
        super().__init__(name, llm, system_prompt, config)
        if custom_prompts:
            planner_prompt = custom_prompts.get("planner")
            executor_prompt = custom_prompts.get("executor")
        else:
            planner_prompt = None
            executor_prompt = None
        self.planner = MyPlanner(self.llm, planner_prompt)
        self.executor = MyExecutor(self.llm, executor_prompt)
        print(f"✅ {name} 初始化完成")

    # TODO 4: run(input_text, **kwargs) -> str
    #   print(f"\n🤖 {self.name} 开始处理问题: {input_text}")
    #   1. plan = self.planner.plan(input_text, **kwargs)
    #      plan 为空 → final_answer = "无法生成有效的行动计划，任务终止。"
    #               → 存历史 + return（安全终止，这就是异常处理机制的意义）
    #   2. final_answer = self.executor.execute(input_text, plan, **kwargs)
    #   3. 存历史（Message(input_text, "user") + Message(final_answer, "assistant")）
    #   4. return final_answer
    def run(self, input_text: str, **kwargs) -> str:
        print(f"\n🤖 {self.name} 开始处理问题: {input_text}")
        plan = self.planner.plan(input_text, **kwargs)
        if not plan:
            final_answer = "无法生成有效的行动计划，任务终止。"
            print(f"\n--- 任务终止 ---\n{final_answer}")
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(final_answer, "assistant"))
            return final_answer
        final_answer = self.executor.execute(input_text, plan, **kwargs)
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer
