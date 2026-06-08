# AI Pilot Agent：数据分析与金融策略研究自动化助手

> 一个面向 AI Pilot / AI 应用 / Agent 工具调用岗位的项目原型。  
> 项目目标是用 Python 构建一个可交互的命令行 Agent Demo，让系统能够根据用户自然语言任务，自动选择工具、校验数据类型、执行数据分析或策略研究任务，并生成 Markdown 报告、工具调用轨迹和日志记录。

---

## 1. 项目背景

本项目围绕 AI Pilot 实习生岗位常见能力要求设计，重点覆盖：

- 大模型与智能 Agent 在业务场景中的落地思路；
- 数据智能处理与流程自动化；
- 金融数据分析、风险收益指标计算；
- 简单量化策略回测与参数扫描；
- 工具调用、状态管理、文件类型校验、调用轨迹与日志审计。

虽然当前版本暂未接入真实大模型 API，但已经完成了一个 Rule-based Agent Prototype：

```text
用户自然语言输入
→ 当前文件状态管理
→ 文件类型识别
→ Tool Registry 匹配工具
→ 参数解析
→ 文件类型校验
→ 工具执行
→ 自然语言回复
→ Markdown 报告生成
→ 工具调用轨迹展示
→ 工具调用日志记录
```

---

## 2. 项目定位

本项目不是传统 Notebook 分析脚本，而是一个小型 Agent 工程原型。

它模拟了真实 Agent 系统中的几个核心模块：

| 项目模块 | Agent 系统概念 |
|---|---|
| `main.py` | 用户交互入口 / CLI Assistant |
| `current_file_path` | 状态管理 State |
| `file_inspector.py` | 上下文识别 / 数据环境识别 |
| `tool_registry.py` | 工具注册表 / Tool Registry |
| `router.py` | 工具选择 / Tool Selection / Guardrails |
| `parameter_parser.py` | 参数解析 / Parameter Extraction |
| `tools.py` | 渠道数据分析工具 |
| `finance_tools.py` | 金融分析与策略研究工具 |
| `response_formatter.py` | 结果解释 / Response Formatting |
| `trace_formatter.py` | 工具调用轨迹 / Tool Call Trace |
| `logger.py` | 日志记录 / Audit Log |

---

## 3. 核心功能

### 3.1 交互式命令行助手

用户可以直接输入自然语言任务，例如：

```text
帮我读取这个 CSV 文件
分析一下渠道转化率
生成渠道分析报告
切换文件 data/stock_price_strategy.csv
运行 MA5-MA10 回测
按收益率扫描均线参数
生成策略研究总结报告
查看工具
查看日志
开启轨迹
```

系统会自动识别任务并调用对应工具。

---

### 3.2 文件状态管理

系统维护当前数据文件状态：

```python
current_file_path = "data/channel_data.csv"
```

用户可以通过命令切换文件：

```text
切换文件 data/stock_price.csv
切换文件 data/stock_price_strategy.csv
切换文件 data/channel_data_new.csv
```

切换后，后续分析都基于新文件执行。

---

### 3.3 文件类型识别与任务兼容性校验

系统根据 CSV 字段自动识别文件类型：

| 文件字段 | 文件类型 |
|---|---|
| `date, channel, visits, signups, payments` | 渠道转化数据 |
| `date, close` | 股票价格数据 |
| 其他字段 | 未知类型数据 |

如果用户用错误文件执行任务，系统会拦截。

示例：

```text
当前文件：data/channel_data.csv
用户输入：分析风险收益
系统提示：当前任务需要股票价格数据，请先切换文件 data/stock_price.csv
```

这体现了 Agent Guardrails 思路：不是所有工具都能随便调用，必须先校验数据结构是否匹配。

---

## 4. 已实现工具列表

### 4.1 渠道数据分析工具

| 工具名称 | 功能 |
|---|---|
| `read_csv_file()` | 读取 CSV，返回行数、字段和前几行预览 |
| `summarize_csv()` | 输出数据规模、字段、缺失值和数值统计 |
| `analyze_channel_conversion()` | 计算注册转化率、付费转化率、注册到付费转化率 |
| `generate_channel_analysis_report()` | 自动生成渠道分析 Markdown 报告 |

示例输入：

```text
分析渠道转化率
生成渠道分析报告
```

---

### 4.2 金融指标分析工具

| 工具名称 | 功能 |
|---|---|
| `read_stock_price_data()` | 读取股票/策略价格数据 |
| `calculate_stock_metrics()` | 计算区间收益率、年化波动率、最大回撤、夏普比率 |
| `generate_stock_metrics_report()` | 生成金融指标 Markdown 报告 |

示例输入：

```text
读取股票价格数据
分析风险收益
生成金融指标报告
```

---

### 4.3 策略回测工具

| 工具名称 | 功能 |
|---|---|
| `run_moving_average_backtest()` | 运行均线策略回测 |
| `generate_backtest_report()` | 生成均线策略回测报告 |

支持默认参数：

```text
运行均线策略回测
生成回测报告
```

也支持自定义参数：

```text
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
用 5 日均线和 10 日均线做回测
```

系统会解析：

```python
short_window = 5
long_window = 10
```

并传入回测工具。

---

### 4.4 参数扫描与策略优化工具

| 工具名称 | 功能 |
|---|---|
| `optimize_moving_average_parameters()` | 批量扫描多组均线参数 |
| `generate_parameter_scan_report()` | 生成参数扫描对比报告 |

示例输入：

```text
扫描均线参数
优化均线策略参数
按收益率扫描均线参数
按超额收益优化均线策略
按最大回撤生成参数扫描报告
```

支持排序指标解析：

| 用户表达 | 对应参数 |
|---|---|
| 夏普、夏普比率、sharpe | `sort_by="sharpe_ratio"` |
| 收益率、策略收益 | `sort_by="strategy_total_return"` |
| 超额收益 | `sort_by="excess_return"` |
| 最大回撤、回撤 | `sort_by="max_drawdown"` |

---

### 4.5 策略研究总结报告工具

| 工具名称 | 功能 |
|---|---|
| `generate_strategy_research_summary()` | 综合基础金融指标、默认回测、参数扫描，生成策略研究总结报告 |

示例输入：

```text
生成策略研究总结报告
生成按收益率排序的策略研究报告
生成按最大回撤排序的策略研究报告
总结一下这个策略研究结果
```

报告内容包括：

1. 标的基础风险收益指标；
2. 默认 MA3-MA5 策略表现；
3. 参数扫描最佳组合；
4. 策略与买入持有对比；
5. 风险提示；
6. 后续优化建议。

---

## 5. 项目目录结构

当前推荐目录结构：

```text
ai_pilot_agent/
├── main.py
├── router.py
├── tool_registry.py
├── file_inspector.py
├── parameter_parser.py
├── response_formatter.py
├── trace_formatter.py
├── logger.py
├── tools.py
├── finance_tools.py
├── test_finance_tools.py
├── test_backtest.py
├── test_parameter_scan.py
├── test_strategy_summary.py
├── data/
│   ├── channel_data.csv
│   ├── channel_data_new.csv
│   ├── stock_price.csv
│   ├── stock_price_strategy.csv
│   ├── channel_analysis_report.md
│   ├── stock_metrics_report.md
│   ├── backtest_report.md
│   ├── parameter_scan_report.md
│   ├── strategy_research_summary.md
│   └── logs/
│       └── tool_calls.jsonl
└── README.md
```

---

## 6. 运行方式

### 6.1 安装依赖

当前项目核心依赖：

```bash
pip install pandas numpy
```

如果后续增加图表或可视化，可加入：

```bash
pip install matplotlib streamlit
```

---

### 6.2 启动命令行助手

```bash
python main.py
```

启动后可以输入：

```text
查看工具
切换文件 data/stock_price_strategy.csv
开启轨迹
运行 MA5-MA10 回测
生成策略研究总结报告
查看日志
退出
```

---

## 7. 示例数据说明

### 7.1 渠道数据

文件：

```text
data/channel_data.csv
```

字段：

| 字段 | 含义 |
|---|---|
| `date` | 日期 |
| `channel` | 渠道 |
| `visits` | 访问量 |
| `signups` | 注册数 |
| `payments` | 付费数 |

用于分析渠道转化率。

---

### 7.2 股票价格数据

文件：

```text
data/stock_price.csv
data/stock_price_strategy.csv
```

字段：

| 字段 | 含义 |
|---|---|
| `date` | 日期 |
| `close` | 收盘价 / 净值 |

用于金融指标计算、策略回测和参数扫描。

---

## 8. 示例交互

### 示例 1：渠道分析

```text
请输入你的问题：分析渠道转化率
```

系统输出：

```text
已完成渠道转化率分析。

整体来看，小红书是当前表现最好的渠道，它在注册转化率、付费转化率和注册到付费转化率三个指标上均排名第一。
```

---

### 示例 2：金融指标分析

```text
请输入你的问题：切换文件 data/stock_price_strategy.csv
请输入你的问题：分析风险收益
```

系统输出：

```text
已完成风险收益指标分析。

区间收益率：41.00%
年化波动率：...
最大回撤：...
夏普比率：...
```

---

### 示例 3：自定义均线回测

```text
请输入你的问题：运行 MA5-MA10 回测
```

系统输出：

```text
已完成均线策略回测。

策略名称：MA5-MA10 均线策略
策略区间收益率：22.61%
买入持有收益率：41.00%
超额收益：-18.39%
最新信号：持仓
```

---

### 示例 4：参数扫描

```text
请输入你的问题：按收益率扫描均线参数
```

系统输出：

```text
已完成均线策略参数扫描。

本次共完成 9 组参数组合回测，排序指标为：策略收益率。
最佳参数组合：...
```

---

### 示例 5：策略研究总结报告

```text
请输入你的问题：生成策略研究总结报告
```

系统输出：

```text
策略研究总结报告已生成。

报告路径：
data/strategy_research_summary.md

综合建议：
当前样本中均线策略整体未能产生正超额收益，建议不要直接使用当前参数，后续应扩大样本区间、增加震荡和下跌行情数据，并引入风控或过滤条件。
```

---

## 9. 工具调用轨迹

输入：

```text
开启轨迹
运行 MA5-MA10 回测
```

系统会显示：

```text
工具调用轨迹：
- 用户输入：运行 MA5-MA10 回测
- 匹配方式：关键词匹配
- 命中关键词：回测
- 选择工具：run_moving_average_backtest
- 当前文件：data/stock_price_strategy.csv
- 当前文件类型：股票价格数据
- 工具要求文件类型：股票价格数据
- 参数解析：短期均线=5，长期均线=10
- 实际传入参数：{'short_window': 5, 'long_window': 10}
- 文件类型校验：通过
- 工具执行状态：成功
```

这体现了 Agent 系统的可解释性与可审计性。

---

## 10. 工具调用日志

系统会将工具调用写入：

```text
data/logs/tool_calls.jsonl
```

日志记录内容包括：

- 时间戳；
- 用户输入；
- 当前文件；
- 选择工具；
- 工具执行状态；
- 输出摘要；
- 工具调用轨迹。

可在助手中输入：

```text
查看日志
```

查看最近工具调用记录。

---

## 11. 当前能力边界

当前版本仍有一些限制：

1. 路由仍基于关键词规则，而不是真正的大模型理解；
2. 当前金融数据为本地 CSV 示例数据，未接入实时行情；
3. 回测未考虑手续费、滑点和冲击成本；
4. 当前策略仅支持简单均线策略；
5. 参数扫描存在样本内过拟合风险；
6. 样本数据较短，夏普比率和年化波动率不适合过度解读；
7. 当前版本主要是命令行交互，尚未提供 Web UI；
8. 当前未接入 RAG、研报解析或真实投研文档问答。

---

## 12. 后续优化方向

### 12.1 接入 LLM Tool Calling

将当前 Tool Registry 升级为 LLM 可理解的工具 schema，让大模型根据工具描述自动选择工具。

计划新增：

```text
tool name
tool description
tool parameters
required file type
execution constraints
```

---

### 12.2 使用 LangGraph 做 Workflow 编排

将当前单步工具调用升级为多步骤工作流：

```text
读取数据
→ 判断文件类型
→ 选择分析路径
→ 执行指标分析
→ 执行回测
→ 执行参数扫描
→ 生成总结报告
```

---

### 12.3 增加 RAG 文档分析能力

面向证券投研场景，增加：

- 研报 PDF 读取；
- 财报/公告文本解析；
- 文本切分；
- 向量检索；
- 带引用来源的问答；
- 投研摘要和风险提示生成。

---

### 12.4 增加更多策略工具

可扩展：

- 均线交叉策略；
- 动量策略；
- 布林带策略；
- 回撤止损；
- 仓位控制；
- 多标的对比；
- 基准指数对比。

---

### 12.5 增加可视化和前端

可加入：

- Streamlit；
- FastAPI；
- 策略净值曲线；
- 回撤曲线；
- 参数扫描热力图；
- 报告下载功能。

---

## 13. 面试表达

可以这样介绍项目：

> 我做了一个面向 AI Pilot 场景的 Agent 工具调用原型。系统支持命令行自然语言输入，通过文件类型识别、Tool Registry、参数解析和工具调用轨迹，实现渠道数据分析、金融风险收益分析、均线策略回测、参数扫描和策略研究总结报告生成。  
> 
> 项目的重点不是单一模型训练，而是模拟真实业务中 Agent 如何把数据处理、策略分析和报告生成流程自动化。系统会根据用户输入选择工具，并在执行前做文件类型校验，避免用错误数据调用错误工具；同时记录工具调用轨迹和日志，提升可解释性和可审计性。  
> 
> 后续我计划接入 LLM Tool Calling 和 LangGraph，把当前规则路由升级成更接近真实生产系统的 Agent Workflow，并加入 RAG 研报分析能力。

---

## 14. 项目关键词

```text
Python
pandas
Agent
Tool Calling
Tool Registry
Rule-based Router
Parameter Parsing
Financial Data Analysis
Backtesting
Moving Average Strategy
Parameter Scan
Markdown Report
Trace
Audit Log
AI Pilot
Workflow Automation
```

---

## 15. 免责声明

本项目仅用于学习和技术演示，不构成任何投资建议。  
所有数据均为示例数据，策略结果不代表真实市场表现。
