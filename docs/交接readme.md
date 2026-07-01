# AI Pilot Agent Practice 交接 README

本文件用于把当前项目状态交接给新的 ChatGPT 对话或新的开发阶段。请先阅读本文件，再继续后续课程。

---

## 1. 项目基本信息

项目名：

```text
AI Pilot Agent Practice
```

本地路径：

```powershell
D:\Vibecoding\ai_pilot_agent
```

conda 环境：

```text
IND5003
```

远程仓库名：

```text
AI_PILOT_AGENT_PRACTICE
```

主分支：

```text
main
```

当前进度：

```text
已完成到第 81 课：Skill-aware RAG 前置过滤优化
```

---

## 2. 项目定位

这是一个面向 **AI Pilot / Agent Tool Calling / RAG / Workflow Agent / Skill-aware Agent** 的学习型工程项目。

项目不是普通聊天机器人，也不是单纯数据分析脚本。它的核心是展示：

```text
用户自然语言输入
→ 意图识别
→ Skill 路由
→ 工具选择 / RAG / Workflow
→ Python 安全执行
→ trace 可解释
→ 报告和图表输出
```

重要原则：

```text
LLM 不直接执行代码；
LLM 只负责理解意图、生成结构化工具调用、或基于 RAG 总结回答；
Python 负责工具注册、参数校验、文件类型判断、安全执行、日志和 trace；
RAG 负责本地知识注入；
Workflow 负责多步任务编排；
Skill 负责能力域抽象和路由；
fallback 保证无 API 或失败场景仍可运行。
```

---

## 3. 当前阶段总览

项目目前已经形成四层结构：

```text
Tool 层：
具体 Python 工具函数，例如数据读取、指标计算、报告生成、图表生成。

RAG 层：
本地知识库检索与问答，支持 keyword / embedding / hybrid / skill-aware prefilter。

Workflow 层：
复杂任务拆解、顺序执行、结果汇总、风险判断和 LLM/local fallback 总结。

Skill 层：
把 tools、workflow、documents、prompt 方向组织成业务能力包。
```

---

## 4. 已完成课程记录

### v0.3 之前

已完成：

```text
基础 CSV 数据分析
Rule-based Router
Tool Registry
文件类型识别
渠道转化分析
股票风险收益分析
均线策略回测
参数扫描
图表生成
Markdown 报告生成
LLM Tool Calling
DeepSeek real selector
mock selector fallback
RAG QA
工具调用 trace
logger
```

### v0.4

已完成：

```text
第 56 课：提交统一 RAG retrieval router
第 57 课：整理 pytest 测试体系
第 58 课：RAG retrieval mode 配置化
第 59 课：RAG 文档质量升级
第 60 课：Embedding RAG 设计文档
第 61 课：最小 embedding indexer
第 62 课：Embedding retriever
第 63 课：Hybrid RAG
第 64 课：RAG trace 优化
第 65 课：Agent Workflow 设计文档
第 66 课：项目展示文档
第 67 课：v0.4 稳定版收尾
第 68 课：v0.4 复盘与下一阶段规划
```

### v0.5 已完成

```text
第 69 课：Workflow Planner 原型
第 70 课：Workflow Runner 原型
第 71 课：Workflow 输出与 trace 优化
第 72 课：Workflow 接入 CLI / Agent 主流程
第 73 课：Workflow Summary Report
第 74 课：Workflow 结果判断
第 75 课：Workflow LLM Summary fallback
第 76 课：Skill 抽象设计
第 77 课：skill_registry.py
第 78 课：skill_router.py
第 79 课：Skill 接入 CLI / Trace
第 80 课：Skill-aware RAG
第 81 课：Skill-aware RAG 前置过滤优化
```

---

## 5. 当前关键模块

### Tool 相关

```text
tool_registry.py
router.py
llm_router.py
llm_tool_schema.py
tools.py
finance_tools.py
file_inspector.py
parameter_parser.py
```

### LLM 相关

```text
llm_agent_runner.py
llm_tool_selector.py
real_llm_tool_selector.py
mock_llm_tool_selector.py
llm_health_check.py
```

### RAG 相关

```text
rag_document_loader.py
rag_retriever.py
rag_embedding_indexer.py
rag_embedding_retriever.py
rag_hybrid_retriever.py
rag_retrieval_router.py
rag_qa.py
rag_llm_answerer.py
skill_aware_rag.py
```

当前 RAG 已支持：

```text
keyword retrieval
embedding retrieval
hybrid retrieval
skill-aware retrieval
skill-aware pre-filtered retrieval
global fallback
trace metadata
```

### Workflow 相关

```text
workflow_planner.py
workflow_runner.py
workflow_summary_report.py
workflow_evaluator.py
workflow_llm_summarizer.py
```

当前核心 workflow：

```text
stock_strategy_research_workflow
```

### Skill 相关

```text
skill_registry.py
skill_router.py
skill_aware_rag.py
```

已登记 Skill：

```text
channel_analysis_skill
stock_metrics_skill
ma_strategy_backtest_skill
stock_strategy_research_skill
rag_qa_skill
```

---

## 6. 第 81 课后的重要状态

第 81 课完成后，Skill-aware RAG 已从“检索后过滤”升级为“检索前过滤”。

旧逻辑：

```text
全局加载所有 documents
→ 全局打分
→ 再筛选 Skill 关联文档
```

新逻辑：

```text
skill_router 命中 Skill
→ 根据 skill.documents 构造 source_filter
→ rag_document_loader 只加载指定文档
→ rag_retriever 只对指定文档 chunks 打分
→ 有结果则 rag_retrieval_scope = skill_documents_prefiltered
→ 无结果时 fallback 到 global documents
```

相关函数变化：

```text
build_document_chunks(source_filter=None)
retrieve_relevant_chunks(source_filter=None)
retrieve_chunks(skill_name=..., fallback_to_global=True)
```

之前全局测试出现过一个适配问题：

```text
tests/test_rag_hybrid_retriever.py 里的 monkeypatch lambda 没接收 source_filter 参数
```

修法：

```python
lambda source_filter=None: [...]
```

当前该问题已修复并提交。

---

## 7. 当前还没完成的内容

目前 Skill 已经：

```text
能登记
能路由识别
能显示在 CLI / trace
能影响 RAG 检索范围
能做 RAG 前置过滤
```

但 Skill 还没有完全接管执行层。

当前 workflow / tool 执行主要仍走：

```text
workflow_planner.py
workflow_runner.py
router.py
llm_router.py
tool_registry.py
```

后续要做的是：

```text
用户输入
→ skill_router.py
→ skill_dispatcher.py
→ 由 Skill 决定走 workflow / tool / RAG / prompt
```

---

## 8. 推荐下一课

下一课建议：

```text
第 82 课：Skill-aware Workflow Dispatch
```

目标：

```text
让 Skill 不只影响 RAG，而是开始影响 workflow 入口。
```

建议设计：

```text
新增 skill_dispatcher.py
新增 tests/test_skill_dispatcher.py
轻量修改 main.py
轻量修改 trace_formatter.py
保持原 workflow 路径和 tool router fallback
```

预期流程：

```text
用户输入
→ skill_router 命中 stock_strategy_research_skill
→ skill_dispatcher 发现该 Skill 绑定 stock_strategy_research_workflow
→ 判断当前文件类型是否兼容
→ dispatch 到 workflow_runner
→ trace 记录 skill_dispatch 信息
```

第一版不要一次性接管全部工具执行，先让 workflow dispatch 可测试、可回退。

---

## 9. 新对话继续开发时的要求

如果这是一个新对话，请先做：

```text
1. 阅读最新项目 zip
2. 查看 README.md
3. 查看 docs/交接readme.md
4. 查看 docs/交接roadmap.md
5. 查看关键代码：
   - skill_registry.py
   - skill_router.py
   - skill_aware_rag.py
   - rag_retrieval_router.py
   - workflow_runner.py
   - main.py
   - trace_formatter.py
6. 以真实代码为准，不要凭空猜测
```

如果文档描述和代码不一致，以代码为准，并说明不一致点。

---

## 10. 常用命令

运行测试：

```powershell
python -m pytest
```

运行主程序：

```powershell
python main.py
```

提交时不要提交：

```text
临时 patch 文件
临时 zip 文件
docs/交接readme.md 以外的重复交接草稿
docs/交接roadmap.md 以外的重复路线草稿
```

如果用户明确要求更新交接文档，则可以提交：

```text
README.md
docs/交接readme.md
docs/交接roadmap.md
```

---

## 11. 一句话交接

当前项目已经完成到 Skill-aware RAG 前置过滤阶段。下一步应从第 82 课开始，让 Skill 从“影响 RAG 检索范围”升级为“影响 workflow 执行入口”，逐步形成完整的 Skill-aware Workflow Agent。
