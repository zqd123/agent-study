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

## 学习总结

### 当前完成情况

- ✅ `llm_client.py`：封装了兼容 OpenAI Chat Completions 的流式 LLM 客户端
- ✅ `tools.py`：实现了工具注册、工具描述和统一执行入口
- ✅ `react_agent.py`：实现最小 ReAct 循环
- ✅ `plan_and_solve.py`：实现先规划、后执行的 Plan-and-Solve 流程
- ✅ `reflection.py`：实现生成、反思、优化的 Reflection 循环

### 三种范式的核心差异

| 范式 | 核心循环 | 关键点 | 适用场景 |
| --- | --- | --- | --- |
| ReAct | `Thought -> Action -> Observation -> ... -> Finish` | LLM 决定调用哪个工具，工具结果作为 Observation 写回历史 | 需要外部工具、实时信息或分步推理的问题 |
| Plan-and-Solve | `规划 -> 按步骤执行 -> 汇总结果` | 先生成完整计划，再逐步执行计划中的子任务 | 目标明确、可以提前拆解成多个步骤的问题 |
| Reflection | `生成 -> 反思 -> 优化 -> ... -> 无需改进` | 用短期记忆保存历史尝试和反馈，让模型持续改进自己的输出 | 对答案质量要求高、可以接受多次模型调用的任务 |

### 关键实现要点

1. **统一 LLM 调用协议**

   所有范式都通过 `HelloAgentsLLM.think()` 调用模型，调用参数使用：

   ```python
   messages = [{"role": "user", "content": prompt}]
   response = llm_client.think(message=messages)
   ```

   这里需要特别注意：

   - `think()` 的参数名是 `message`
   - OpenAI 接口期望的 `messages` 是一个列表
   - 单条消息不能直接写成 `{"role": "user", "content": prompt}`

2. **ReAct 的核心是结构化解析**

   ReAct 要求模型输出固定格式：

   ```text
   Thought: ...
   Action: ...
   ```

   代码通过正则解析 `Thought` 和 `Action`，再根据 `Action` 调用工具或进入 `Finish[最终答案]` 结束循环。

3. **Plan-and-Solve 的核心是先拆解再执行**

   `Planner` 先让模型生成一个 Python 列表格式的计划，然后使用 `ast.literal_eval()` 做安全解析。
   `Executor` 按顺序执行每个步骤，并把历史步骤结果继续带入后续提示词。

4. **Reflection 的核心是短期记忆**

   `Memory` 按 `execution` 和 `reflection` 记录：

   - `execution`：某次生成的代码或答案
   - `reflection`：模型对当前结果的反思维度反馈

   `ReflectionAgent` 每轮都取最近一次执行结果进行反思。如果反馈中包含“无需改进”，则提前结束；否则根据反馈生成优化版本。

### 调试经验

学习过程中遇到并修复了两个典型问题：

1. `think() got an unexpected keyword argument 'messages'`

   原因是调用方使用了 `messages=messages`，但 `HelloAgentsLLM.think()` 定义的参数名是 `message`。

2. OpenAI 兼容服务返回：

   ```text
   json: cannot unmarshal object into Go struct field ***.messages of type []***.Message
   ```

   原因是把单条消息 dict 直接传给了 `messages`。正确结构应该是：

   ```python
   [{"role": "user", "content": prompt}]
   ```

### 运行方式

进入本目录：

```bash
cd code/chapter04-classic-paradigms
```

分别运行：

```bash
python3 llm_client.py
python3 react_agent.py
python3 plan_and_solve.py
python3 reflection.py
```

注意：这些脚本会读取 `.env` 中的真实模型配置，并可能调用真实 LLM 服务。

### 后续可优化点

1. Reflection 中，重复调用 `run()` 时可以先清空 `Memory`
2. LLM 调用失败时，可以在关键流程中提前终止，而不是继续把空字符串送入下一轮
3. Reflection 提示词中可以移除教程遗留的 `<strong>` HTML 标签
4. ReAct 的 Action 解析可以继续增强，兼容更多模型输出风格
5. Plan-and-Solve 可以补充异常情况处理，例如计划为空、单步执行失败、模型输出不稳定等场景
