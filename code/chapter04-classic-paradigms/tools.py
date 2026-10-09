"""
第四章实践：工具定义与执行器

学习目标：
1. 理解一个工具需要 name / description / func
2. 实现 ToolExecutor，负责注册、查找、执行工具
"""

from typing import Dict, Any

class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"⚠️警告：工具 {name} 已存在，将被覆盖。")
        self.tools[name] = {
            "description": description,
            "func": func
        }
        print(f"✅ 工具 {name} 注册成功。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])




# 测试
# if __name__ == "__main__":
#     def mock_search(query: str) -> str:
#         return f"模拟搜索结果：{query}"

#     def mock_weather(city: str) -> str:
#         return f"模拟天气结果：{city} 今天晴，25°C"

#     tool_executor = ToolExecutor()

#     tool_executor.register_tool(
#         name="Search",
#         description="一个搜索工具。当你需要查询实时信息时使用。",
#         func=mock_search
#     )

#     tool_executor.register_tool(
#         name="Weather",
#         description="一个天气查询工具。当你需要查询城市天气时使用。",
#         func=mock_weather
#     )

#     print(tool_executor.getAvailableTools())
#     print(tool_executor.getTool("Weather")("北京"))