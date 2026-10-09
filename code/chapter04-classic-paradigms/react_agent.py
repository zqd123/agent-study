"""
第四章实践：最小 ReAct Agent

学习目标：
1. 构造 ReAct prompt
2. 解析 Thought / Action
3. 执行工具并将 Observation 写回历史
4. 遇到 Finish[...] 时返回最终答案
"""

# Agent执行过程
# Thought -> Action -> Observation -> Thought -> Action -> ... -> Finish[答案]
import re
from llm_client import HelloAgentsLLM
from tools import ToolExecutor

# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""
class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        运行ReAct智能体来回答一个问题。
        """
        self.history = [] # 每次运行时重置历史记录
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            # 2. 调用LLM进行思考
            message = [{"role":"user", "content": prompt}]
            response_text = self.llm_client.think(message=message)

            if not response_text:
                print("错误：LLM未能返回有效响应。")
                break

            # (这段逻辑在 run 方法的 while 循环内)
            # 3. 解析LLM的输出
            thought, action = self._parse_output(response_text)
            action = self._clean_action(action)
            
            if thought:
                print(f"思考: {thought}")

            if not action:
                print("警告:未能解析出有效的Action，流程终止。")
                break

            # 4. 执行Action
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = self._parse_final_answer(action)
                if final_answer is None:
                    print("警告: Finish 格式无效，请使用 Finish[最终答案]。")
                    print(f"原始Action: {repr(action)}")
                    self.history.append(f"Action: {action}")
                    self.history.append("Observation: Finish 格式错误，请使用 Finish[最终答案]。")
                    continue

                print(f"🎉 最终答案: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # ... 处理无效Action格式 ...
                continue

            print(f"🎬 行动: {tool_name}[{tool_input}]")
            
            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input) # 调用真实工具

            print(f"👀 观察: {observation}")
            
            # 将本轮的Action和Observation添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        # 循环结束
        print("已达到最大步数，流程终止。")
        return None


    def _parse_output(self, text: str):
        """
        解析LLM的输出，提取Thought和Action。
        """
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """
        解析Action字符串，提取工具名称和输入。
        例如从 Search[华为最新手机] 中提取出工具名 Search 和工具输入 华为最新手机。

        """
        action_text = self._clean_action(action_text)
        match = re.match(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*[\[【［]\s*(.*?)\s*[\]】］]\s*$",
            action_text,
            re.DOTALL
        )
        if match:
            return match.group(1), match.group(2)
        return None, None


    def _parse_final_answer(self, action_text: str):
        """
        解析Finish[最终答案]中的最终答案。
        兼容多行答案、中文括号和Markdown反引号。
        """
        action_text = self._clean_action(action_text)
        match = re.search(
            r"Finish\s*[\[【［]\s*(.*?)\s*[\]】］]\s*$",
            action_text,
            re.DOTALL
        )
        return match.group(1).strip() if match else None


    def _clean_action(self, action_text):
        """
        清理Action两侧的空白、反引号和星号，避免Markdown格式影响解析。
        """
        if not action_text:
            return ""
        return action_text.strip().strip("`").strip("*").strip()

# 下面是测试验证代码
# if __name__ == "__main__":
#     def mock_weather(city: str) -> str:
#         return f"{city} 今天晴，25°C"

#     def mock_search(query: str) -> str:
#         return f"搜索结果：{query} 适合户外运动。"

#     tool_executor = ToolExecutor()

#     tool_executor.register_tool(
#         name="Weather",
#         description="查询指定城市今天的天气。",
#         func=mock_weather
#     )

#     tool_executor.register_tool(
#         name="Search",
#         description="搜索相关信息。",
#         func=mock_search
#     )

#     llm = HelloAgentsLLM()

#     agent = ReActAgent(
#         llm_client=llm,
#         tool_executor=tool_executor,
#         max_steps=5
#     )

#     agent.run("北京今天天气怎么样？适合户外运动吗？")
