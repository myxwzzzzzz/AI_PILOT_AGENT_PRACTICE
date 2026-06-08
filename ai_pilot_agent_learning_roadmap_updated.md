# AI Pilot / Agent 工具调用与流程自动化学习路线（更新版）

> 这个文件用于在新的 ChatGPT 对话窗口中恢复上下文。  
> 如果上下文窗口耗尽，把这个 Markdown 文件发给新的对话，并说明：  
> **“请根据这个学习路线，继续带我完成 AI Pilot / Agent 工具调用与金融策略研究自动化项目。”**

更新时间：2026-06-08

---

## 1. 当前项目定位

项目名称：

**AI Pilot Agent：数据分析与金融策略研究自动化助手**

项目目标：

构建一个面向 AI Pilot / AI 应用 / Agent 工具调用岗位的项目原型。系统可以根据用户自然语言输入，自动选择工具、校验数据类型、解析参数、执行数据分析或策略研究任务，并生成自然语言回复、Markdown 报告、工具调用轨迹和工具调用日志。

当前版本是一个 **Rule-based Agent Prototype**，还没有接入真实大模型 API，但已经具备真实 Agent 系统的核心工程结构。

---

## 2. 当前系统总体流程

```text
用户自然语言输入
→ main.py 接收输入
→ 维护 current_file_path 状态
→ file_inspector.py 识别当前文件类型
→ tool_registry.py 匹配候选工具
→ parameter_parser.py 解析任务参数
→ router.py 校验文件类型和执行工具
→ tools.py / finance_tools.py 执行具体任务
→ response_formatter.py 生成自然语言回复
→ trace_formatter.py 展示工具调用轨迹
→ logger.py 记录工具调用日志
→ 必要时生成 Markdown 报告
```

---

## 3. 已完成阶段总览

| 阶段 | 内容 | 状态 |
|---|---|---|
| 第 1 阶段 | 基础工具函数：CSV 读取、统计、报告保存 | 已完成 |
| 第 2 阶段 | 渠道转化率分析工具 | 已完成 |
| 第 3 阶段 | 自动生成渠道分析 Markdown 报告 | 已完成 |
| 第 4 阶段 | Rule-based Router 自然语言任务路由 | 已完成 |
| 第 5 阶段 | 自然语言回复格式化 | 已完成 |
| 第 6 阶段 | 交互式命令行助手 | 已完成 |
| 第 7 阶段 | 文件状态管理：支持切换当前文件 | 已完成 |
| 第 8 阶段 | 工具调用日志 | 已完成 |
| 第 9 阶段 | 金融指标工具 | 已完成 |
| 第 10 阶段 | 金融工具接入主助手 | 已完成 |
| 第 11 阶段 | 文件类型识别与任务兼容性校验 | 已完成 |
| 第 12 阶段 | Tool Registry 工具注册表 | 已完成 |
| 第 13 阶段 | Tool Call Trace 工具调用轨迹 | 已完成 |
| 第 14 阶段 | 均线策略回测工具 | 已完成 |
| 第 15 阶段 | 回测工具接入主助手 | 已完成 |
| 第 16 阶段 | 自然语言解析 MA 参数 | 已完成 |
| 第 17 阶段 | 均线参数批量扫描 | 已完成 |
| 第 18 阶段 | 参数扫描工具接入主助手 | 已完成 |
| 第 19 阶段 | 支持参数扫描排序指标解析 | 已完成 |
| 第 20 阶段 | 策略研究总结报告工具 | 已完成 |
| 第 21 阶段 | 策略研究总结报告接入主助手 | 已完成 |
| 第 22 阶段 | 第一版 README.md 项目文档 | 已完成 |

---

## 4. 当前项目文件结构

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

## 5. 当前已实现模块说明

### 5.1 `main.py`

职责：

- 启动命令行助手；
- 接收用户自然语言输入；
- 维护当前文件路径 `current_file_path`；
- 处理切换文件、查看日志、查看工具、开启/关闭轨迹等命令；
- 调用 `router.py` 路由任务；
- 调用 `response_formatter.py` 输出自然语言回复；
- 调用 `trace_formatter.py` 展示工具调用轨迹；
- 调用 `logger.py` 记录日志。

---

### 5.2 `file_inspector.py`

职责：

- 读取 CSV 字段；
- 自动识别文件类型。

支持识别：

| 字段 | 文件类型 |
|---|---|
| `date, channel, visits, signups, payments` | `channel_data` |
| `date, close` | `stock_price` |
| 其他字段 | `unknown` |

---

### 5.3 `tool_registry.py`

职责：

- 统一管理工具名称、描述、关键词、所需文件类型和执行函数；
- 支持 `查看工具`；
- 为后续 LLM Tool Calling 做准备。

每个工具结构类似：

```python
{
    "name": "run_moving_average_backtest",
    "description": "运行简单均线策略回测，支持 MA 参数。",
    "keywords": ["均线策略", "策略回测", "运行回测", "回测"],
    "required_file_type": "stock_price",
    "required_file_type_name": "股票价格数据",
    "handler": run_moving_average_backtest
}
```

---

### 5.4 `router.py`

职责：

- 根据用户输入从 Tool Registry 匹配工具；
- 调用 `file_inspector.py` 识别文件类型；
- 校验任务与文件类型是否兼容；
- 调用 `parameter_parser.py` 解析 MA 参数和扫描排序指标；
- 执行工具；
- 返回工具结果和 trace。

---

### 5.5 `parameter_parser.py`

职责：

- 从自然语言中解析均线参数；
- 从自然语言中解析参数扫描排序指标。

支持：

```text
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
用 5 日均线和 10 日均线做回测
按收益率扫描均线参数
按最大回撤生成参数扫描报告
```

---

### 5.6 `tools.py`

职责：渠道数据分析。

已实现：

- `read_csv_file()`
- `summarize_csv()`
- `analyze_channel_conversion()`
- `generate_channel_analysis_report()`

---

### 5.7 `finance_tools.py`

职责：金融指标、回测、参数扫描、策略总结。

已实现：

- `read_stock_price_data()`
- `calculate_stock_metrics()`
- `generate_stock_metrics_report()`
- `run_moving_average_backtest()`
- `generate_backtest_report()`
- `optimize_moving_average_parameters()`
- `generate_parameter_scan_report()`
- `generate_strategy_research_summary()`

---

### 5.8 `response_formatter.py`

职责：

- 将工具返回的字典结果转换成用户可读的自然语言回复。

已支持：

- CSV 读取回复；
- 数据统计回复；
- 渠道分析回复；
- 渠道报告生成回复；
- 股票价格读取回复；
- 金融指标分析回复；
- 金融报告生成回复；
- 均线回测回复；
- 回测报告回复；
- 参数扫描回复；
- 参数扫描报告回复；
- 策略研究总结报告回复。

---

### 5.9 `trace_formatter.py`

职责：

- 将 `router.py` 返回的 trace 格式化输出；
- 展示工具调用过程。

轨迹包含：

- 用户输入；
- 匹配方式；
- 命中关键词；
- 选择原因；
- 选择工具；
- 当前文件；
- 当前文件类型；
- 工具要求文件类型；
- MA 参数解析；
- 扫描排序解析；
- 实际传入参数；
- 文件类型校验；
- 工具执行状态。

---

### 5.10 `logger.py`

职责：

- 记录工具调用日志；
- 日志文件为：

```text
data/logs/tool_calls.jsonl
```

支持命令：

```text
查看日志
```

---

## 6. 当前支持的用户输入示例

### 6.1 基础数据分析

```text
帮我读取这个 CSV 文件
帮我看一下这个数据的缺失值和统计信息
分析渠道转化率
生成渠道分析报告
```

---

### 6.2 文件切换

```text
切换文件 data/channel_data.csv
切换文件 data/channel_data_new.csv
切换文件 data/stock_price.csv
切换文件 data/stock_price_strategy.csv
```

---

### 6.3 金融指标分析

```text
读取股票价格数据
分析风险收益
生成金融指标报告
```

---

### 6.4 策略回测

```text
运行均线策略回测
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
用 5 日均线和 10 日均线做回测
```

---

### 6.5 参数扫描

```text
扫描均线参数
优化均线策略参数
按收益率扫描均线参数
按超额收益优化均线策略
按最大回撤生成参数扫描报告
```

---

### 6.6 策略研究总结

```text
生成策略研究总结报告
生成按收益率排序的策略研究报告
生成按最大回撤排序的策略研究报告
总结一下这个策略研究结果
```

---

### 6.7 工具与轨迹

```text
查看工具
查看日志
开启轨迹
关闭轨迹
```

---

## 7. 当前关键测试结果

### 7.1 渠道分析

测试数据：

```text
data/channel_data.csv
```

结果：

- 小红书在注册转化率、付费转化率、注册到付费转化率上均表现最好；
- 成功生成 `data/channel_analysis_report.md`。

---

### 7.2 金融指标分析

测试数据：

```text
data/stock_price.csv
```

结果：

- 区间收益率约 15%；
- 成功计算年化波动率、最大回撤、夏普比率；
- 成功生成 `data/stock_metrics_report.md`。

---

### 7.3 均线回测

测试数据：

```text
data/stock_price_strategy.csv
```

默认 MA3-MA5：

- 策略收益率约 22.27%；
- 买入持有收益率约 41.00%；
- 策略跑输买入持有；
- 最大回撤约 -4.84%。

MA5-MA10：

- 策略收益率约 22.61%；
- 买入持有收益率约 41.00%；
- 最新信号为持仓。

---

### 7.4 参数扫描

默认扫描：

```text
short_windows = [3, 5, 7]
long_windows = [10, 15, 20]
```

当前按夏普比率排序，最佳组合为：

```text
MA3-MA10
```

但多组参数结果接近，原因是测试数据为明显单边上涨趋势，样本区分度不足。

---

### 7.5 策略研究总结报告

生成文件：

```text
data/strategy_research_summary.md
```

核心结论：

- 标的买入持有收益约 41.00%；
- 默认 MA3-MA5 策略收益约 22.27%；
- 最佳参数组合 MA3-MA10 策略收益约 22.61%；
- 均线策略整体未产生正超额收益；
- 建议扩大样本区间、加入震荡和下跌行情数据，并引入风控或过滤条件。

---

## 8. 当前项目最重要的面试表达

可以这样说：

> 我做了一个面向 AI Pilot 场景的 Agent 工具调用原型。系统支持命令行自然语言输入，通过文件类型识别、Tool Registry、参数解析和工具调用轨迹，实现渠道数据分析、金融风险收益分析、均线策略回测、参数扫描和策略研究总结报告生成。  
> 
> 项目重点不是训练大模型，而是模拟真实业务中 Agent 如何把数据处理、策略分析和报告生成流程自动化。系统会根据用户输入选择工具，并在执行前做文件类型校验，避免用错误数据调用错误工具；同时记录工具调用轨迹和日志，提升可解释性和可审计性。  
> 
> 后续我计划接入 LLM Tool Calling 和 LangGraph，把当前规则路由升级成更接近真实生产系统的 Agent Workflow，并加入 RAG 研报分析能力。

---

## 9. 当前能力边界

当前版本限制：

1. 路由仍基于关键词规则，不是真正 LLM Tool Calling；
2. 金融数据为本地 CSV 示例数据；
3. 回测未考虑手续费、滑点和冲击成本；
4. 策略只支持简单均线策略；
5. 参数扫描存在样本内过拟合风险；
6. 样本较短，夏普比率和年化波动率不宜过度解读；
7. 当前为命令行交互，尚未提供 Web UI；
8. 尚未接入 RAG 文档问答；
9. 尚未接入真实行情接口或数据库。

---

## 10. 下一步推荐学习路线

### 第 23 阶段：整理简历项目描述

目标：

- 将当前项目压缩成 2-4 条简历 bullet；
- 准备 AI Pilot 岗位版本；
- 准备数据分析岗位版本；
- 准备 AI 应用 / Agent 岗位版本。

---

### 第 24 阶段：增加 Streamlit 可视化界面

目标：

- 页面选择数据文件；
- 输入自然语言任务；
- 展示自然语言回复；
- 展示工具调用轨迹；
- 展示生成报告下载链接。

---

### 第 25 阶段：增加图表输出

目标：

- 策略净值曲线；
- 买入持有基准曲线；
- 回撤曲线；
- 参数扫描对比图；
- 渠道转化率柱状图。

---

### 第 26 阶段：接入 RAG 文档分析

目标：

- 读取研报 PDF / TXT；
- 切分文本；
- 构建向量索引；
- 检索相关片段；
- 生成带引用的投研摘要；
- 输出风险提示。

---

### 第 27 阶段：接入 LLM Tool Calling

目标：

- 将 Tool Registry 转为 LLM tool schema；
- 用大模型替代关键词匹配；
- 支持更自然的任务理解；
- 保留文件类型校验和 trace。

---

### 第 28 阶段：接入 LangGraph

目标：

- 构建可控 workflow；
- 实现多步骤任务；
- 支持失败重试；
- 支持人工确认；
- 支持更复杂的策略研究流程。

---

## 11. 新窗口继续学习提示词

如果换新窗口，可以直接发：

> 我正在做一个 AI Pilot / Agent 工具调用与金融策略研究自动化项目。这个 Markdown 是当前学习路线和项目进度。请先阅读，然后从第 23 阶段“整理简历项目描述”继续带我做，或者根据当前进度继续优化 README、代码结构、Streamlit 界面、RAG 文档分析和 LLM Tool Calling。

---

## 12. 当前状态一句话总结

目前项目已经完成：

**Rule-based Agent Prototype + Tool Registry + 文件类型校验 + 参数解析 + 渠道分析 + 金融指标分析 + 均线回测 + 参数扫描 + 策略研究总结报告 + 工具调用轨迹 + 工具调用日志 + 第一版 README。**

下一步建议：

**先整理简历项目描述，再考虑做 Streamlit 可视化界面或 RAG 文档分析。**
