"""第六章 6.5.2：三步问答助手代码骨架。

结构对齐教程中的三步流程：

    START -> understand -> search -> answer -> END
"""

# 教程中用于读取 .env 配置
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from tavily import TavilyClient

# 教程在模块加载时读取环境变量
load_dotenv()

#  按教程初始化全局 llm 和 tavily_client
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID", "gpt-4o-mini"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0.7,
)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


class SearchState(TypedDict):
    """LangGraph 全局状态。"""

    # 教程使用 messages 作为消息历史的字段名
    messages: Annotated[list, add_messages]

    # 经过 LLM 理解后的用户需求总结
    user_query: str

    # 优化后用于 Tavily API 的搜索查询
    search_query: str

    # Tavily 搜索返回的结果
    search_results: str

    # 最终生成的答案
    final_answer: str

    # 标记当前步骤
    step: str


def understand_query_node(state: SearchState) -> dict:
    """教程步骤 1：理解用户查询并生成搜索关键词。"""
    user_message = state["messages"][-1].content
    understand_prompt = f"""分析用户的查询："{user_message}"
请完成两个任务：
1. 简洁总结用户想要了解什么
2. 生成最适合搜索引擎的关键词（中英文均可，要精准）

格式：
理解：[用户需求总结]
搜索词：[最佳搜索关键词]"""
    response = llm.invoke([SystemMessage(content=understand_prompt)])
    response_text = response.content
    print("\n🧠 理解阶段:", response_text)
    # 解析LLM的输出，提取搜索关键词
    search_query = user_message  # 默认使用原始查询
    if "搜索词" in response_text:
        search_query = response_text.split("搜索词：")[1].strip()
    return {
        "user_query": response_text,
        "search_query": search_query,
        "step": "understood",
        "messages": [AIMessage(content=f"我将为您搜索：{search_query}")],
    }
    pass


def _format_search_results(response: dict) -> str:
    """把 Tavily 返回结果整理成适合 LLM 阅读的文本。"""
    parts = []

    if response.get("answer"):
        parts.append(f"搜索摘要：{response['answer']}")

    results = response.get("results", [])
    for index, item in enumerate(results, start=1):
        title = item.get("title", "")
        url = item.get("url", "")
        content = item.get("content", "")

        part = f"{index}. {title}\n{url}\n{content}".strip()
        parts.append(part)

    return "\n\n".join(parts) if parts else "没有找到有效搜索结果。"


def tavily_search_node(state: SearchState) -> dict:
    """步骤2：使用Tavily API进行真实搜索"""
    search_query = state["search_query"]
    try:
        print(f"🔍 正在搜索: {search_query}")
        response = tavily_client.search(
            query=search_query, search_depth="basic", max_results=5, include_answer=True
        )
        # ... (处理和格式化搜索结果) ...
        search_results = _format_search_results(response)  # 格式化后的结果字符串
        print(f"🔍 搜索阶段: {search_results}")
        return {
            "search_results": search_results,
            "step": "searched",
            "messages": [AIMessage(content="✅ 搜索完成！正在整理答案...")],
        }
    except Exception as e:
        # ... (处理错误) ...
        return {
            "search_results": f"搜索失败：{e}",
            "step": "search_failed",
            "messages": [AIMessage(content="❌ 搜索遇到问题...")],
        }


def generate_answer_node(state: SearchState) -> dict:
    """教程步骤 3：基于搜索结果生成最终答案。"""
    if state["step"] == "search_failed":
        # 如果搜索失败，执行回退策略，基于LLM自身知识回答
        fallback_prompt = f"搜索API暂时不可用，请基于您的知识回答用户的问题：\n用户问题：{state['user_query']}"
        response = llm.invoke([SystemMessage(content=fallback_prompt)])
    else:
        # 搜索成功，基于搜索结果生成答案
        answer_prompt = f"""基于以下搜索结果为用户提供完整、准确的答案：
    用户问题：{state["user_query"]}
    搜索结果：\n{state["search_results"]}
    请综合搜索结果，提供准确、有用的回答..."""
        response = llm.invoke([SystemMessage(content=answer_prompt)])

    return {
        "final_answer": response.content,
        "step": "completed",
        "messages": [AIMessage(content=response.content)],
    }


# 将所有节点连接起来，构建图
def create_search_assistant():
    """教程步骤 4：构建三步问答助手的 LangGraph 工作流。"""
    workflow = StateGraph(SearchState)
    # 添加节点
    workflow.add_node("understand", understand_query_node)
    workflow.add_node("search", tavily_search_node)
    workflow.add_node("answer", generate_answer_node)
    # 设置线性流程
    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)

    # 编译图
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app


def main() -> None:
    """教程步骤 5：运行三步问答助手。"""
    app = create_search_assistant()
    print("🔍 智能搜索助手启动！")
    print("流程：理解 -> 搜索 -> 回答")
    print("输入 quit / exit / q 退出\n")
    config = {"configurable": {"thread_id": "three-step-search-assistant"}}

    while True:
        try:
            question = input("🤔 您想了解什么: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not question:
            continue

        if question.lower() in {"q", "quit", "exit"}:
            print("再见！")
            break

        inputs = {
            "messages": [HumanMessage(content=question)],
            "user_query": "",
            "search_query": "",
            "search_results": "",
            "final_answer": "",
            "step": "",
        }

        try:
            result = app.invoke(inputs, config=config)

            print("\n" + "=" * 60)
            print(f"💡 最终回答:\n{result['final_answer']}")
            print("=" * 60 + "\n")

        except Exception as exc:
            print(f"❌ 处理问题时出错：{exc}\n")


if __name__ == "__main__":
    main()
