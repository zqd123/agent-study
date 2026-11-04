from dotenv import load_dotenv
# 导入我们封装的LLM
from my_llm import MyLLM

# 加载环境变量
load_dotenv()

# 实例化我们重写的客户端，并指定provider
llm = MyLLM(
    provider="modelscope",
    model="Qwen/Qwen3.5-27B",   # 教程默认的 Qwen2.5-VL 已下架
)

# 准备消息

message = [{"role":"user","content":"你好，请介绍一下你自己。"}]

# 发起调用，think等方法都从父类继承，无需重写
response_stream = llm.think(message)
print("模型回复：")
for chunk in response_stream:
    pass