# -*- coding: utf-8 -*-
"""MyReflectionAgent（7.4.3）—— 严格按教程：继承 pip 包 ReflectionAgent 重写。

对应教程 7.4.3 节。教程只给出提示词模板与测试代码，要求参考第四章实现
自行构建。与教程一致的设计：
- 继承 hello_agents.ReflectionAgent（pip 包）
- DEFAULT_PROMPTS 三套通用模板：initial / reflect / refine（教程原文）
- 重写 run()：初始执行 → 反思循环（"无需改进"即停）→ 优化
- 复用 pip 基类的 _get_llm_response() 私有方法与 Memory 短期记忆
"""
from typing import Dict, Optional

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from hello_agents import ReflectionAgent, HelloAgentsLLM, Config, Message
# Memory 与 DEFAULT_PROMPTS 定义在 pip 包的 reflection_agent 模块里（未导出到顶层）
from hello_agents.agents.reflection_agent import Memory

# TODO 1: 定义 DEFAULT_PROMPTS（教程 7.4.3 原文，一字不差）
#   三个模板，占位符分别为：
#   - "initial": {task}
#   - "reflect": {task} {content}   （反思提示：回答"无需改进"则停止）
#   - "refine": {task} {last_attempt} {feedback}
DEFAULT_PROMPTS: Dict[str, str] = {
    "initial": """
请根据以下要求完成任务:

任务: {task}

请提供一个完整、准确的回答。
""",
    "reflect": """
请仔细审查以下回答，并找出可能的问题或改进空间:

# 原始任务:
{task}

# 当前回答:
{content}

请分析这个回答的质量，指出不足之处，并提出具体的改进建议。
如果回答已经很好，请回答"无需改进"。
""",
    "refine": """
请根据反馈意见改进你的回答:

# 原始任务:
{task}

# 上一轮回答:
{last_attempt}

# 反馈意见:
{feedback}

请提供一个改进后的回答。
"""
}  # 替换为教程三段模板字符串


class MyReflectionAgent(ReflectionAgent):
    """重写的反思 Agent —— 执行 → 反思 → 优化 迭代循环。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_iterations: int = 3,
        custom_prompts: Optional[Dict[str, str]] = None,
    ) -> None:
        # TODO 2: 调 super().__init__(name, llm, system_prompt, config)
        #   然后设置：
        #   - self.max_iterations = max_iterations
        #   - self.memory = Memory()
        #   - self.prompts = custom_prompts if custom_prompts else DEFAULT_PROMPTS
        #   - print(f"✅ {name} 初始化完成，最大迭代次数: {max_iterations}")
        super().__init__(name, llm, system_prompt, config)
        self.max_iterations = max_iterations
        self.memory = Memory()
        self.prompts = custom_prompts if custom_prompts else DEFAULT_PROMPTS
        print(f"✅ {name} 初始化完成，最大迭代次数: {max_iterations}")

    # TODO 3: run(input_text, **kwargs) -> str —— 教程式迭代循环
    #   print(f"\n🤖 {self.name} 开始处理任务: {input_text}")；重置 self.memory = Memory()
    #   1. 初始执行：
    #      initial_prompt = self.prompts["initial"].format(task=input_text)
    #      initial_result = self._get_llm_response(initial_prompt, **kwargs)  # 复用 pip 基类
    #      self.memory.add_record("execution", initial_result)
    #   2. for i in range(self.max_iterations):
    #      a. 反思：reflect_prompt = self.prompts["reflect"].format(task=input_text, content=last_result)
    #         last_result = self.memory.get_last_execution()
    #         feedback = self._get_llm_response(reflect_prompt, **kwargs)
    #         self.memory.add_record("reflection", feedback)
    #      b. 停止条件：feedback 含 "无需改进" 或 "no need for improvement"（lower()）
    #         → print 提示 + break
    #      c. 优化：refine_prompt = self.prompts["refine"].format(
    #             task=input_text, last_attempt=last_result, feedback=feedback)
    #         refined_result = self._get_llm_response(refine_prompt, **kwargs)
    #         self.memory.add_record("execution", refined_result)
    #   3. final_result = self.memory.get_last_execution()
    #   4. 存历史（Message(input_text, "user") + Message(final_result, "assistant")）
    #   5. return final_result
    def run(self, input_text: str, **kwargs) -> str:
        print(f"\n🤖 {self.name} 开始处理任务: {input_text}")

        # 重置记忆
        self.memory = Memory()

        # 1. 初始执行
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = self.prompts["initial"].format(task=input_text)
        initial_result = self._get_llm_response(initial_prompt, **kwargs)
        self.memory.add_record("execution", initial_result)

        # 2. 迭代循环：反思与优化
        for i in range(self.max_iterations):
            print(f"\n--- 第 {i + 1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")
            last_result = self.memory.get_last_execution()
            reflect_prompt = self.prompts["reflect"].format(
                task=input_text,
                content=last_result,
            )
            feedback = self._get_llm_response(reflect_prompt, **kwargs)
            self.memory.add_record("reflection", feedback)

            # b. 停止条件：反思认为无需改进
            if "无需改进" in feedback or "no need for improvement" in feedback.lower():
                print("\n✅ 反思认为结果已无需改进，任务完成。")
                break

            # c. 优化
            print("\n-> 正在进行优化...")
            refine_prompt = self.prompts["refine"].format(
                task=input_text,
                last_attempt=last_result,
                feedback=feedback,
            )
            refined_result = self._get_llm_response(refine_prompt, **kwargs)
            self.memory.add_record("execution", refined_result)

        # 3. 取最后一次执行结果作为最终答案
        final_result = self.memory.get_last_execution()
        print(f"\n--- 任务完成 ---\n最终结果:\n{final_result}")

        # 4. 存历史
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_result, "assistant"))

        return final_result
