# MCP 论文研究助手

这是一个基于 MCP (Model Context Protocol) 协议的智能论文研究助手项目。

## 项目功能

- **记忆存储与检索**：使用 Chroma 向量数据库存储和检索历史对话
- **arXiv 论文搜索**：在 arXiv 上搜索相关论文
- **Wikipedia 搜索**：在 Wikipedia 上搜索相关知识
- **ReAct Agent**：基于 LangChain 的智能代理

## 项目结构

```
MCP_Paper_Research_Assistant/
├── mcp_server.py      # MCP 服务器实现
├── agent.py           # LangChain ReAct Agent 客户端
├── requirements.txt   # 项目依赖
├── my.env             # 环境变量配置
├── chroma_db/         # Chroma 数据库
├── memory_db/         # 记忆向量存储
└── text.py            # 工具脚本
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

编辑 `my.env` 文件，设置你的 API 密钥：

```
DASHSCOPE_API_KEY=your_api_key_here
```

### 运行 MCP 服务器

```bash
python mcp_server.py
```

### 运行 Agent 客户端

```bash
python agent.py
```

## 技术栈

- **FastMCP**：MCP 协议实现
- **LangChain**：AI 应用框架
- **Chroma**：向量数据库
- **DashScope**：通义千问模型
