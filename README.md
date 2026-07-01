# AI Pilot Agent Practice

一个面向 **AI Pilot / Agent Tool Calling / RAG / Workflow Agent / Skill-aware Agent** 的 Python 学习型工程项目。

本项目不是普通聊天机器人，而是一个逐步演进的 Agent 原型。项目从基础 CSV 数据分析助手开始，逐步扩展到：

```text
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
LLM 安全执行
RAG 文档检索
keyword / embedding / hybrid retrieval
Skill-aware RAG
Workflow Planner
Workflow Runner
Workflow Summary Report
Workflow Result Judgement
Workflow LLM Summary fallback
Skill Registry
Skill Router
Skill-aware RAG pre-filtered retrieval
trace / logger 可观测链路
```

---

## 1. 项目定位

本项目的核心目标是展示：

```text
如何把用户自然语言输入
转换成可控、安全、可追踪的数据分析、RAG 问答和金融策略研究 workflow
```

项目重点不在于预测股票，也不在于单纯调用大模型聊天，而在于 Agent 工程结构：

```text
自然语言理解
工具选择
参数生成
安全执行
本地知识增强
多步任务编排
结果总结
fallback 容错
trace 可解释
skill 能力抽象
```

核心原则：

```text
LLM 不直接执行代码；
LLM 负责理解意图、选择工具、生成参数，或基于 RAG 生成回答；
Python 负责工具注册、参数校验、文件类型判断、安全执行、日志、trace 和 workflow；
RAG 负责本地知识注入；
mock selector / rule router 是 fallback、离线演示和测试能力；
所有新增能力都尽量做到可测试、可解释、可回退。
```

---

## 2. 当前项目状态

当前主线已完成到：

```text
第 81 课：Skill-aware RAG 前置过滤优化
```

当前项目可以理解为：

```text
v0.3：Tool Calling + RAG 原型
v0.4：RAG router + embedding / hybrid + trace + workflow 设计
v0.5：Workflow Agent + Skill-aware Agent
```

当前已经具备四层能力：

```text
Tool 层：具体工具函数与安全执行
RAG 层：keyword / embedding / hybrid / skill-aware prefilter
Workflow 层：planner / runner / summary / judgement / LLM summary fallback
Skill 层：registry / router / CLI trace / skill-aware RAG
```

---

## 3. 当前核心执行路径

### 3.1 规则工具调用路径

```text
用户输入
→ main.py
→ router.py
→ tool_registry.py
→ file_inspector.py
→ parameter_parser.py
→ tools.py / finance_tools.py
→ response_formatter.py
→ trace_formatter.py
```

适合无 API Key、基础演示、fallback 和稳定测试。

### 3.2 LLM Tool Calling 路径

```text
用户输入
→ llm_agent_runner.py
→ llm_tool_selector.py
→ real_llm_tool_selector.py / mock_llm_tool_selector.py
→ llm_router.py
→ tool_registry.py
→ 工具执行
→ response_formatter.py
→ trace_formatter.py
```

DeepSeek 不可用时可 fallback 到 mock selector 或 rule router。

### 3.3 RAG QA 路径

```text
知识性问题
→ skill_router.py
→ rag_retrieval_router.py
→ skill_aware_rag.py
→ rag_retriever.py / rag_embedding_retriever.py / rag_hybrid_retriever.py
→ rag_qa.py
→ rag_llm_answerer.py
→ 本地或 LLM 回答
```

第 81 课后，RAG 已支持 Skill-aware 前置过滤：

```text
用户问题
→ 识别 skill_name
→ 根据 skill.documents 得到 source_filter
→ 只加载 / 只打分 Skill 关联文档
→ 无结果时按配置 fallback 到 global documents
```

### 3.4 Workflow 路径

```text
复杂任务
→ workflow_planner.py
→ workflow_runner.py
→ 多步工具执行
→ workflow_summary_report.py
→ workflow_evaluator.py
→ workflow_llm_summarizer.py
→ trace / reports / charts
```

当前核心 workflow：

```text
stock_strategy_research_workflow
```

典型输入：

```text
完整分析股票数据，并按夏普比率生成策略研究报告
```

---

## 4. 当前支持的数据能力

### 4.1 渠道转化分析

适用于包含以下字段的 CSV：

```text
date, channel, visits, signups, payments
```

支持：

```text
读取 CSV
查看字段
缺失值检查
基础统计
渠道访问 / 注册 / 支付聚合
注册率 / 支付率 / 注册到支付转化率计算
判断最佳渠道
生成渠道分析报告
```

### 4.2 股票风险收益分析

适用于包含以下字段的 CSV：

```text
date, close
```

支持：

```text
读取股票价格数据
计算总收益率
计算年化波动率
计算最大回撤
计算夏普比率
生成金融指标报告
```

### 4.3 均线策略回测与参数扫描

支持：

```text
MA 均线策略回测
回测报告生成
回测图表生成
均线参数扫描
按夏普比率 / 策略收益率 / 超额收益 / 最大回撤排序
参数扫描报告
参数扫描图表
策略研究总结报告
```

### 4.4 Workflow 股票策略研究

当前完整 workflow 会串联：

```text
1. 读取股票数据
2. 计算风险收益指标
3. 生成金融指标报告
4. 扫描均线参数
5. 生成参数扫描报告
6. 生成参数扫描图表
7. 生成策略研究总结报告
8. 生成 workflow summary report
9. 生成 workflow result judgement
10. 生成 workflow final summary，本地 fallback 或 LLM summary
```

---

## 5. Skill-aware Agent 当前能力

当前已登记的 Skill：

```text
channel_analysis_skill
stock_metrics_skill
ma_strategy_backtest_skill
stock_strategy_research_skill
rag_qa_skill
```

当前 Skill 能力状态：

```text
第 77 课：skill_registry.py，登记已有能力包
第 78 课：skill_router.py，根据用户输入识别 Skill
第 79 课：Skill 接入 CLI / Trace
第 80 课：Skill-aware RAG，Skill 开始影响 RAG 返回结果
第 81 课：Skill-aware RAG 前置过滤，Skill 在检索前缩小候选文档范围
```

目前 Skill 已经影响 RAG，但还没有完全接管 workflow / tool 执行调度。

下一步建议：

```text
第 82 课：Skill-aware Workflow Dispatch
```

目标是让命中的 Skill 开始影响 workflow 入口。

---

## 6. 常用命令

### 6.1 安装依赖

```powershell
pip install -r requirements.txt
```

### 6.2 运行主程序

```powershell
python main.py
```

### 6.3 常用 CLI 示例

```text
查看状态
查看工具
查看技能
开启LLM模式
开启RAG模式
开启轨迹
切换文件 data/stock_price_strategy.csv
最大回撤是什么意思？
完整分析股票数据，并按夏普比率生成策略研究报告
退出
```

### 6.4 运行测试

```powershell
python -m pytest
```

运行单课相关测试示例：

```powershell
python -m pytest tests/test_skill_aware_rag_prefilter.py tests/test_skill_aware_rag.py tests/test_rag_retrieval_router.py
```

### 6.5 配置 DeepSeek API Key

PowerShell 当前窗口临时配置：

```powershell
$env:DEEPSEEK_API_KEY="你的新APIKey"
```

永久配置：

```powershell
setx DEEPSEEK_API_KEY "你的新APIKey"
```

---

## 7. 主要目录结构

```text
ai_pilot_agent/
├─ main.py
├─ config.py
├─ tool_registry.py
├─ router.py
├─ llm_agent_runner.py
├─ llm_tool_selector.py
├─ llm_router.py
├─ llm_tool_schema.py
├─ mock_llm_tool_selector.py
├─ real_llm_tool_selector.py
├─ llm_health_check.py
├─ rag_document_loader.py
├─ rag_retriever.py
├─ rag_embedding_indexer.py
├─ rag_embedding_retriever.py
├─ rag_hybrid_retriever.py
├─ rag_retrieval_router.py
├─ rag_qa.py
├─ rag_llm_answerer.py
├─ skill_registry.py
├─ skill_router.py
├─ skill_aware_rag.py
├─ workflow_planner.py
├─ workflow_runner.py
├─ workflow_summary_report.py
├─ workflow_evaluator.py
├─ workflow_llm_summarizer.py
├─ response_formatter.py
├─ trace_formatter.py
├─ cli_command_handler.py
├─ tools.py
├─ finance_tools.py
├─ documents/
├─ data/
├─ docs/
└─ tests/
```

---

## 8. 当前下一步

建议下一课继续：

```text
第 82 课：Skill-aware Workflow Dispatch
```

推荐先做原型，不要一次性大改执行链路：

```text
新增 skill_dispatcher.py
新增 tests/test_skill_dispatcher.py
轻量接入 main.py
trace 展示 skill dispatch 信息
保持原 workflow_runner / tool router fallback
```

目标：

```text
用户输入
→ skill_router 命中 stock_strategy_research_skill
→ skill_dispatcher 发现该 skill 绑定 stock_strategy_research_workflow
→ dispatch 到 workflow_runner
→ trace 记录 skill dispatch 决策
```

---

## 9. 项目展示一句话

本项目是一个从 Tool Calling 和 RAG 逐步演进到 Workflow Agent 与 Skill-aware Agent 的学习型工程原型，重点展示大模型不直接执行代码，而是通过 Python 安全执行层、RAG 知识增强、Workflow 编排和 Skill 路由完成可解释、可回退、可测试的自动化任务。
