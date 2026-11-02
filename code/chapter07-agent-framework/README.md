# 第七章：构建你的 Agent 框架

> 教程：`hello-agents/docs/chapter7/第七章 构建你的Agent框架.md`
> 配套源码：`hello-agents/code/chapter7/`

## 本章目标

从"框架使用者"跃迁为"框架构建者"：

1. 理解为什么自建框架（对比 LangChain 等的痛点）
2. 实现 HelloAgents 框架的核心组件（LLM 统一接口、消息、配置、Agent 基类）
3. 把第四章的四大范式（Simple / ReAct / Reflection / Plan-and-Solve）框架化
4. 实现工具系统（基类、注册机制、自定义工具、多源搜索）

## 两条学习路径（教程建议"先体验，后实现"）

- **体验式**：直接 `pip install hello-agents==0.1.1`（已安装），运行示例
- **深度式**：跟随本章，在本目录从零实现每个组件，用教程的 test_*.py 验证

## 学习顺序

```text
7.1 框架整体架构设计（理念，不用写代码）
  ↓
7.2 HelloAgentsLLM 扩展
    - 多提供商支持（7.2.1）
    - 本地模型调用（7.2.2，了解即可）
    - 自动检测机制（7.2.3）
  ↓
7.3 框架接口实现
    - Message 类（7.3.1）
    - Config 类（7.3.2）
    - Agent 抽象基类（7.3.3）
  ↓
7.4 Agent 范式的框架化实现
    - SimpleAgent（7.4.1）
    - ReActAgent（7.4.2）
    - ReflectionAgent（7.4.3）
    - PlanAndSolveAgent（7.4.4）
    - FunctionCallAgent（7.4.5）
  ↓
7.5 工具系统
    - 工具基类与注册机制（7.5.1）
    - 自定义工具：计算器（7.5.2）
    - 多源搜索工具（7.5.3）
    - 高级特性：工具链 + 异步执行（7.5.4，选学）
  ↓
7.6 小结与习题
```

## 目录结构（对应教程 7.1.3 蓝图）

```text
code/chapter07-agent-framework/
├── README.md
├── requirements.txt
├── core/                     # 核心框架层
│   ├── llm.py                # 7.2 LLM 统一接口
│   ├── message.py            # 7.3.1 消息系统
│   ├── config.py             # 7.3.2 配置管理
│   └── agent.py              # 7.3.3 Agent 抽象基类
├── agents/                   # Agent 实现层
│   ├── simple_agent.py       # 7.4.1
│   ├── react_agent.py        # 7.4.2
│   ├── reflection_agent.py   # 7.4.3
│   ├── plan_solve_agent.py   # 7.4.4
│   └── function_call_agent.py# 7.4.5
├── tools/                    # 工具系统层
│   ├── base.py               # 7.5.1 工具基类与注册
│   ├── calculator.py         # 7.5.2 计算工具
│   └── search.py             # 7.5.3 多源搜索工具
└── tests/                    # 测试（参考教程 test_*.py）
```

## 环境说明

- 已安装 `hello-agents==0.1.1`（体验式学习用）
- 自研实现复用根目录 `.env`（`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_ID`）
- `HelloAgentsLLM` 自动检测机制兼容 OpenAI 接口，无需额外配置

## 学习笔记

### 7.1 为什么自建框架（要点）

- 现成框架的痛点：过度抽象、API 迭代快、黑盒化、依赖重
- 自建的价值：深度理解原理 + 完全控制权 + 系统设计能力
- HelloAgents 设计理念：轻量级、基于 OpenAI 标准 API、统一工具抽象

（后续笔记按小节补充…）
