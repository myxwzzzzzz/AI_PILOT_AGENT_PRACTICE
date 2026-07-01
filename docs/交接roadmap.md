# AI Pilot Agent Learning Roadmap

本文件记录 `AI Pilot Agent Practice` 项目的学习路线、已完成课程、当前状态和后续规划。

---

## 0. 项目基本信息

项目名：

```text
AI Pilot Agent Practice
```

远程仓库：

```text
AI_PILOT_AGENT_PRACTICE
```

本地路径：

```powershell
D:\Vibecoding\ai_pilot_agent
```

conda 环境：

```text
IND5003
```

当前主分支：

```text
main
```

当前完成进度：

```text
第 81 课：Skill-aware RAG 前置过滤优化
```

---

## 1. 项目总目标

构建一个可展示、可测试、可解释的 AI Pilot Agent 原型。

项目重点：

```text
Tool Calling
安全工具执行
文件类型识别
参数校验
RAG 本地知识增强
LLM fallback
trace / logger
Workflow 多步任务编排
Skill 能力抽象
Skill-aware RAG
后续 Skill-aware Dispatch
```

项目原则：

```text
LLM 不直接执行代码；
LLM 只负责理解意图、选择工具、生成参数或生成总结；
Python 负责实际执行、安全校验、日志和 trace；
RAG 负责本地知识增强；
Workflow 负责任务编排；
Skill 负责能力域组织和路由。
```

---

## 2. 阶段总览

| 阶段 | 主题 | 状态 |
|---|---|---|
| v0.1 | 基础 CSV 数据分析助手 | 已完成 |
| v0.2 | Tool Registry + 金融指标 + 策略回测 | 已完成 |
| v0.3 | LLM Tool Calling + DeepSeek + RAG QA | 已完成 |
| v0.4 | RAG router + embedding / hybrid + trace + workflow 设计 | 已完成 |
| v0.5 | Workflow Agent + Skill-aware Agent | 进行中，已完成到第 81 课 |

---

## 3. v0.1：基础 CSV 数据分析助手

已完成：

```text
创建 Python 项目结构
创建 conda 环境 IND5003
准备 data/channel_data.csv
实现 CSV 读取
查看字段
缺失值检查
基础统计
渠道访问 / 注册 / 支付聚合
注册率 / 支付率 / 注册到支付转化率计算
判断最佳渠道
生成渠道分析 Markdown 报告
建立早期 CLI 主循环
```

---

## 4. v0.2：Tool Registry + 金融策略工具

已完成：

```text
引入 Tool Registry
建立 router.py
建立 file_inspector.py
建立 parameter_parser.py
支持文件类型识别
支持股票价格数据 date, close
计算总收益率
计算年化波动率
计算最大回撤
计算夏普比率
生成金融指标报告
运行均线策略回测
生成回测报告
生成回测图表
参数扫描
参数扫描报告
参数扫描图表
策略研究总结报告
```

---

## 5. v0.3：LLM Tool Calling + RAG QA

已完成：

```text
DeepSeek real selector
OpenAI-compatible API 调用
mock selector fallback
LLM Tool Calling JSON 结构
LLM 安全执行路由
工具存在性校验
文件类型校验
参数合法性校验
RAG 文档读取
RAG keyword retriever
RAG QA
DeepSeek RAG answerer
本地规则 fallback
trace 工具调用轨迹
logger 工具调用日志
```

---

## 6. v0.4：RAG router + embedding / hybrid + trace + workflow 设计

### 第 56 课：提交统一 RAG retrieval router

状态：已完成

内容：

```text
统一 RAG 检索入口
接入 llm_agent_runner.py
接入 llm_tool_selector.py
新增 tests/test_rag_retrieval_router.py
```

### 第 57 课：整理 pytest 测试体系

状态：已完成

内容：

```text
新增 pytest.ini
新增 tests/conftest.py
requirements.txt 增加 pytest
标准化 python -m pytest
真实 LLM 测试默认跳过
```

### 第 58 课：RAG retrieval mode 配置化

状态：已完成

内容：

```text
DEFAULT_RETRIEVAL_MODE
RAG 检索模式从硬编码改为配置化
```

### 第 59 课：RAG 文档质量升级

状态：已完成

内容：

```text
扩展 ma_strategy_notes.md
扩展 risk_metrics_notes.md
扩展 agent_tool_usage_notes.md
新增 rag_qa_examples.md
```

### 第 60 课：Embedding RAG 设计文档

状态：已完成

内容：

```text
docs/rag_embedding_design.md
设计 embedding index、retriever、fallback
```

### 第 61 课：最小 embedding indexer

状态：已完成

内容：

```text
rag_embedding_indexer.py
本地 hash embedding
data/rag_index/rag_index.json
tests/test_rag_embedding_indexer.py
```

### 第 62 课：Embedding retriever

状态：已完成

内容：

```text
rag_embedding_retriever.py
cosine similarity
mode="embedding"
```

### 第 63 课：Hybrid RAG

状态：已完成

内容：

```text
rag_hybrid_retriever.py
keyword + embedding fusion
deduplicate + rerank
mode="hybrid"
```

### 第 64 课：RAG trace 优化

状态：已完成

内容：

```text
RAG 检索模式
chunk 数量
source
score
retrieval_sources
fallback 信息
```

### 第 65 课：Agent Workflow 设计文档

状态：已完成

内容：

```text
docs/agent_workflow_design.md
设计 stock_strategy_research_workflow
规划 workflow_planner.py / workflow_runner.py
```

### 第 66 课：项目展示文档

状态：已完成

内容：

```text
docs/project_highlights.md
docs/demo_script.md
```

### 第 67 课：v0.4 稳定版收尾

状态：已完成

内容：

```text
README.md
docs/architecture.md
docs/usage_example.md
docs/ai_pilot_agent_learning_roadmap_updated.md
v0.4 tag
```

### 第 68 课：v0.4 复盘与下一阶段规划

状态：已完成

内容：

```text
docs/v04_retrospective_and_next_steps.md
```

---

## 7. v0.5：Workflow Agent + Skill-aware Agent

### 第 69 课：Workflow Planner 原型

状态：已完成

内容：

```text
workflow_planner.py
tests/test_workflow_planner.py
识别 stock_strategy_research_workflow
生成多步计划
```

### 第 70 课：Workflow Runner 原型

状态：已完成

内容：

```text
workflow_runner.py
tests/test_workflow_runner.py
按 plan 顺序执行工具
失败默认停止
返回 step_results / trace / outputs
```

### 第 71 课：Workflow 输出与 trace 优化

状态：已完成

内容：

```text
步骤统计
参数展示
耗时
输出文件
generated_files
step_traces
```

### 第 72 课：Workflow 接入 CLI / Agent 主流程

状态：已完成

内容：

```text
main.py 接入 workflow_runner
response_formatter.py 支持 workflow result
trace_formatter.py 支持 workflow trace
cli_command_handler.py 新增 查看工作流
```

### 第 73 课：Workflow Summary Report

状态：已完成

内容：

```text
workflow_summary_report.py
自动生成 workflow_summary_report_xxx.md
展示用户请求、数据文件、步骤、输出文件、建议查看顺序
```

### 第 74 课：Workflow 结果判断

状态：已完成

内容：

```text
workflow_evaluator.py
根据最大回撤、夏普比率、超额收益做规则判断
生成风险提示、主要发现和后续建议
```

### 第 75 课：Workflow LLM Summary fallback

状态：已完成

内容：

```text
workflow_llm_summarizer.py
尝试 DeepSeek 总结
失败 fallback 到本地总结
workflow_final_summary
```

### 第 76 课：Skill 抽象设计

状态：已完成

内容：

```text
docs/skill_abstraction_design.md
定义 Tool / Workflow / Skill 关系
规划 skill_registry.py / skill_router.py
```

### 第 77 课：skill_registry.py

状态：已完成

内容：

```text
skill_registry.py
tests/test_skill_registry.py
登记 channel_analysis_skill
登记 stock_metrics_skill
登记 ma_strategy_backtest_skill
登记 stock_strategy_research_skill
登记 rag_qa_skill
```

### 第 78 课：skill_router.py

状态：已完成

内容：

```text
skill_router.py
tests/test_skill_router.py
根据用户输入识别 Skill
返回 skill_name / confidence / reason / matched_keywords / file_type_compatible
```

### 第 79 课：Skill 接入 CLI / Trace

状态：已完成

内容：

```text
查看技能
Skill route 写入 trace
trace 展示命中 Skill、原因、关键词、文件类型匹配
```

### 第 80 课：Skill-aware RAG

状态：已完成

内容：

```text
skill_aware_rag.py
根据 skill.documents 优先筛选 RAG chunks
支持 global fallback
trace 展示 skill-aware RAG 信息
```

说明：

```text
这一课主要是检索后筛选，主要提升准确性和可解释性，不明显提升速度。
```

### 第 81 课：Skill-aware RAG 前置过滤优化

状态：已完成

内容：

```text
rag_document_loader.py 支持 source_filter
rag_retriever.py 支持 source_filter
rag_retrieval_router.py 在 skill_name 存在时先按 skill.documents 缩小候选文档
rag_retrieval_scope 支持 skill_documents_prefiltered
tests/test_skill_aware_rag_prefilter.py
```

意义：

```text
Skill 不只是筛选结果，而是在检索前就缩小候选文档范围。
```

---

## 8. 后续课程规划

### 第 82 课：Skill-aware Workflow Dispatch

状态：待做

目标：

```text
用户输入
→ skill_router 命中 Skill
→ skill_dispatcher 判断是否绑定 workflow
→ 如果绑定并且文件类型兼容，则进入 workflow_runner
→ trace 记录 skill_dispatch
```

建议新增：

```text
skill_dispatcher.py
tests/test_skill_dispatcher.py
```

建议修改：

```text
main.py
trace_formatter.py
tests/test_skill_cli_integration.py 或新增 tests/test_skill_workflow_dispatch.py
```

### 第 83 课：Skill-aware Tool Dispatch

状态：待做

目标：

```text
用户输入
→ 命中 Skill
→ 在该 Skill 允许 tools 内辅助选择具体 tool
```

意义：

```text
减少乱选工具
让工具调用受 Skill 能力域约束
提高可控性
```

### 第 84 课：Skill-specific Prompt

状态：待做

目标：

```text
不同 Skill 使用不同 prompt 风格
stock_strategy_research_skill 使用金融策略分析口吻
channel_analysis_skill 使用增长数据分析口吻
rag_qa_skill 使用知识解释口吻
```

建议新增：

```text
skill_prompt_registry.py
tests/test_skill_prompt_registry.py
```

### 第 85 课：Skill Trace 完整化

状态：待做

目标：

```text
trace 完整展示：
Skill route
Skill dispatch
RAG scope
Workflow dispatch
Tool dispatch
fallback
generated files
```

### 第 86 课：Skill Fallback 策略

状态：待做

目标：

```text
文件类型不匹配时解释原因
Skill workflow 失败时给出 fallback 建议
RAG 无结果时 fallback 到 global documents
工具失败时记录影响范围
```

### 第 87 课：Skill 文档化

状态：待做

目标：

```text
docs/skills/channel_analysis_skill.md
docs/skills/stock_metrics_skill.md
docs/skills/ma_strategy_backtest_skill.md
docs/skills/stock_strategy_research_skill.md
docs/skills/rag_qa_skill.md
```

### 第 88 课：v0.5 README / architecture / usage 更新

状态：待做

目标：

```text
更新 README.md
更新 docs/architecture.md
更新 docs/usage_example.md
更新 docs/ai_pilot_agent_learning_roadmap_updated.md
```

### 第 89 课：v0.5 Demo Script

状态：待做

目标：

```text
更新 docs/demo_script.md
展示 Skill-aware RAG、Workflow、Trace、LLM Summary fallback
```

### 第 90 课：v0.5 稳定版收尾

状态：待做

目标：

```text
完整 pytest
清理临时文件
提交文档
打 tag v0.5
push GitHub
```

建议命令：

```powershell
python -m pytest

git tag v0.5
git push AI_PILOT_AGENT_PRACTICE v0.5
```

---

## 9. 更远期 v0.6 方向

v0.5 做扎实后，再考虑：

```text
LLM Planner
ReAct loop
任务重规划
状态持久化
MCP 接入
外部 API 工具
数据库工具
Web UI / Streamlit 展示
多 Agent handoff
```

当前不建议过早跳到 v0.6。应先完成 v0.5 的 Skill-aware Workflow Agent 闭环。

---

## 10. 当前一句话总结

当前项目已经完成到：

```text
Skill-aware RAG 前置过滤优化
```

下一步应该做：

```text
Skill-aware Workflow Dispatch
```

目标是把 Skill 从“影响 RAG 检索范围”升级为“影响 workflow 执行入口”，让项目进一步接近真正的 Skill-aware Workflow Agent。
