"""多源搜索工具 —— 对应教程 7.5.3

教程做法：MyAdvancedSearchTool 类，按环境变量自动启用搜索源：
  - TAVILY_API_KEY  -> tavily.TavilyClient，search(query, max_results=3)
  - SERPAPI_API_KEY -> serpapi.GoogleSearch
搜索时按顺序尝试各源，取第一个有效结果；全部失败返回错误提示。
注册名 "advanced_search"。

你本地 .env 只有 TAVILY_API_KEY，实现 Tavily 分支即可跑通。

TODO(7.5.3): 参考教程 my_advanced_search.py 实现
  - MyAdvancedSearchTool.__init__        name/description/_setup_search_sources()
  - _setup_search_sources()              检测环境变量并创建客户端
  - search(query: str) -> str            空查询提示 -> 逐源尝试 -> 失败兜底提示
  - _search_with_tavily(query) -> str    response['answer'] + results 前3条
  - create_advanced_search_registry() -> ToolRegistry
      注册 name="advanced_search"，func=search_tool.search
"""
