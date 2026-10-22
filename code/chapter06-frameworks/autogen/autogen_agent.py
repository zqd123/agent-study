"""AutoGen 多智能体协作示例。

本示例演示如何使用 AutoGen AgentChat 组建一个按固定顺序轮流的团队：
产品经理负责需求分析，工程师负责实现，代码审查员负责质量检查，
用户代理最后等待人类确认是否结束协作。
"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

# 从当前示例目录下的 .env 文件加载模型、API Key 和 Base URL 配置。
load_dotenv()


def create_openai_model_client():
    """创建并配置 OpenAI 兼容模型客户端。

    Returns:
        OpenAIChatCompletionClient: 供所有 AssistantAgent 共用的模型客户端。
    """
    return OpenAIChatCompletionClient(
        model=os.getenv("LLM_MODEL_ID"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        # 当前模型名不是 OpenAI 官方模型名，因此需要显式声明模型能力。
        # 这样 AutoGen 才能正确处理工具调用、JSON 输出等特性。
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
        },
    )


def create_product_manager(model_client):
    """创建产品经理智能体。

    Args:
        model_client: 用于生成回复的模型客户端。

    Returns:
        AssistantAgent: 负责需求分析和任务拆解的智能体。
    """
    system_message = """你是一位经验丰富的产品经理，专门负责软件产品的需求分析和项目规划。

你的核心职责包括：
1. **需求分析**：深入理解用户需求，识别核心功能和边界条件
2. **技术规划**：基于需求制定清晰的技术实现路径
3. **风险评估**：识别潜在的技术风险和用户体验问题
4. **协调沟通**：与工程师和其他团队成员进行有效沟通

当接到开发任务时，请按以下结构进行分析：
1. 需求理解与分析
2. 功能模块划分
3. 技术选型建议
4. 实现优先级排序
5. 验收标准定义

请简洁明了地回应，并在分析完成后说"请工程师开始实现"。"""

    return AssistantAgent(
        name="ProductManager",
        model_client=model_client,
        system_message=system_message,
    )


def create_engineer(model_client):
    """创建软件工程师智能体。

    Args:
        model_client: 用于生成回复的模型客户端。

    Returns:
        AssistantAgent: 负责编写实现方案和示例代码的智能体。
    """
    system_message = """你是一位资深的软件工程师，擅长 Python 开发和 Web 应用构建。

你的技术专长包括：
1. **Python 编程**：熟练掌握 Python 语法和最佳实践
2. **Web 开发**：精通 Streamlit、Flask、Django 等框架
3. **API 集成**：有丰富的第三方 API 集成经验
4. **错误处理**：注重代码的健壮性和异常处理

当收到开发任务时，请：
1. 仔细分析技术需求
2. 选择合适的技术方案
3. 编写完整的代码实现
4. 添加必要的注释和说明
5. 考虑边界情况和异常处理

请提供完整的可运行代码，并在完成后说"请代码审查员检查"。"""

    return AssistantAgent(
        name="Engineer",
        model_client=model_client,
        system_message=system_message,
    )


def create_code_reviewer(model_client):
    """创建代码审查员智能体。

    Args:
        model_client: 用于生成回复的模型客户端。

    Returns:
        AssistantAgent: 负责检查实现质量和给出修改建议的智能体。
    """
    system_message = """你是一位经验丰富的代码审查专家，专注于代码质量和最佳实践。

你的审查重点包括：
1. **代码质量**：检查代码的可读性、可维护性和性能
2. **安全性**：识别潜在的安全漏洞和风险点
3. **最佳实践**：确保代码遵循行业标准和最佳实践
4. **错误处理**：验证异常处理的完整性和合理性

审查流程：
1. 仔细阅读和理解代码逻辑
2. 检查代码规范和最佳实践
3. 识别潜在问题和改进点
4. 提供具体的修改建议
5. 评估代码的整体质量

请提供具体的审查意见，完成后说"代码审查完成，请用户代理测试"。"""

    return AssistantAgent(
        name="CodeReviewer",
        model_client=model_client,
        system_message=system_message,
    )


def create_user_proxy():
    """创建用户代理智能体。

    Returns:
        UserProxyAgent: 人类用户介入协作流程的入口。
    """
    # UserProxyAgent 不会自动执行代码，而是默认等待人类在终端输入反馈。
    # 这里用它接收测试结论；回复中包含 TERMINATE 时，团队协作结束。
    return UserProxyAgent(
        name="UserProxy",
        description="人类用户代理，用于确认测试结果并提供反馈。测试通过后回复 TERMINATE。",
    )


# 创建一次模型客户端，并让多个 AssistantAgent 复用，避免重复初始化 HTTP 客户端。
model_client = create_openai_model_client()

# RoundRobinGroupChat 会按参与者列表顺序循环发言：
# 产品经理 -> 工程师 -> 代码审查员 -> 用户代理 -> 产品经理 ...
team_chat = RoundRobinGroupChat(
    participants=[
        create_product_manager(model_client),
        create_engineer(model_client),
        create_code_reviewer(model_client),
        create_user_proxy(),
    ],
    # 任意消息中包含 TERMINATE 时结束本轮团队协作。
    termination_condition=TextMentionTermination("TERMINATE"),
    # 防止模型持续循环，设置最大轮数作为安全兜底。
    max_turns=20,
)


async def run_software_development_team():
    """运行多智能体软件开发团队。

    Returns:
        TaskResult: 包含团队协作过程和最终状态的结果对象。
    """
    # 定义本次协作要解决的开发任务。
    task = """我们需要开发一个比特币价格显示应用，具体要求如下：
核心功能：
- 实时显示比特币当前价格（USD）
- 显示24小时价格变化趋势（涨跌幅和涨跌额）
- 提供价格刷新功能

技术要求：
- 使用 Streamlit 框架创建 Web 应用
- 界面简洁美观，用户友好
- 添加适当的错误处理和加载状态

请团队协作完成这个任务，从需求分析到最终实现。"""

    # run_stream 返回异步消息流；Console 会实时打印每个智能体的回复。
    result = await Console(team_chat.run_stream(task=task))
    return result


if __name__ == "__main__":
    # 使用 asyncio.run 启动异步团队协作流程。
    asyncio.run(run_software_development_team())
