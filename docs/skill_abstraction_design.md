# Skill Abstraction Design

本文件用于设计 `AI Pilot Agent Practice` 项目中的 Skill 抽象层。

当前项目已经具备：

```text
Tool Registry
LLM Tool Calling
RAG QA
keyword / embedding / hybrid retrieval
Workflow Planner
Workflow Runner
Workflow Summary Report
Workflow Result Judgement
Workflow LLM Summary fallback
```

第 76 课的目标不是新增业务工具，而是把现有能力按“可复用能力包”的方式重新理解和组织，为后续 skill registry、skill routing 和更高级 Agent 编排做准备。

---

## 1. 为什么要引入 Skill 概念

当前项目中已经有很多工具：

```text
读取股票数据
计算风险收益指标
生成金融指标报告
扫描均线参数
生成参数扫描报告
生成参数扫描图表
生成策略研究总结报告
RAG 知识问答
Workflow 多步执行
```

这些工具本身是单个能力。

但在真实 Agent 项目里，用户通常不是要“调用某个工具”，而是要完成一个更完整的任务，例如：

```text
帮我完整分析这份股票数据，并生成策略研究报告。
```

这个任务背后需要一组工具、知识文档、参数规则、workflow 和输出格式共同配合。

因此可以把这一组能力抽象成一个 Skill。

简单理解：

```text
Tool = 一个具体函数能力
Workflow = 多个 Tool 的执行流程
Skill = 围绕一个业务目标组织起来的能力包
```

---

## 2. Skill 在本项目中的定义

在本项目中，Skill 可以定义为：

```text
围绕某一类用户任务，把相关工具、知识文档、workflow、参数规则和展示说明组织到一起的可复用能力单元。
```

一个 Skill 不一定直接执行代码。

它更像一个能力说明和调度边界。

---

## 3. Tool、Workflow、Skill 的关系

### 3.1 Tool

Tool 是最底层的能力。

例如：

```text
calculate_stock_metrics
generate_parameter_scan_report
generate_parameter_scan_chart
```

它们通常只负责一个具体动作。

### 3.2 Workflow

Workflow 是多个工具的编排。

例如：

```text
stock_strategy_research_workflow
```

它会依次执行：

```text
1. read_stock_price_data
2. calculate_stock_metrics
3. generate_stock_metrics_report
4. optimize_moving_average_parameters
5. generate_parameter_scan_report
6. generate_parameter_scan_chart
7. generate_strategy_research_summary
```

### 3.3 Skill

Skill 是更高一层的能力包。

例如：

```text
stock_strategy_research_skill
```

它可以包含：

```text
相关 tools
相关 workflow
相关 documents
相关 RAG 知识
参数解析规则
适用文件类型
典型用户问题
展示说明
fallback 策略
```

---

## 4. 第一版建议支持的 Skills

### 4.1 channel_analysis_skill

面向渠道转化分析。

适合用户任务：

```text
分析渠道转化率
哪个渠道表现最好
生成渠道分析报告
```

相关工具：

```text
read_csv_file
show_columns
check_missing_values
show_basic_statistics
analyze_channel_conversion
find_best_channel
generate_channel_report
```

适用文件类型：

```text
channel_data
```

相关数据字段：

```text
date, channel, visits, signups, payments
```

---

### 4.2 stock_metrics_skill

面向基础金融风险收益指标分析。

适合用户任务：

```text
分析风险收益
计算最大回撤
计算夏普比率
生成金融指标报告
```

相关工具：

```text
read_stock_price_data
calculate_stock_metrics
generate_stock_metrics_report
```

适用文件类型：

```text
stock_price
```

---

### 4.3 ma_strategy_backtest_skill

面向均线策略回测。

适合用户任务：

```text
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
生成 MA5-MA10 回测图表
```

相关工具：

```text
run_moving_average_backtest
generate_backtest_report
generate_backtest_chart
```

适用文件类型：

```text
stock_price
```

相关参数：

```text
short_window
long_window
```

---

### 4.4 stock_strategy_research_skill

面向完整股票策略研究。

适合用户任务：

```text
完整分析股票数据
生成策略研究报告
按夏普比率生成完整策略分析
按最大回撤做策略研究
```

相关 workflow：

```text
stock_strategy_research_workflow
```

相关工具：

```text
read_stock_price_data
calculate_stock_metrics
generate_stock_metrics_report
optimize_moving_average_parameters
generate_parameter_scan_report
generate_parameter_scan_chart
generate_strategy_research_summary
```

相关文档：

```text
documents/ma_strategy_notes.md
documents/risk_metrics_notes.md
documents/agent_tool_usage_notes.md
documents/rag_qa_examples.md
```

适用文件类型：

```text
stock_price
```

相关输出：

```text
stock_metrics_report.md
parameter_scan_report_xxx.md
parameter_scan_chart_xxx.png
strategy_research_summary_xxx.md
workflow_summary_report_xxx.md
```

---

### 4.5 rag_qa_skill

面向本地知识问答。

适合用户任务：

```text
最大回撤是什么意思？
夏普比率高说明什么？
MA5-MA10 策略适合震荡行情吗？
如果用户问最大回撤，sort_by 应该是什么？
```

相关模块：

```text
rag_document_loader.py
rag_retriever.py
rag_embedding_retriever.py
rag_hybrid_retriever.py
rag_retrieval_router.py
rag_qa.py
rag_llm_answerer.py
```

相关文档：

```text
documents/
```

---

## 5. 后续可以新增的 skill_registry.py

未来可以新增：

```text
skill_registry.py
```

用于登记每个 Skill。

建议数据结构示例：

```python
SKILL_REGISTRY = [
    {
        "name": "stock_strategy_research_skill",
        "display_name": "股票策略研究 Skill",
        "description": "用于对股票价格数据执行完整风险收益分析、均线参数扫描、图表生成和策略研究总结。",
        "required_file_type": "stock_price",
        "tools": [
            "read_stock_price_data",
            "calculate_stock_metrics",
            "generate_stock_metrics_report",
            "optimize_moving_average_parameters",
            "generate_parameter_scan_report",
            "generate_parameter_scan_chart",
            "generate_strategy_research_summary",
        ],
        "workflows": [
            "stock_strategy_research_workflow",
        ],
        "documents": [
            "ma_strategy_notes.md",
            "risk_metrics_notes.md",
            "agent_tool_usage_notes.md",
        ],
        "example_queries": [
            "完整分析股票数据，并按夏普比率生成策略研究报告",
            "帮我做一次完整的均线策略研究",
        ],
    }
]
```

---

## 6. Skill Router 的未来作用

未来可以新增：

```text
skill_router.py
```

它负责判断用户请求更适合哪个 Skill。

例如：

```text
用户：完整分析股票数据，并生成策略研究报告
→ stock_strategy_research_skill

用户：最大回撤是什么意思？
→ rag_qa_skill

用户：哪个渠道表现最好？
→ channel_analysis_skill
```

Skill Router 和现有 router 的区别是：

```text
router.py 更偏工具级路由
skill_router.py 更偏能力级路由
```

---

## 7. Skill 与 Workflow 的关系

并不是所有 Skill 都需要 Workflow。

例如：

```text
rag_qa_skill
```

可能只是 RAG QA，不需要多步工具执行。

但：

```text
stock_strategy_research_skill
```

非常适合绑定 workflow。

可以理解为：

```text
Skill 是业务能力包
Workflow 是 Skill 内部的一种执行方式
```

---

## 8. Skill 与 RAG 的关系

Skill 可以绑定自己的知识文档。

例如：

```text
stock_strategy_research_skill
```

可以优先使用：

```text
ma_strategy_notes.md
risk_metrics_notes.md
```

未来 RAG 检索时，可以根据 Skill 缩小检索范围。

例如：

```text
用户正在使用 stock_strategy_research_skill
→ 优先检索金融策略相关文档
```

这可以减少无关文档干扰。

---

## 9. Skill 与 Prompt 的关系

未来每个 Skill 可以有自己的 prompt。

例如：

```text
stock_strategy_research_skill
```

可以有专门的总结 prompt：

```text
你是一名金融策略研究助手，请基于工具结果和风险指标，生成谨慎、客观、结构化的策略研究总结。
```

而：

```text
channel_analysis_skill
```

可以有另一套 prompt：

```text
你是一名增长数据分析助手，请基于访问、注册、支付数据，分析渠道转化表现。
```

这样比所有任务共用一个 prompt 更清晰。

---

## 10. Skill 与 MCP 的关系

当前项目还没有 MCP。

但如果未来引入 MCP，Skill 可以作为 MCP 工具组织的上层描述。

例如：

```text
stock_strategy_research_skill
```

未来可以同时调用：

```text
本地 Python 工具
数据库查询工具
外部行情 API
MCP 文件系统工具
MCP GitHub 工具
```

Skill 负责描述“这一组工具共同服务于什么业务能力”。

---

## 11. 第 76 课暂不实现的内容

本课只做设计，不新增执行逻辑。

暂不实现：

```text
skill_registry.py
skill_router.py
Skill-based RAG filtering
Skill-specific prompt
Skill CLI 展示命令
```

这些可以作为后续第 77 课及之后的内容。

---

## 12. 推荐后续课程

### 第 77 课：实现最小 skill_registry.py

目标：

```text
新增 skill_registry.py
登记当前项目已有 Skills
新增 tests/test_skill_registry.py
支持查看所有 skill
```

### 第 78 课：实现 skill_router.py 原型

目标：

```text
根据用户输入识别 Skill
返回 skill_name、reason、confidence
```

### 第 79 课：把 Skill 接入 CLI

目标：

```text
新增 查看技能 命令
在 trace 中显示本次命中的 skill
```

### 第 80 课：Skill-aware RAG

目标：

```text
根据当前 skill 优先检索相关 documents
减少无关知识片段干扰
```

---

## 13. 一句话总结

第 76 课的核心是：

```text
把已经实现的 tools、RAG 和 workflow，从“零散模块”提升为“可复用业务能力包”的设计。
```

这一步完成后，项目会更容易向企业 Agent 里的 Skill / Capability / Domain Agent 概念靠拢。
