# agent.py
import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

# ========== 配置服务器启动参数（显式传递环境变量） ==========
from mcp.client.stdio import get_default_environment

server_params = StdioServerParameters(
    command="D:/conda_envs/paper_agent_cpu/python.exe",
    args=["D:/Appt/大三下/学习/langchain_agent/mcp_server.py"],
    env={
        **get_default_environment(),
        "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY"),
        "PYTHONIOENCODING": "utf-8",
    }
)

# ========== 初始化 LLM ==========
llm = ChatOpenAI(
    model="qwen3.5-flash",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=60,
    max_retries=2
)

# ========== 创建 MCP 客户端 Agent ==========
async def create_mcp_agent():
    """创建并返回一个连接了MCP服务器的Agent"""
    try:
        # 建立与 MCP 服务器的连接
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化会话，设置超时防止卡死
                await asyncio.wait_for(session.initialize(), timeout=30.0)
                # 加载服务器提供的工具
                tools = await load_mcp_tools(session)
                # 创建 ReAct Agent
                agent = create_react_agent(
                    model=llm,
                    tools=tools,
                    prompt=(
                        "你是一个具有长期记忆的智能研究助手。"
                        "你可以使用以下工具："
                        "- save_to_memory: 将问答结果存入记忆库。"
                        "- retrieve_memory: 从历史记忆库中检索相关信息。"
                        "- search_arxiv: 在arXiv上搜索论文摘要。"
                        "- search_wikipedia: 在Wikipedia上搜索词条摘要。"
                    )
                )
                return agent
    except Exception as e:
        print(f"\n[错误] 无法连接到 MCP 服务器：{e}")
        print("请确认 mcp_server.py 可以独立运行，且依赖已正确安装。")
        sys.exit(1)

# ========== 主交互循环 ==========
async def main():
    print("欢迎使用 MCP 智能助手！输入 'exit' 退出。")
    agent = await create_mcp_agent()
    while True:
        query = input("\n请输入您的问题: ")
        if query.lower() == "exit":
            break

        print("[系统] 正在思考中...")
        try:
            async for event in agent.astream_events(
                {"messages": [{"role": "user", "content": query}]},
                version="v2"
            ):
                kind = event["event"]
                if kind == "on_tool_start":
                    print(f"[工具调用] {event['name']}...")
                elif kind == "on_tool_end":
                    print(f"[工具完成] {event['name']}")
                elif kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        print(content, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f"\n[错误] {e}\n")

if __name__ == "__main__":
    asyncio.run(main())