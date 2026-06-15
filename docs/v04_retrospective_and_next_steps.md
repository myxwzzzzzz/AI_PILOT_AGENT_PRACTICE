# v0.4 复盘与下一阶段规划

本文用于复盘 `AI Pilot Agent Practice` 项目在 v0.4 阶段完成的能力、当前边界、学习价值，以及下一阶段建议。

v0.4 的核心主题不是单纯增加功能，而是让项目从 `v0.3` 的 LLM Tool Calling + RAG QA 原型，进一步变成一个更清晰、更稳定、更容易展示和继续扩展的 Agent 工程项目。

---

## 1. 当前项目定位

当前项目可以描述为：

```text
一个面向数据分析和金融策略研究的 Tool-Calling + RAG AI Agent 原型。
```

它不是普通聊天机器人，也不是单一数据分析脚本。

它的重点是展示：

```text
如何把用户自然语言输入
转换成可控、安全、可追踪的数据分析和金融策略研究工作流。
```

当前项目已经具备：

```text
规则路由
工具注册表
文件类型识别
参数解析
金融分析工具
策略回测工具
报告和图表生成
LLM Tool Calling
DeepSeek real selector
mock selector fallback
LLM 安全执行
RAG QA
keyword retrieval
embedding retrieval 原型
hybrid retrieval 原型
trace
logger
pytest 测试体系
项目展示文档
workflow 设计文档
```

---

## 2. v0.4 阶段完成内容

v0.4 主要覆盖第 56 课到第 67 课。

| 课程 | 主题 | 状态 |
| --- | --- | --- |
| 第 56 课 | 提交 RAG retrieval router | 已完成 |
| 第 57 课 | 整理 pytest 测试体系 | 已完成 |
| 第 58 课 | 配置默认 RAG retrieval mode | 已完成 |
| 第 59 课 | 升级 RAG 知识文档 | 已完成 |
| 第 60 课 | 设计 embedding-based RAG retrieval | 已完成 |
| 第 61 课 | 实现本地 embedding indexer | 已完成 |
| 第 62 课 | 实现 embedding retriever | 已完成 |
| 第 63 课 | 实现 hybrid RAG retriever | 已完成 |
| 第 64 课 | 优化 RAG trace 展示 | 已完成 |
| 第 65 课 | 设计 Agent Workflow 架构 | 已完成 |
| 第 66 课 | 补充项目展示文档 | 已完成 |
| 第 67 课 | v0.4 文档收尾与 tag | 已完成 |

---

## 3. v0.4 最重要的变化

### 3.1 RAG 检索入口统一

v0.4 之前，上层模块容易直接依赖具体检索器。

v0.4 之后，统一通过：

```text
rag_retrieval_router.py
```

作为检索入口。

当前结构是：

```text
上层模块
→ rag_retrieval_router.py
→ 具体检索器
   ├─ rag_retriever.py              keyword
   ├─ rag_embedding_retriever.py    embedding
   └─ rag_hybrid_retriever.py       hybrid
```

这样做的意义是：

```text
上层只关心“我要相关文档片段”，
不关心底层到底用关键词、embedding 还是 hybrid。
```

这为后续扩展真实 embedding、向量数据库、rerank 等能力留下了清晰接口。

---

### 3.2 测试体系工程化

v0.4 引入并整理了 pytest 测试体系。

现在可以通过：

```bash
python -m pytest
```

统一运行测试。

相比之前一个个运行脚本式测试，pytest 带来的好处是：

```text
自动发现测试
统一运行方式
统一报告通过 / 失败 / 跳过
减少重复 sys.path 代码
避免真实 LLM 测试默认误触发
方便后续持续回归
```

这让项目更接近真实工程项目，而不是零散脚本集合。

---

### 3.3 RAG 从 keyword 扩展到 embedding / hybrid

v0.4 保留 keyword retrieval 作为默认稳定路径，同时新增了 embedding 和 hybrid 能力。

当前支持：

```text
mode="keyword"
mode="embedding"
mode="hybrid"
```

但默认仍然是：

```python
DEFAULT_RETRIEVAL_MODE = "keyword"
```

这是有意设计的。

原因是：

```text
keyword 是当前最稳定、最可解释的路径；
embedding / hybrid 是为下一阶段升级准备的能力；
不应在刚实现时立刻替换主路径。
```

---

### 3.4 RAG trace 更清晰

v0.4 让 trace 可以展示更多 RAG 检索细节，例如：

```text
retrieval_mode
retrieved chunk count
chunk source
chunk score
retrieval_sources
keyword_score
embedding_score
embedding_provider
embedding_status
fallback 信息
```

这让 Agent 不再只是给出答案，而是能解释：

```text
我用了什么检索方式？
我找到了哪些知识片段？
这些片段来自哪里？
有没有发生 fallback？
```

这对 Agent 的可解释性非常重要。

---

### 3.5 项目展示材料补齐

v0.4 新增了面向展示和讲解的文档，例如：

```text
docs/project_highlights.md
docs/demo_script.md
docs/agent_workflow_design.md
docs/rag_embedding_design.md
```

这些文档的作用是：

```text
帮助别人快速理解项目亮点；
帮助自己在面试或答辩时讲清楚项目；
帮助后续开发时不偏离主线。
```

---

## 4. 当前项目里 Agent 概念的体现

### 4.1 Tool / Tool Calling

当前已经明显体现。

项目中的工具包括：

```text
CSV 读取
字段查看
缺失值检查
渠道分析
金融指标分析
均线策略回测
参数扫描
图表生成
报告生成
```

相关模块包括：

```text
tools.py
finance_tools.py
tool_registry.py
llm_tool_schema.py
llm_router.py
```

LLM 不直接执行代码，而是选择工具和参数，Python 负责校验和执行。

---

### 4.2 RAG

当前已经明显体现。

RAG 相关模块包括：

```text
documents/
rag_document_loader.py
rag_retriever.py
rag_embedding_indexer.py
rag_embedding_retriever.py
rag_hybrid_retriever.py
rag_retrieval_router.py
rag_qa.py
rag_llm_answerer.py
```

当前 RAG 既能用于知识问答，也能为 LLM 工具选择提供上下文。

---

### 4.3 Prompt Engineering

当前已经体现。

主要体现在：

```text
real_llm_tool_selector.py
rag_llm_answerer.py
```

工具选择 prompt 要求模型返回结构化 JSON。

RAG QA prompt 要求模型基于本地文档回答，不要编造。

---

### 4.4 Temperature

当前已经体现。

工具选择一般使用较低温度，例如：

```text
temperature = 0
```

这样可以让工具选择更稳定。

RAG 回答可以使用稍高但仍保守的温度，例如：

```text
temperature = 0.2
```

这样可以让回答自然一些，但不至于过度发散。

---

### 4.5 Skill

当前有雏形，但还没有正式抽象。

目前可以把这些看成隐含 skill：

```text
渠道分析 skill
金融指标分析 skill
均线策略研究 skill
RAG 知识问答 skill
```

但项目里还没有正式的：

```text
skill_registry.py
```

后续可以考虑把工具、文档、提示词和使用场景组合成更明确的 skill。

---

### 4.6 MCP

当前还没有体现。

当前项目是：

```text
LLM → 本地 tool_registry → Python 工具
```

还不是：

```text
LLM → MCP client → MCP server → 外部工具 / 数据源
```

MCP 可以作为未来更高级阶段再考虑。

---

## 5. 当前稳定主路径

当前最稳定、最适合作为演示主路径的是：

```text
规则模式
LLM Tool Calling 模式
RAG QA keyword 模式
trace 展示
pytest 测试
报告和图表生成
```

其中 RAG 默认仍然建议使用：

```text
keyword retrieval
```

因为它最稳定、最可解释。

---

## 6. 当前原型 / 预备能力

以下能力已经实现，但更适合看作下一阶段的基础，不建议立刻作为默认主路径：

```text
hash-based embedding indexer
embedding retriever
hybrid retriever
workflow design
```

原因是：

```text
当前 embedding 仍是本地 hash-based 原型；
还没有接真实语义 embedding 模型；
workflow 目前还停留在设计文档阶段；
hybrid 结构已具备，但还需要更真实的 embedding 才能发挥效果。
```

---

## 7. v0.5 建议方向

下一阶段不建议马上大范围重写。

推荐优先级如下：

```text
1. 实现最小 workflow planner
2. 实现最小 workflow runner
3. 支持股票策略研究多步 workflow
4. 增强 workflow trace
5. 再考虑 skill_registry
6. 再考虑真实 embedding API
7. 最后再考虑 MCP / 外部数据源
```

推荐原因：

```text
当前项目的工具已经比较丰富；
下一步最自然的升级是把多个工具串成工作流；
这样更能体现 Agent 的多步任务能力。
```

---

## 8. v0.5 可能课程安排

### 第 69 课：实现 workflow planner 原型

目标：

```text
识别用户是否在请求完整策略研究 workflow；
返回 workflow_name 和步骤列表；
先使用规则方式，不调用 LLM。
```

可能新增：

```text
workflow_planner.py
tests/test_workflow_planner.py
```

---

### 第 70 课：实现 workflow runner 原型

目标：

```text
按步骤调用 tool_registry 中的工具；
收集每一步结果；
失败时停止并返回清晰错误；
形成 workflow_result。
```

可能新增：

```text
workflow_runner.py
tests/test_workflow_runner.py
```

---

### 第 71 课：接入 CLI / Agent Runner

目标：

```text
当用户提出完整策略研究请求时，进入 workflow 路径；
普通单步任务仍然走原来的 tool calling；
RAG QA 仍然走 RAG QA。
```

可能修改：

```text
llm_agent_runner.py
response_formatter.py
trace_formatter.py
```

---

### 第 72 课：workflow trace 优化

目标：

```text
展示 workflow 名称；
展示每一步工具名、参数、状态、输出摘要；
展示失败步骤和 fallback。
```

---

### 第 73 课：skill registry 设计

目标：

```text
把工具、文档和使用场景组织成 skill；
例如 channel_analysis_skill、ma_strategy_research_skill、rag_qa_skill。
```

---

## 9. 当前项目面试讲法

可以这样介绍：

```text
我做了一个面向数据分析和金融策略研究的 AI Agent 原型。
它不是让 LLM 直接执行代码，而是让 LLM 负责理解用户意图、选择工具和生成参数，
然后由 Python 进行文件类型检查、参数校验、工具执行、日志记录和 trace 展示。

项目支持规则模式、LLM Tool Calling 模式和 RAG QA 模式。
在 RAG 部分，我先实现了 keyword retrieval，后续扩展了 embedding indexer、embedding retriever 和 hybrid retriever，
并通过统一的 retrieval router 进行调度。

项目还加入了 fallback 机制，DeepSeek 不可用时可以退回 mock selector 或 rule router，
RAG 回答失败时也可以走本地 fallback。

v0.4 阶段我重点做了工程化整理，包括 pytest 测试体系、RAG trace、项目展示文档和 v0.4 tag。
下一阶段计划把单步工具调用升级成多步 workflow Agent。
```

---

## 10. 总结

v0.4 的价值可以总结为：

```text
把项目从“能跑的 Agent 原型”推进到“结构清晰、可测试、可解释、可展示的 Agent 工程项目”。
```

当前最重要的下一步是：

```text
从单步 Tool Calling 迈向多步 Agent Workflow。
```
