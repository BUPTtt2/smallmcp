# ========== 环境编码设置（必须在所有 import 之前） ==========
import os
import sys
from pathlib import Path

# 强制 Python 使用 UTF-8 编码
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 日志重定向到文件（便于调试 Trae 启动问题）
import datetime
LOG_FILE = Path(__file__).parent / "mcp_error.log"
sys.stderr = open(LOG_FILE, "a", encoding="utf-8")
print(f"\n\n=== MCP Server Started at {datetime.datetime.now()} ===", file=sys.stderr)

from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

mcp = FastMCP("Paper Research Assistant")

# ========== 配置持久化目录 ==========
BASE_DIR = Path(__file__).parent
MEMORY_DIR = BASE_DIR / "memory_db"
MEMORY_DIR.mkdir(exist_ok=True)

# ========== 初始化嵌入模型 ==========
try:
    embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)
    print("嵌入模型初始化成功", file=sys.stderr)
except Exception as e:
    print(f"嵌入模型初始化失败：{e}", file=sys.stderr)
    sys.exit(1)

# ========== 初始化 Chroma 向量存储 ==========
try:
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory=str(MEMORY_DIR)
    )
    print(f"向量存储初始化成功，目录：{MEMORY_DIR}", file=sys.stderr)
except Exception as e:
    print(f"向量存储初始化失败：{e}", file=sys.stderr)
    sys.exit(1)

# ========== 工具定义 ==========
arxiv_tool = ArxivQueryRun()
wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
import traceback

@mcp.tool()
def retrieve_memory(query: str) -> str:
    try:
        docs = vector_store.similarity_search(query, k=3)
        if not docs:
            return "未在记忆库中找到相关内容。"
        memories = "\n\n".join([f"记忆片段 {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
        return memories
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- retrieve_memory error ---\n")
            traceback.print_exc(file=f)
            f.write(f"Query: {query}\n")
        return f"记忆检索失败：{str(e)[:100]}"

@mcp.tool()
def save_to_memory(query: str, response: str) -> str:
    try:
        content = f"Q: {query}\nA: {response}"
        vector_store.add_texts([content])
        return "记忆已存入。"
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- save_to_memory error ---\n")
            traceback.print_exc(file=f)
            f.write(f"Query: {query}\nResponse: {response}\n")
        return f"记忆存储失败：{str(e)[:100]}"
    
@mcp.tool()
def search_arxiv(query: str) -> str:
    try:
        return arxiv_tool.run(query)
    except Exception as e:
        return f"arXiv 服务暂时不可用：{str(e)[:100]}"

@mcp.tool()
def search_wikipedia(query: str) -> str:
    try:
        return wiki_tool.run(query)
    except Exception as e:
        return f"Wikipedia 服务暂时不可用：{str(e)[:100]}"

print("MCP 服务器准备就绪，进入主循环...", file=sys.stderr)

if __name__ == "__main__":
    # 关键：禁用横幅输出，避免 Rich 库引发 Unicode 编码错误
    mcp.run(transport="stdio", show_banner=False)