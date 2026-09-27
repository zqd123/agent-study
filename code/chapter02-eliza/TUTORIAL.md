# 第二章实战：复刻 ELIZA —— 世界上第一个聊天机器人（1966）

> 来源：hello-agents 教程 2.2 节
> 目标：不用任何 LLM，只用正则模式匹配实现一个会"鹦鹉学舌"的 therapist

## ✅ 搭建清单

- [ ] 1. 定义规则库（正则模式 → 响应模板列表）
- [ ] 2. 实现代词转换（you→I，I→you）
- [ ] 3. 实现主聊天循环（匹配 → 反射替换 → 输出）
- [ ] 4. 与 ELIZA 对话 5 轮，记录它的回复
- [ ] 5. 思考题：ELIZA 和第一章的 ReAct 智能体差在哪里？写进笔记

## 💡 动手提示（不含答案）

- 规则库本质就是 `list[(re.compile(模式), [模板1, 模板2])]`
- 代词转换是 ELIZA 的灵魂：用户说 I 时它当成 you 来反射
- 思考题提示：ELIZA 有没有"感知→思考→行动"的闭环？它的 Thought 是真的吗？

---

## 📖 教程原文（2.2 节全文）

## 2.2 构建基于规则的聊天机器人

在探讨了符号主义的理论挑战后，本节我们将通过一个具体的编程实践，来直观地感受基于规则的系统是如何工作的。我们将尝试复现人工智能历史上一个极具影响力的早期聊天机器人——ELIZA。

### 2.2.1 ELIZA 的设计思想

ELIZA是由麻省理工学院的计算机科学家<strong>约瑟夫·魏泽鲍姆（Joseph Weizenbaum）</strong>于1966年发布的一个计算机程序<sup>[6]</sup>，是早期自然语言处理领域的著名尝试之一。ELIZA并非一个单一的程序，而是一个可以执行不同“脚本”的框架。其中，最广为人知也最成功的脚本是“DOCTOR”，它模仿了一位罗杰斯学派的非指导性心理治疗师。

ELIZA的工作方式极其巧妙：它从不正面回答问题或提供信息，而是通过识别用户输入中的关键词，然后应用一套预设的转换规则，将用户的陈述转化为一个开放式的提问。例如，当用户说“我为我的男朋友感到难过”时，ELIZA可能会识别出关键词“我为……感到难过”，并应用规则生成回应：“你为什么会为你的男朋友感到难过？”

魏泽鲍姆的设计思想并非要创造一个真正能够“理解”人类情感的智能体，恰恰相反，他想证明的是，通过一些简单的句式转换技巧，机器可以在完全不理解对话内容的情况下，营造出一种“智能”和“共情”的假象。然而，出乎他意料的是，许多与ELIZA交互过的人（包括他的秘书）都对其产生了情感上的依赖，深信它能够理解自己。

本节的实践目标即为复现ELIZA的核心机制，以深入理解这种规则驱动方法的优势与根本局限。

### 2.2.2 模式匹配与文本替换

ELIZA的算法流程基于<strong>模式匹配（Pattern Matching）与文本替换（Text Substitution）</strong>，可被清晰地分解为以下四个步骤：

1. <strong>关键词识别与排序：</strong>规则库为每个关键词（如 `mother`, `dreamed`, `depressed`）设定一个优先级。当输入包含多个关键词时，程序会选择优先级最高的关键词所对应的规则进行处理。
2. <strong>分解规则：</strong>找到关键词后，程序使用带通配符（`*`）的分解规则来捕获句子的其余部分。
   1. <strong>规则示例</strong>： `* my *`
   2. <strong>用户输入</strong>： `"My mother is afraid of me"`
   3. <strong>捕获结果</strong>： `["", "mother is afraid of me"]`
3. <strong>重组规则：</strong>程序从与分解规则关联的一组重组规则中，选择一条来生成回应（通常随机选择以增加多样性），并可选择性地使用上一步捕获的内容。
   1. <strong>规则示例</strong>： `"Tell me more about your family."`
   2. <strong>生成输出</strong>： `"Tell me more about your family."`
4. <strong>代词转换：</strong>在重组前，程序会进行简单的代词转换（如 `I` → `you`, `my` → `your`），以维持对话的连贯性。

整个工作流程可以用一个简单的伪代码思路来表示：

```Python
FUNCTION generate_response(user_input):
    // 1. 将用户输入拆分成单词
    words = SPLIT(user_input)

    // 2. 寻找优先级最高的关键词规则
    best_rule = FIND_BEST_RULE(words)
    IF best_rule is NULL:
        RETURN a_generic_response() // 例如:"Please go on."

    // 3. 使用规则分解用户输入
    decomposed_parts = DECOMPOSE(user_input, best_rule.decomposition_pattern)
    IF decomposition_failed:
        RETURN a_generic_response()

    // 4. 对分解出的部分进行代词转换
    transformed_parts = TRANSFORM_PRONOUNS(decomposed_parts)

    // 5. 使用重组规则生成回应
    response = REASSEMBLE(transformed_parts, best_rule.reassembly_patterns)

    RETURN response
```

通过这套机制，ELIZA成功地将复杂的自然语言理解问题，简化为了一个可操作的、基于规则的模式匹配游戏。

### 2.2.3 核心逻辑的实现

现在，我们将上一节描述的技术原理转化为一个简单的、可运行的Python函数。下面的代码实现了一个迷你版的ELIZA，它包含了一小部分规则，但足以展示其核心工作机制。

```Python
import re
import random

# 定义规则库:模式(正则表达式) -> 响应模板列表
rules = {
    r'I need (.*)': [
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "Are you sure you need {0}?"
    ],
    r'Why don\'t you (.*)\?': [
        "Do you really think I don't {0}?",
        "Perhaps eventually I will {0}.",
        "Do you really want me to {0}?"
    ],
    r'Why can\'t I (.*)\?': [
        "Do you think you should be able to {0}?",
        "If you could {0}, what would you do?",
        "I don't know -- why can't you {0}?"
    ],
    r'I am (.*)': [
        "Did you come to me because you are {0}?",
        "How long have you been {0}?",
        "How do you feel about being {0}?"
    ],
    r'.* mother .*': [
        "Tell me more about your mother.",
        "What was your relationship with your mother like?",
        "How do you feel about your mother?"
    ],
    r'.* father .*': [
        "Tell me more about your father.",
        "How did your father make you feel?",
        "What has your father taught you?"
    ],
    r'.*': [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?"
    ]
}

# 定义代词转换规则
pronoun_swap = {
    "i": "you", "you": "i", "me": "you", "my": "your",
    "am": "are", "are": "am", "was": "were", "i'd": "you would",
    "i've": "you have", "i'll": "you will", "yours": "mine",
    "mine": "yours"
}

def swap_pronouns(phrase):
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    words = phrase.lower().split()
    swapped_words = [pronoun_swap.get(word, word) for word in words]
    return " ".join(swapped_words)

def respond(user_input):
    """
    根据规则库生成响应
    """
    for pattern, responses in rules.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            # 捕获匹配到的部分
            captured_group = match.group(1) if match.groups() else ''
            # 进行代词转换
            swapped_group = swap_pronouns(captured_group)
            # 从模板中随机选择一个并格式化
            response = random.choice(responses).format(swapped_group)
            return response
    # 如果没有匹配任何特定规则，使用最后的通配符规则
    return random.choice(rules[r'.*'])

# 主聊天循环
if __name__ == '__main__':
    print("Therapist: Hello! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Therapist: Goodbye. It was nice talking to you.")
            break
        response = respond(user_input)
        print(f"Therapist: {response}")
        
>>>
Therapist: Hello! How can I help you today?
You: I am feeling sad today.
Therapist: How long have you been feeling sad today?
You: I need some help with my project.
Therapist: Are you sure you need some help with your project?
You: My mother is not happy with my work.
Therapist: Tell me more about your mother.
You: quit
Therapist: Goodbye. It was nice talking to you.
```

通过上述的编程实践，我们可以直观地总结出规则驱动系统的根本局限性，这些局限正是对 `2.1.4` 节中符号主义理论挑战的直接印证：

- <strong>缺乏语义理解</strong>：系统不理解词义。例如，面对“I am <strong>not</strong> happy”的输入，它仍会机械地匹配 `I am (.*)` 规则并生成语义不通的回应，因为它无法理解否定词“not”的作用。
- <strong>无上下文记忆</strong>：系统是<strong>无状态的（Stateless）</strong>，每次回应仅基于当前单句输入，无法进行连贯的多轮对话。
- <strong>规则的扩展性问题</strong>：尝试增加更多规则会导致规则库的规模爆炸式增长，规则间的冲突与优先级管理将变得极其复杂，最终导致系统难以维护。

然而，尽管存在这些显而易见的缺陷，ELIZA在当时却产生了著名的“<strong>ELIZA效应</strong>”，许多用户相信它能理解自己。这种智能的幻觉主要源于其巧妙的对话策略（如扮演被动的提问者、使用开放式模板）以及人类天生的情感投射心理。

ELIZA的实践清晰地揭示了符号主义方法的核心矛盾：系统看似智能的表现，完全依赖于设计者预先编码的规则。然而，面对真实世界语言的无限可能性，这种穷举式的方法注定不可扩展。系统没有真正的理解，只是在执行符号操作，这正是其脆弱性的根源。

## 2.3 马文·明斯基的心智社会
