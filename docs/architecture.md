# AI Pilot Agent 系统架构说明

本文档说明当前 v0.4 阶段的系统结构和主要执行路径。

---

## 1. 总体定位

本项目是一个面向数据分析和金融策略研究的 **Tool-Calling + RAG AI Agent 原型**。

核心思想：

```text
用户用自然语言提出任务；
LLM 或规则模块负责理解意图；
Tool Registry 暴露可调用工具；
Python 安全执行层负责校验和执行；
RAG 检索层负责本地知识增强；
trace 和 logger 负责可解释性和调试。
```

---

## 2. 三条主要执行路径

### 2.1 规则模式

```text
用户输入
→ main.py
→ router.py
→ tool_registry.py
→ file_inspector.py
→ parameter_parser.py
→ tools.py / finance_tools.py
→ response_formatter.py
→ logger.py
```

规则模式不依赖 API Key，适合基础演示、回归测试和最终 fallback。

---

### 2.2 LLM Tool Calling 模式

```text
用户输入
→ main.py
→ llm_agent_runner.py
→ llm_tool_selector.py
→ real_llm_tool_selector.py / mock_llm_tool_selector.py
→ llm_router.py
→ tool_registry.py
→ 工具 handler
→ response_formatter.py
→ trace_formatter.py
→ logger.py
```

关键原则：

```text
LLM 不直接执行工具；
LLM 只返回 tool_name 和 arguments；
llm_router.py 负责校验工具名、文件类型和参数；
Python 工具执行真实任务。
```

fallback 路径：

```text
DeepSeek real selector 失败
→ mock selector
→ rule router
```

---

### 2.3 RAG QA 模式

```text
知识性问题
→ llm_agent_runner.py
→ rag_retrieval_router.py
→ keyword / embedding / hybrid retriever
→ rag_qa.py
→ rag_llm_answerer.py
→ DeepSeek 回答或本地 fallback 回答
→ response_formatter.py
→ trace_formatter.py
```

RAG QA 用于回答知识性问题，不执行数据分析工具。

---

## 3. 模块职责

| 模块 | 职责 |
|---|---|
| `main.py` | CLI 主循环、输入分发、输出展示 |
| `cli_state.py` | 保存当前文件、LLM 模式、RAG 模式、trace 状态 |
| `cli_command_handler.py` | 处理系统命令，如切换文件、开启 LLM、开启 RAG |
| `router.py` | 规则模式主路由，也是最终 fallback |
| `tool_registry.py` | 统一登记工具元信息和 handler |
| `file_inspector.py` | 根据 CSV 字段识别文件类型 |
| `parameter_parser.py` | 从自然语言解析 MA 参数和排序指标 |
| `llm_tool_schema.py` | 将工具注册表转换为 LLM 可读 schema |
| `llm_tool_selector.py` | 统一选择 real / mock selector |
| `real_llm_tool_selector.py` | 调用 DeepSeek 选择工具 |
| `mock_llm_tool_selector.py` | 本地模拟 LLM tool call，用于 fallback 和测试 |
| `llm_router.py` | LLM tool call 的安全执行层 |
| `llm_agent_runner.py` | LLM Agent 总调度器，连接 Tool Calling 和 RAG QA |
| `rag_retrieval_router.py` | RAG 检索统一入口 |
| `rag_retriever.py` | keyword retrieval |
| `rag_embedding_indexer.py` | 构建本地 embedding index |
| `rag_embedding_retriever.py` | embedding retrieval |
| `rag_hybrid_retriever.py` | keyword + embedding 融合检索 |
| `rag_qa.py` | RAG QA 入口和 fallback 控制 |
| `rag_llm_answerer.py` | 基于本地片段调用 DeepSeek 生成回答 |
| `trace_formatter.py` | 格式化工具调用和 RAG 检索轨迹 |
| `logger.py` | 写入工具调用日志 |

---

## 4. Tool Calling 架构

Tool Calling 的核心不是让 LLM 自由执行代码，而是让 LLM 在受控范围内选择工具。

```text
Tool Registry
→ LLM Tool Schema
→ LLM Selector
→ LLM Router
→ Python Handler
```

工具注册表中的每个工具包含：

```text
name
description
keywords
required_file_type
required_file_type_name
handler
```

这让规则 router 和 LLM Tool Calling 共用同一套工具定义。

---

## 5. RAG 架构

RAG 层现在采用统一 router：

```text
rag_retrieval_router.py
├─ mode="keyword"   → rag_retriever.py
├─ mode="embedding" → rag_embedding_retriever.py
└─ mode="hybrid"    → rag_hybrid_retriever.py
```

默认模式在 `config.py` 中配置：

```python
DEFAULT_RETRIEVAL_MODE = "keyword"
```

embedding index 构建流程：

```text
documents/
→ rag_document_loader.py
→ chunks
→ rag_embedding_indexer.py
→ hash-based embedding
→ data/rag_index/rag_index.json
```

embedding 检索流程：

```text
用户问题
→ hash-based query embedding
→ 读取 rag_index.json
→ cosine similarity
→ top_k chunks
```

hybrid 检索流程：

```text
用户问题
→ keyword retrieval
→ embedding retrieval
→ 分数归一化
→ 去重
→ 融合排序
→ top_k chunks
```

---

## 6. Trace 与可解释性

开启轨迹后，系统可以展示：

```text
规则路由类型
LLM selector 模式
LLM reason
工具名
参数
文件类型检查
fallback 路径
RAG answer source
RAG retrieval mode
RAG chunk source
RAG chunk score
hybrid retrieval sources
embedding provider / status
```

trace 的目的不是给普通用户增加复杂度，而是帮助开发者和面试讲解时说明：

```text
Agent 为什么这样做？
用了哪个工具？
用了哪些文档片段？
有没有 fallback？
```

---

## 7. 测试体系

项目使用 pytest 统一测试：

```bash
python -m pytest
```

测试覆盖：

```text
金融工具
参数解析
图表和报告生成
Tool Schema
LLM Router
Mock Selector
LLM Selector 入口
RAG document loader
Keyword retriever
Embedding indexer
Embedding retriever
Hybrid retriever
RAG QA
Trace formatter
CLI 相关模块
```

真实 DeepSeek 集成测试默认跳过，避免误消耗 API。

---

## 8. 当前架构边界

当前已经完成：

```text
单步工具调用 Agent
RAG QA Agent
keyword / embedding / hybrid retrieval
fallback
trace
pytest
```

当前尚未完成：

```text
真正多步 workflow runner
skill registry
真实 embedding provider
向量数据库
MCP 接入
长期记忆
自动联网研究
```

下一阶段建议从 Agent Workflow 入手，把已有工具串成可控的多步流程。
