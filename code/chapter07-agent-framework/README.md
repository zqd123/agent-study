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

### 7.2.1 多提供商支持（已完成 ✅）

**实现**：`core/my_llm.py`，`MyLLM(HelloAgentsLLM)` 继承扩展
- 拦截 `provider="modelscope"`：自己解析 `MODELSCOPE_API_KEY` → 校验 → 设默认参数 → 建 OpenAI 客户端
- 其他 provider 走 `super().__init__()`，`think()`/`invoke()` 直接继承
- 验收：父类路径（digiwin .env）invoke 正常；modelscope 无密钥时正确抛 ValueError

**实测踩坑记录（错误码分层排查）**：

| 错误码 | 真实原因 | 解法 |
|---|---|---|
| 401 Authentication failed | 拿 digiwin 的 key 冒充 MODELSCOPE_API_KEY —— 改变量名不改变 key 的身份 | 申请真正的 ModelScope key |
| 400 no provider supported | 教程默认模型 `Qwen/Qwen2.5-VL-72B-Instruct` 已下架（ModelScope 模型目录已换代） | 显式传 `model="Qwen/Qwen3.5-27B"` |
| 403 complete your profile | 账号未完成邮箱验证，推理服务对所有模型 403 | modelscope.cn/my/settings/account 完成验证 |

**经验教训**：
1. **一把钥匙开一把锁**——把 A 服务的 key 改名成 B 服务的变量名，不会让它变成 B 的 key
2. **错误码分层解读**：401=身份错、400=资源不存在、403=身份对但权限不足；比笼统的"报错了"信息量大得多
3. **模型列表有欺骗性**：`/v1/models` 返回 37 个 ≠ 都能调，以实测为准（部分模型上架未开通推理）
4. **教程代码会过时**：教程写死的模型 ID 一年后可能下架，生产代码默认值要可覆盖
5. 继承扩展的价值在排查中体现：拦截分支只改凭证解析，请求链路（URL/模型/流式）全部复用父类

**最终验证**（2026-11-04）：
```
MyLLM(provider="modelscope", model="Qwen/Qwen3.5-27B")
→ invoke 正常返回通义千问自我介绍
```
