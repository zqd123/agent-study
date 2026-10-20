# 第四章 智能体经典范式构建

> 对应教程：`hello-agents/docs/chapter4/第四章 智能体经典范式构建.md`
> 学习日期：2026-10-20
> 状态：已完成 ✅

## 🎯 本章目标

- 封装一个可复用的 LLM 客户端，并从 `.env` 读取模型配置
- 理解并亲手实现 ReAct 的 `Thought -> Action -> Observation` 循环
- 掌握 Plan-and-Solve 的“先规划、后执行”流程
- 掌握 Reflection 的“生成、反思、优化”循环
- 能根据任务特点选择合适的 Agent 范式

## 📖 核心概念

| 概念 | 解释 | 我的理解 |
| ---- | ---- | -------- |
| 通用 LLM 客户端 | 统一封装模型配置、API 地址、密钥、超时和流式调用 | 后续所有 Agent 复用同一个 `think()`，避免到处复制调用代码 |
| 工具（Tool） | Agent 可以调用的外部能力，如搜索、天气查询、计算器 | LLM 是“大脑”，工具是“手和脚”；工具结果必须变成模型能理解的 Observation |
| ToolExecutor | 负责注册工具、保存工具描述、按名称找到执行函数 | 相当于工具箱 + 调度器，让 ReAct 不需要硬编码 `if action == ...` |
| ReAct | Reason + Act，核心循环是 `Thought -> Action -> Observation -> ... -> Finish` | 模型边推理边行动；Observation 又作为下一轮推理的事实依据 |
| Thought | 智能体的显式思考，用来分析任务、选择工具、判断是否完成 | 高可解释性的关键，调试时优先看这里 |
| Action | 智能体决定执行的动作，如 `Weather[北京]` 或 `Finish[最终答案]` | 需要严格解析，并防御模型输出的 Markdown、反引号、多行文本 |
| Observation | Action 的执行结果，会被写回历史 | 相当于环境反馈；好的 Observation 应简洁、可读、无无关噪声 |
| Plan-and-Solve | 先让 LLM 生成完整计划，再逐步执行计划 | 适合步骤清晰、逻辑路径相对确定的任务 |
| Planner / Executor | 规划器负责拆解任务，执行器按顺序完成子任务并维护历史状态 | 拆解和执行解耦，便于观察每一步的结果 |
| Reflection | 生成初版结果后，让 LLM 审查，再根据反馈优化 | “以成本换质量”；需要短期记忆保存历史尝试和反馈 |
| 短期记忆（Memory） | 保存 `execution` 和 `reflection` 记录 | 没有记忆就无法基于上一轮结果继续优化 |

## 🔑 关键要点

1. **统一 LLM 调用协议很重要**：`HelloAgentsLLM.think(message=messages)` 接收的是消息列表，不是单条 dict。调用方传错参数名或结构，都会导致运行时错误。
2. **ReAct 的本质是“推理指导行动，行动修正推理”**：`Thought` 负责规划，`Action` 负责调用工具，`Observation` 负责回填事实，循环直到模型判断可以 `Finish`。
3. **Agent 输出解析必须防御式设计**：模型可能输出反引号、星号、中文括号，也可能在 `Finish[...]` 中写多行 Markdown。解析器应兼容这些情况，并在格式异常时给回 Observation，而不是直接崩溃。
4. **历史记录驱动下一轮推理**：每次工具执行后，都要把 `Action` 和 `Observation` 写回上下文，模型才能基于最新事实继续决策。
5. **Plan-and-Solve 适合可拆解任务**：Planner 输出结构化计划，Executor 按顺序执行，并把历史步骤结果继续带入后续提示词，形成状态管理。
6. **Reflection 的关键是迭代质量与成本的平衡**：每轮至少额外调用反思和优化模型，能提升质量，但会显著增加耗时和 token 成本。
7. **三种范式没有绝对优劣**：需要实时外部信息选 ReAct；任务路径清晰、可提前拆解选 Plan-and-Solve；对质量要求高且允许更高延迟选 Reflection。

## 💻 实践记录

- 对应代码：`code/chapter04-classic-paradigms/`
- 实现文件：

  - `llm_client.py`：通用 LLM 客户端，读取 `.env`，封装流式响应
  - `tools.py`：工具注册、工具描述、按名称获取执行函数
  - `react_agent.py`：最小 ReAct Agent
  - `plan_and_solve.py`：Planner、Executor、Plan-and-Solve Agent
  - `reflection.py`：Memory、ReflectionAgent

- 运行与验证：

  - ReAct 范式已运行通过
  - 本次使用系统 Python 3.9 做语法检查，五个文件均通过 `py_compile`
  - 使用 stub/mock 做逻辑级测试：ReAct 多行 `Finish[...]` 解析、Plan-and-Solve 计划解析、Reflection 记忆取最新执行记录均通过
  - 后续已切换到项目级 Python 3.12.12，并在第四章目录重建 `.venv`，安装了 `requirements.txt` 中的依赖

- 踩过的坑：

  1. **`think()` 参数名不一致**
     - 教程示例和自研客户端之间存在 `messages=...` / `message=...` 差异
     - 调用方必须与 `HelloAgentsLLM.think()` 的实际参数名保持一致
  2. **消息结构传错**
     - OpenAI Chat Completions 需要 `messages` 是列表
     - 不能直接传单条 dict，否则兼容服务可能报 `json: cannot unmarshal object into Go struct field ... messages`
  3. **多行 `Finish[...]` 解析失败**
     - 现象：最终答案含多行 Markdown 时，`Finish[...]` 跨行，旧正则无法匹配，返回 `None`
     - 根因：正则没有可靠处理换行和闭合括号
     - 修复：使用 `re.DOTALL`，兼容反引号、星号、中英文括号，并增加空值保护
  4. **Python 3.9 不支持 f-string 内嵌同种双引号**
     - `f"{record["content"]}"` 在当前系统 Python 3.9 下直接语法错误
     - 已改为 `f"{record['content']}"`
  5. **Reflection 提示词中的教程遗留 HTML 标签**
     - 已把 `<strong>算法效率</strong>` 改成 Markdown 风格的 `**算法效率**`，让提示词更自然

## ❓ 疑问与思考

- Reflection 很适合高质量代码生成，但多轮调用成本高。以后可以尝试：先让模型输出置信度，低置信时才进入反思；或设置“满足关键标准即停止”。
- Plan-and-Solve 目前是“一次规划、逐步执行”。如果中间某一步失败，是否应该允许 Planner 重新规划？后续可以尝试加入 replanning。
- ReAct 的历史会不断增长。长任务中需要考虑上下文压缩、只保留关键 Observation，或引入外部记忆。
- 本章是单智能体范式，第五章之后可以在这些范式之上叠加工具生态、框架能力和多智能体协作。

## 🔗 相关链接

- 教程原文：`hello-agents/docs/chapter4/第四章 智能体经典范式构建.md`
- 教程代码：`hello-agents/code/chapter4/`
- 在线阅读：https://datawhalechina.github.io/hello-agents/
- 下一章预告：第五章 低代码平台搭建
