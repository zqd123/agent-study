import requests
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from openai import OpenAI
import re

load_dotenv()  # 自动加载同目录下的 .env 文件

# ============================================================
# 工具层：智能体的"手"
# 每个工具 = 一个普通 Python 函数：接收参数 → 执行动作 → 返回"自然语言"结果
# 关键约定：工具内部永不抛异常，一切错误都转成字符串返回——
#           这样错误会作为 Observation 喂回 LLM，让它自己决定下一步怎么补救
# ============================================================

# 查某个城市的天气信息
def get_weather(city: str)->str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    url = f"https://wttr.in/{city}?format=j1"
    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200（成功）
        response.raise_for_status()
        # 解析返回的 JSON 数据
        data = response.json()

        # 提取当前天气状况
        current_condition = data["current_condition"][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        # 格式化成自然语言返回
        return f"{city} 的当前天气是: {weather_desc}, 温度为 {temp_c}°C"
    except requests.exceptions.RequestException as e:
        return f"错误：查询天气时遇到网络问题- {e}"
    except (KeyError, IndexError) as e:
        return f"错误：解析天气数据失败，可能是城市名称无效- {e}"

# 验证：临时加一行 print(get_weather("北京"))，能输出 JSON 天气数据就通过
# print(get_weather("北京"))
# print(get_weather("南京"))


# 根据城市和天气推荐旅游景点
def get_attraction(city:str,weather:str)->str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。
    """
    # 1. 从环境变量中读取API密钥
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误：未配置TAVILY_API_KEY环境变量。"

    # 2. 初始化 Tavily 客户端
    tavily = TavilyClient(api_key=api_key)

    # 3. 构造一个精确的查询
    query = f"{city} 在 '{weather}'天气下最值得去的旅游景点推荐及理由"

    try:
        # 4. 调用API， include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query,search_depth="basic",include_answer=True)

        # 5. Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get('answer'):
            return response['answer']

        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get('results',[]):
            formatted_results.append(f"- {result['title']}:{result['content']}")

        if not formatted_results:
            return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted_results)
    
    except Exception as e:
        return f"错误：调用Tavily API时发生异常- {e}"

    
# 工具字典（分发表 / Dispatch Table）
# 作用：把 LLM 输出的"函数名字符串"映射到真实的 Python 函数，
#       主循环里 available_tools[tool_name](**kwargs) 一行即完成调用分发。
#       第七章自研框架时，这里会演化成带参数校验、自动描述生成的完整 Tool 类。
available_tools = {
    "get_weather":get_weather,
    "get_attraction":get_attraction
}


# ============================================================
# 大脑层：系统提示词 = 你与 LLM 之间的"输出协议"
# 结构：角色定义 → 可用工具清单 → 输出格式约定 → 收紧约束
# 注意：这里的工具清单必须与 available_tools 字典人工保持同步（改进点：
#       第七章会用装饰器从工具函数自动生成这段清单）
# 主循环里的所有解析正则，本质上都是在解析这份协议的产物
# ============================================================

AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式要求:
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought: [你的思考过程和下一步计划]
Action: [你要执行的具体行动]

Action的格式必须是以下之一：
1. 调用工具：function_name(arg_name="arg_value")
2. 结束任务：Finish[最终答案]

# 重要提示:
- 每次只输出一对Thought-Action
- Action必须在同一行，不要换行
- 当收集到足够信息可以回答用户问题时，必须使用 Action: Finish[最终答案] 格式结束

请开始吧！
"""


# ============================================================
# LLM 客户端：OpenAI 兼容封装
# 任何兼容 OpenAI 协议的服务商（DeepSeek/GLM/通义...）只需改 .env，代码零改动
# ============================================================

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self,model:str,api_key:str,base_url:str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self,prompt:str,system_prompt:str)->str:
        """调用LLM API来生成回应。"""
        print("正在调用大语言模型。。。")
        try:
            messages = [
                {'role':'system','content':system_prompt},
                {'role':'user','content':prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("大语言模型响应成功。")
            return answer
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return "错误：调用大语言模型时发生错误"

# 1. 配置LLM客户端（密钥和模型名统一从 .env 读取，代码中不出现明文）
API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_URL = os.environ.get("OPENAI_API_BASE_URL")
MODEL_ID = os.environ.get("MODEL_ID")


llm = OpenAICompatibleClient(
    model=MODEL_ID, 
    api_key=API_KEY,
    base_url=BASE_URL
)

# 2. 初始化
user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "="*40)

# ============================================================
# 循环层：主循环 = ReAct 循环引擎（整个智能体的"心跳"）
# 每一轮完成一次完整的闭环：
#   1) 拼接历史 prompt        —— 智能体的"短期记忆"（LLM 本身无状态）
#   2) 调用 LLM 思考          —— 产生本轮 Thought + Action
#   3) 截断多余输出           —— 强制只保留一对 Thought-Action
#   4) 解析并执行 Action      —— LLM 的"话"变成真实的"行动"
#   5) 执行结果包装成 Observation 喂回历史 —— 成为下一轮的"观察"
# ============================================================
for i in range(5):  # 最多 5 轮，防止无限循环（改进点：轮数可提取为常量/参数）
    print(f"--- 循环 {i+1} ---\n")

    # --- 3.1 构建本轮 Prompt：观察与记忆的载体 ---
    # prompt_history 不断累积：用户请求、历轮 Thought/Action、历轮 Observation
    # 全部拼接后整条发给 LLM —— 模型"看到"的上下文就是它的全部记忆
    full_prompt = "\n".join(prompt_history)

    # --- 3.2 调用 LLM 思考（Thought 诞生的地方）---
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)

    # 截断：模型可能不遵守"只输出一对"的约定，连续输出多轮计划甚至幻觉出 Observation。
    # 正则解读：
    #   (Thought:.*?Action:.*?)          → 捕获第一对 Thought-Action（懒惰匹配，尽量少）
    #   (?=...)                           → 前瞻断言：只定"停在哪"，不吞进结果
    #   \n\s*(?:Thought:|Action:|Observation:)  → 停在下一块标记之前
    #   \Z                                → 或者停在字符串末尾
    #   re.DOTALL                         → 让 . 能匹配换行符
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():  # 截取结果 ≠ 原文 → 说明原文确有多余内容
            llm_output = truncated
            print("截断多余的Thought-Action。")
    print(f"模型输出: \n{llm_output}\n")
    # 本轮 Thought/Action 存入历史，下一轮 LLM 能"记得"自己说过什么
    prompt_history.append(llm_output)

    # --- 3.3 解析并执行行动：Action → 真实工具调用 ---
    # 提取 "Action: " 之后的全部内容（DOTALL：允许捕获多行内容，如多行 Finish 答案）
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        # 反馈纠错：解析失败不崩溃、不跳过，而是把错误信息作为 Observation 喂回，
        # 让 LLM 下一轮自己修正格式（把程序错误转化为智能体的学习信号）
        observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "="*40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    # Finish 判断必须在工具解析之前：Finish[...] 不是工具调用，而是任务结束信号
    if action_str.startswith("Finish"):
        # re.DOTALL：最终答案可能是多行 Markdown，.* 必须能跨行
        # （踩坑：两处正则 DOTALL 不一致曾导致 NoneType 崩溃，详见笔记）
        finish_match = re.match(r"Finish\[(.*)\]", action_str, re.DOTALL)
        if finish_match:
            final_answer = finish_match.group(1)
        else:
            # 兜底：模型输出了 Finish 但没带标准括号，去掉前缀后直接作为答案
            final_answer = action_str[6:].strip("[] ")  # 去掉开头的 "Finish"
        print(f"任务完成，最终答案: {final_answer}")
        break

    # 从 action_str 解析出函数名与参数，例如：
    #   'get_weather(city="北京")' → tool_name='get_weather'，kwargs={'city': '北京'}
    tool_name = re.search(r"(\w+)\(", action_str).group(1)   # 函数名：'(' 之前的连续 \w+
    args_str = re.search(r"\((.*)\)", action_str).group(1)   # 括号内的参数串
    # 键值对解析：只支持 key="value" 双引号形式（改进点：单引号/位置参数会解析失败）
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    # 查分发表并执行：字符串函数名 → 真实 Python 函数
    if tool_name in available_tools:
        # 工具内部异常已在工具函数里捕获并转为错误字符串，这里不会中断循环
        observation = available_tools[tool_name](**kwargs)
    else:
        # 模型幻觉出不存在的工具 → 同样作为 Observation 喂回，让模型自己纠正
        observation = f"错误:未定义的工具 '{tool_name}'"

    # --- 3.4 记录观察结果：环境反馈进入历史，闭环完成 ---
    # 下一轮 LLM 将读到这条 Observation，据此产生新的 Thought/Action
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)
