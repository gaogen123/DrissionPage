import os
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pdd_agent_tools import crawl_pinduoduo

# 设置 DeepSeek API Key
# 注意：在实际生产环境中，建议将 API Key 放在环境变量中以保证安全
os.environ["DEEPSEEK_API_KEY"] = "sk-edebb99b4b1045f19f3dd9c2621b8776"
# DeepSeek API 的基础 URL
BASE_URL = "https://api.deepseek.com"

# 1. 定义工具 (Tools)
# 使用 @tool 装饰器将函数转换为 LangChain 可用的工具
@tool
def search_pdd_tool(keyword: str, quantity: int = 2, need_download: bool = False) -> str:
    """
    搜索拼多多(PDD)上的商品，并返回商品详情，包括价格和评论。
    
    Args:
        keyword: 商品的搜索关键词。
        quantity: 需要采集的商品数量 (默认为 2)。如果用户指定了数量（例如“找5个”），请设置此参数。
        need_download: 是否需要下载商品详情和图片 (默认为 False)。如果用户提到“下载”、“保存详情”或“保存图片”，请将其设置为 True。
    """
    try:
        # 这里调用了 pdd_agent_tools.py 中的实际爬虫函数
        return crawl_pinduoduo(keyword, limit=quantity, enable_download=need_download)
    except Exception as e:
        return f"Error crawling Pinduoduo: {str(e)}"

# 将工具放入列表中，后续绑定到 LLM
tools = [search_pdd_tool]

# 2. 定义状态 (State)
# AgentState 用于在 Graph 的节点之间传递数据
# 这里主要传递聊天消息历史
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. 初始化 LLM (Large Language Model)
# 使用 LangChain 的 ChatOpenAI 接口来适配 DeepSeek 模型
llm = ChatOpenAI(
    model="deepseek-chat", # DeepSeek V3 的模型名称通常是 deepseek-chat
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    openai_api_base=BASE_URL,
    temperature=0 # 设置为 0以获得更确定性的回答
)

# 绑定工具到 LLM
# 这使得 LLM 知道它有哪些工具可用，以及如何调用它们
llm_with_tools = llm.bind_tools(tools)

# 4. 定义节点 (Nodes)
# Agent 节点：负责调用 LLM 进行决策
def agent_node(state: AgentState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

from langgraph.checkpoint.memory import MemorySaver

# 5. 构建图 (Graph)
# 初始化状态图
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("agent", agent_node) # 思考节点
builder.add_node("tools", ToolNode(tools)) # 工具执行节点

# 定义边 (Edges)
# 从起点开始，进入 agent 节点
builder.add_edge(START, "agent")

# 添加条件边
# tools_condition 是一个预构建的条件函数：
# - 如果 LLM 决定调用工具 -> 路由到 "tools" 节点
# - 如果 LLM 决定直接回答 (结束) -> 路由到 END (结束)
builder.add_conditional_edges(
    "agent",
    tools_condition,
)

# 工具执行完后，必须跳回 agent 节点，让 LLM 根据工具结果生成最终回答
builder.add_edge("tools", "agent")

# 初始化内存保存器
memory = MemorySaver()

# 编译图，生成可执行的应用，并配置 checkpointer
graph = builder.compile(checkpointer=memory)

# 6. 运行测试逻辑
if __name__ == "__main__":
    import sys
    
    print("🤖 启动拼多多采集 Agent (Powered by DeepSeek)...")
    
    # 获取用户输入
    # 优先使用命令行参数，如果没有则默认搜索 "妈咪包" (为了方便自动化运行)
    # 用户可以在运行命令时传入参数，例如: python pdd_langgraph_agent.py "机械键盘"
    if len(sys.argv) > 1:
        product_name = sys.argv[1]
    else:
        # 如果是交互式运行，可以取消下面这行的注释使用 input
        # product_name = input("请输入您想搜索的商品名称: ") 
        product_name = "妈咪包"
        
    user_input = f"帮我在拼多多上找一下'{product_name}'，并总结一下价格和用户评价。"
    print(f"👤 用户: {user_input}")
    
    # 初始化状态，作为图的输入
    initial_state = {"messages": [("user", user_input)]}
    
    try:
        # 运行图并流式输出结果
        # event 包含每一步的状态更新
        for event in graph.stream(initial_state):
            for value in event.values():
                if "messages" in value:
                    # 打印最新的消息内容 (通常是 Agent 的回复)
                    print(f"🤖 Agent: {value['messages'][-1].content}")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
