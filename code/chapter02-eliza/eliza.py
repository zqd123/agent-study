"""
第二章实战：中文版 ELIZA

代码结构和教程 2.2.3 节保持一致：
1. rules 字典
2. pronoun_swap 字典
3. swap_pronouns 函数
4. respond 函数
5. 主聊天循环

中文和英文的差异：
- 英文按空格分词后替换代词；中文没有天然空格，
  所以这里用一次正则替换，避免“我的 -> 你的”再被“你 -> 我”改坏。
- 中文规则使用“妈妈/母亲”“爸爸/父亲”这类同义词。
"""

import re
import random

# 定义规则库: 模式(正则表达式) -> 响应模板列表
rules = {
    r'我需要(.*)': [
        "你为什么需要{0}？",
        "得到{0}真的会对你有帮助吗？",
        "你确定你需要{0}吗？"
    ],
    r'你为什么不(.*)': [
        "你觉得我真的不会{0}吗？",
        "也许我以后会{0}。",
        "你真的想让我{0}吗？"
    ],
    r'为什么我不能(.*)': [
        "你认为你应该能够{0}吗？",
        "如果你能{0}，你会做什么？",
        "我不知道——为什么你不能{0}呢？"
    ],
    r'^我(?:是|感到|很)(.*)': [
        "你来找我是因为你是{0}吗？",
        "你{0}多久了？",
        "对于{0}，你有什么感受？"
    ],
    r'.*(?:妈妈|母亲).*': [
        "多说说你的妈妈。",
        "你和妈妈的关系怎么样？",
        "你对妈妈有什么感受？"
    ],
    r'.*(?:爸爸|父亲).*': [
        "多说说你的爸爸。",
        "你的爸爸让你有什么感受？",
        "你的爸爸教会了你什么？"
    ],
    r'.*': [
        "请告诉我更多。",
        "我们换个话题吧……说说你的家庭。",
        "能展开说说吗？"
    ]
}

# 定义代词转换规则
pronoun_swap = {
    "我的": "你的", "你的": "我的",
    "我们": "你们", "你们": "我们",
    "我": "你", "你": "我",
}

# 中文没有空格，不能像教程一样按单词 split。
# 这里按长度倒序构建一次性的替换正则，保证“我的/你的”优先于“我/你”。
_PATTERNS = sorted(pronoun_swap, key=len, reverse=True)
_SWAP_RE = re.compile("|".join(re.escape(pattern) for pattern in _PATTERNS))


def swap_pronouns(phrase):
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    return _SWAP_RE.sub(lambda match: pronoun_swap[match.group(0)], phrase)


def respond(user_input):
    """
    根据规则库生成响应
    """
    for pattern, responses in rules.items():
        match = re.search(pattern, user_input)
        if match:
            # 捕获匹配到的部分；无捕获组时返回空字符串
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
    print("Therapist: 你好！今天想聊点什么？")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye", "退出"]:
            print("Therapist: 再见，和你聊天很愉快。")
            break
        response = respond(user_input)
        print(f"Therapist: {response}")
