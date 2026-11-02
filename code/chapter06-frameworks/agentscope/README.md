# 第六章：AgentScope 实践

对应教程：

- `/Users/zhangquande/Documents/studyspace/hello-agents/docs/chapter6/第六章 框架开发实践.md`
- `/Users/zhangquande/Documents/studyspace/hello-agents/code/chapter6/AgentScopeDemo/`

## 🎯 学习目标

1. 理解 AgentScope 的消息驱动架构
2. 掌握 `Msg`、`AgentBase`、`ReActAgent` 的关系
3. 理解 `MsgHub` 的消息广播机制
4. 掌握 `sequential_pipeline` 和 `fanout_pipeline`
5. 理解结构化输出对多智能体协作的价值
6. 对比 AgentScope 与 AutoGen 的差异

## 🧭 学习重点

| 概念 | 作用 | 我的理解 |
| ---- | ---- | -------- |
| `Msg` | 统一消息结构 | Agent 之间不是直接函数调用，而是通过消息交互 |
| `AgentBase` | 智能体基类 | 定义智能体生命周期和响应逻辑 |
| `ReActAgent` | 带推理能力的 Agent | 可以围绕模型、系统提示词和结构化输出组织行为 |
| `MsgHub` | 消息中心 | 让一组 Agent 共享消息，适合群聊/讨论 |
| `sequential_pipeline` | 顺序执行多个 Agent | 按“轮流发言”的方式组织协作 |
| `fanout_pipeline` | 并行执行多个 Agent | 适合投票、并行收集意见、并发推理 |
| 结构化输出 | 用 Pydantic 约束行为 | 让 Agent 输出可解析、可验证的数据，而不是自由文本 |

## 🧪 建议实践路线

### 第一阶段：单 Agent 消息

目标：

- 创建一个 Agent
- 发送一条 `Msg`
- 打印 Agent 的回复

产出建议：

```text
agentscope/
├── README.md
├── requirements.txt
└── single_agent_demo.py
```

配置统一放在仓库根目录 `.env`，模板见根目录 `.env.example`。

### 第二阶段：两个 Agent 轮流讨论

目标：

- 创建两个角色不同的 Agent
- 用 `sequential_pipeline` 让它们轮流发言
- 观察消息如何传递

产出建议：

```text
agentscope/
└── sequential_demo.py
```

### 第三阶段：MsgHub 群聊

目标：

- 创建三个 Agent
- 使用 `MsgHub` 建立共享讨论空间
- 观察消息广播效果

产出建议：

```text
agentscope/
└── msg_hub_demo.py
```

### 第四阶段：结构化输出

目标：

- 定义一个 Pydantic 模型，例如：

```python
class VoteModel(BaseModel):
    target: str
    reason: str
    confidence: int
```

- 让多个 Agent 并行投票
- 使用 `fanout_pipeline` 收集结果
- 统计票数

产出建议：

```text
agentscope/
└── vote_demo.py
```

### 第五阶段：简化版三国狼人杀

不要一开始照抄教程完整游戏。当前先做一个可运行的简化版：

- 4 个 Agent
- 角色：1 狼人、1 预言家、2 村民
- 流程：
  1. 狼人夜晚选择击杀目标
  2. 预言家夜晚查验目标
  3. 白天群聊讨论
  4. 全员投票
  5. 输出胜负结果

已实现文件：

```text
agentscope/
├── prompts.py
├── roles.py
├── structured_outputs.py
└── mini_werewolf.py
```

运行：

```bash
.venv/bin/python code/chapter06-frameworks/agentscope/mini_werewolf.py
```

## 🆚 AgentScope 与 AutoGen 的对比

| 维度 | AutoGen | AgentScope |
| ---- | ------- | ---------- |
| 核心抽象 | 多 Agent 对话 | 消息驱动 |
| 协作方式 | 群聊、轮询、角色对话 | `MsgHub`、Pipeline |
| 编排方式 | 对话驱动 | 显式编排与消息路由 |
| 并发能力 | 可以，但主要围绕对话 | 原生异步、并发更明显 |
| 工程化 | 适合原型和协作流程 | 更强调可靠性、分布式、生产环境 |
| 学习难度 | 相对容易 | 稍高，需要理解消息和异步 |

## ✅ 当前任务

先不要实现完整狼人杀。第一步完成：

1. 安装 AgentScope 依赖
2. 创建 `single_agent_demo.py`
3. 使用教程中的 `Msg` 和 `ReActAgent` 概念
4. 让一个 Agent 回复一句话
5. 打印返回结果
6. 观察消息结构

完成后，再进入两个 Agent 轮流对话。

## ⚠️ 版本策略

- 本目录先按 hello-agents 教程使用 **AgentScope 1.0.2**，便于对照教程中的 `Msg`、`ReActAgent`、`MsgHub`、`sequential_pipeline`、`fanout_pipeline`。
- 官方当前文档以 **2.x** 为主，核心 API 已改为 `Agent`、`UserMsg`、`Toolkit`、`GoalPipeline`、`TeamPipeline`，与教程 1.x API 不兼容。
- 不要混用 1.x 与 2.x。建议先完成教程版实践，再另开一个学习分支或目录研究官方 2.x。

## 🔗 相关链接

- 教程原文：第六章 6.3 AgentScope
- 教程示例：`hello-agents/code/chapter6/AgentScopeDemo`
- 官方文档：<https://docs.agentscope.io/>
- 官方 2.0.11 快速开始：<https://docs.agentscope.io/zh/versions/2.0.11/quickstart.md>
- 官方 2.0.11 Agent 概述：<https://docs.agentscope.io/zh/versions/2.0.11/building-blocks/agent/overview.md>
- 官方 2.0.11 Pipeline 概述：<https://docs.agentscope.io/zh/versions/2.0.11/building-blocks/pipeline/overview.md>
