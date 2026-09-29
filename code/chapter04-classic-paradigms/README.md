# 第四章：智能体经典范式构建

对应教程：

- `/Users/zhangquande/Documents/studyspace/hello-agents/docs/chapter4/第四章 智能体经典范式构建.md`
- `/Users/zhangquande/Documents/studyspace/hello-agents/code/chapter4/`

## 学习目标

1. 封装一个可复用的 LLM 客户端
2. 理解 `Thought -> Action -> Observation` 循环
3. 亲手实现最小 ReAct Agent
4. 理解 Plan-and-Solve 的“先规划后执行”
5. 理解 Reflection 的“生成-审查-修正”机制

## 目录结构

```text
code/chapter04-classic-paradigms/
├── README.md
├── requirements.txt
├── .env.example
├── llm_client.py          # 通用 LLM 调用客户端
├── tools.py               # 工具定义与执行器
├── react_agent.py         # ReAct 范式
├── plan_and_solve.py      # Plan-and-Solve 范式
└── reflection.py          # Reflection 范式
```

## 学习顺序

1. 先实现并运行 `llm_client.py`
2. 再实现 `tools.py`，至少准备两个工具
3. 重点实现 `react_agent.py`
4. 之后再学 `plan_and_solve.py`
5. 最后学 `reflection.py`

## 环境配置

复制示例配置：

```bash
cp .env.example .env
```

然后填入真实值。注意 `.env` 不要提交到 Git。
