# -*- coding: utf-8 -*-
"""SimpleAgent（7.4.1）—— 基础对话范式，手写实现。

教程参考：docs/chapter7/第七章.md 7.4.1 节

核心逻辑：
1. run(input) -> 组装 [system_prompt] + 历史 + [user input]
2. 调用 llm.invoke() 得到回复
3. 把 user input 和 assistant 回复都写入历史
"""

from typing import Optional

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM
from core.message import Message


class SimpleAgent(Agent):
    """基础对话 Agent：单轮调用 LLM 并维护历史。"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> None:
        super().__init__(name, llm, system_prompt, config)

    def _build_messages(self, input_text: str) -> list:
        """组装 OpenAI 格式的消息列表。

        TODO:
        1. 若有 system_prompt，先加 {"role": "system", "content": system_prompt}
        2. 加历史消息：[m.to_dict() for m in self.get_history()]
        3. 最后加当前输入 {"role": "user", "content": input_text}
        """
        raise NotImplementedError

    def run(self, input_text: str, **kwargs) -> str:
        """运行 Agent。

        TODO:
        1. messages = self._build_messages(input_text)
        2. response = self.llm.invoke(messages, **kwargs)
        3. self.add_message(Message(input_text, "user"))
        4. self.add_message(Message(response, "assistant"))
        5. return response
        """
        raise NotImplementedError
