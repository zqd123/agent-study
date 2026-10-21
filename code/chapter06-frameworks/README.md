# 第六章：框架开发实践

本章目标：

1. 理解为什么从手写智能体转向使用框架
2. 对比 AutoGen、AgentScope、CAMEL、LangGraph 的设计思想
3. 分别体验每种框架的典型协作模式
4. 重点掌握 LangGraph 的状态图建模方式

## 学习顺序

```text
6.1 框架总览与选型
  ↓
6.2 AutoGen：对话驱动协作
  ↓
6.3 AgentScope：工程化多智能体平台
  ↓
6.4 CAMEL：角色扮演协作
  ↓
6.5 LangGraph：状态图与可控工作流
  ↓
6.6 总结与习题
```

## 目录结构

```text
code/chapter06-frameworks/
├── README.md
├── autogen/       # AutoGen 实践
├── agentscope/    # AgentScope 实践
├── camel/         # CAMEL 实践
└── langgraph/     # LangGraph 实践
```

## 框架定位

| 框架 | 核心思想 | 适合场景 |
| --- | --- | --- |
| AutoGen | 用多角色对话驱动任务协作 | 软件开发、代码审查、多角色讨论 |
| AgentScope | 工程化、消息驱动的多智能体平台 | 高并发、分布式、复杂多智能体系统 |
| CAMEL | 通过角色扮演让智能体自主协作 | 两个专家角色共同完成创作或研究 |
| LangGraph | 用状态图显式建模工作流 | 需要循环、条件分支、可审计流程的应用 |

## 学习重点

1. **AutoGen**
   - 角色 Agent
   - 群聊或轮询协作
   - 用对话推动任务演进

2. **AgentScope**
   - 消息驱动架构
   - 智能体生命周期管理
   - 分布式部署思路

3. **CAMEL**
   - Role-Playing
   - Inception Prompting
   - 双智能体自主协作

4. **LangGraph**
   - `State`
   - `Node`
   - `Edge`
   - Conditional Edge
   - Cycle / Loop

## 环境配置

复制第四章的示例配置：

```bash
cp ../chapter04-classic-paradigms/.env.example .env
```

如果后续使用 LangGraph 的搜索示例，还需要额外配置：

```text
TAVILY_API_KEY=your_tavily_api_key
```

注意 `.env` 不要提交到 Git。
