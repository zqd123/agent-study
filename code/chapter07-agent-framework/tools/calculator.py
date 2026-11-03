"""计算工具 —— 对应教程 7.5.2

教程做法：用 ast 安全地解析表达式（不用 eval），支持
  四则运算 + - * /、sqrt() 函数、pi 常量
然后通过 register_function 注册成名为 "my_calculator" 的工具。

TODO(7.5.2): 参考教程 my_calculator_tool.py 实现
  - my_calculate(expression: str) -> str
      空表达式返回提示；解析失败返回 "计算失败，请检查表达式格式"
  - _eval_node(node, operators, functions)  递归求值
  - create_calculator_registry() -> ToolRegistry
      注册 name="my_calculator"，
      description="简单的数学计算工具，支持基本运算(+,-,*,/)和sqrt函数"
"""
