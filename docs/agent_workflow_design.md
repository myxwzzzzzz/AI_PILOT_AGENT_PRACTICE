# Agent Workflow Design

本文件记录 `AI Pilot Agent Practice` 项目从单步 Tool Calling 走向多步 Agent Workflow 的设计方案。

第 65 课的目标是：**先设计，不立即实现复杂 workflow runner**。

当前项目已经具备：

```text
规则模式
LLM Tool Calling
RAG QA
keyword / embedding / hybrid retrieval
工具注册表
文件类型校验
参数解析
trace
logger
pytest 测试体系
```

接下来如果要让 Agent 能完成更复杂的任务，就需要从“单次工具调用”升级到“多步工作流”。

---

## 1. 当前系统的能力边界

当前系统更适合处理单步任务，例如：

```text
分析风险收益
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
扫描均线参数
生成策略研究总结报告
最大回撤是什么意思？
```

这些任务通常对应一个明确工具，或者对应一次 RAG QA。

当前系统不太适合直接处理复杂多步任务，例如：

```text
帮我完整分析这份股票数据，并生成一份策略研究报告。
```

因为这个任务其实包含多个步骤：

```text
1. 检查当前文件类型
2. 分析风险收益指标
3. 扫描均线参数
4. 选择较优参数
5. 生成回测报告
6. 生成图表
7. 生成策略研究总结
8. 输出最终说明
```

这些步骤目前都可以单独做，但还没有一个 workflow 层把它们自动串起来。

---

## 2. 什么是 Agent Workflow

在本项目中，Agent Workflow 指的是：

```text
把用户的一个复杂目标，拆成多个可控、可验证、可追踪的工具步骤，然后按顺序执行。
```

它不是让 LLM 随意自由行动，而是让系统在明确边界内执行预定义流程。

本项目的 workflow 仍然要遵守核心原则：

```text
LLM 不直接执行代码；
LLM 可以帮助理解目标或选择 workflow；
Python 负责 workflow 校验、步骤执行、状态记录、错误处理和 trace；
fallback 保证 workflow 某一步失败时能给出清晰结果。
```

---

## 3. 为什么当前先做设计，不直接写 workflow runner

原因有三个。

第一，当前已有工具较多，如果直接写 runner，容易把逻辑写乱。

第二，workflow 会影响主执行路径，应该先明确边界，避免破坏已经稳定的单步 Tool Calling。

第三，workflow 需要 trace、日志、错误处理和测试配套，不应该只写一个简单循环。

因此第 65 课只做设计文档。后续可以分阶段实现：

```text
第 66 课：实现最小 workflow planner
第 67 课：实现 workflow runner
第 68 课：接入 CLI 命令和 trace
第 69 课：补充 workflow 测试
```

课程编号可根据后续 roadmap 调整。

---

## 4. 第一版建议支持的 Workflow

第一版不建议做通用复杂规划器，而是先做一个固定模板 workflow：

```text
stock_strategy_research_workflow
```

中文名称：

```text
股票策略研究工作流
```

适合用户输入：

```text
帮我完整分析这份股票数据
帮我生成完整策略研究报告
对当前股票数据做一份策略研究总结
帮我分析风险收益、扫描参数并生成图表和报告
```

---

## 5. stock_strategy_research_workflow 设计

### 5.1 前置条件

当前文件必须是股票价格数据：

```text
required_file_type = stock_price
```

数据至少需要包含：

```text
date
close
```

如果当前文件不是股票数据，workflow 应该停止，并返回清晰提示。

例如：

```text
当前文件类型是 channel_data，不能执行股票策略研究工作流。请先切换到 data/stock_price_strategy.csv。
```

---

### 5.2 建议步骤

第一版 workflow 可以包含以下步骤：

```text
1. inspect_current_file
2. analyze_financial_metrics
3. scan_moving_average_parameters
4. generate_parameter_scan_report
5. generate_parameter_scan_chart
6. generate_strategy_summary_report
```

如果后续希望更完整，可以加入：

```text
7. generate_backtest_report_for_selected_params
8. generate_backtest_charts_for_selected_params
```

但第一版建议控制范围，不要一开始过大。

---

### 5.3 每一步对应工具

| workflow step | 对应工具 | 说明 |
| --- | --- | --- |
| inspect_current_file | file_inspector | 检查当前文件是否是股票数据 |
| analyze_financial_metrics | finance_metrics 工具 | 计算收益率、波动率、最大回撤、夏普比率 |
| scan_moving_average_parameters | 参数扫描工具 | 扫描不同 MA 参数组合 |
| generate_parameter_scan_report | 参数扫描报告工具 | 生成 Markdown 报告 |
| generate_parameter_scan_chart | 参数扫描图表工具 | 生成图表 |
| generate_strategy_summary_report | 策略总结报告工具 | 汇总策略研究结果 |

当前项目中这些能力大多已经存在于：

```text
finance_tools.py
tool_registry.py
response_formatter.py
```

第一版 workflow 可以直接复用现有工具，不必重复实现业务计算。

---

## 6. Workflow Planner 设计

建议新增：

```text
workflow_planner.py
```

它的职责不是执行工具，而是根据用户输入判断是否应该进入 workflow。

可能返回结构：

```python
{
    "workflow_name": "stock_strategy_research_workflow",
    "steps": [
        {"step_name": "analyze_financial_metrics", "tool_name": "generate_financial_report", "arguments": {}},
        {"step_name": "scan_moving_average_parameters", "tool_name": "scan_ma_parameters", "arguments": {"sort_by": "sharpe_ratio"}},
        {"step_name": "generate_parameter_scan_report", "tool_name": "generate_parameter_scan_report", "arguments": {"sort_by": "sharpe_ratio"}},
        {"step_name": "generate_parameter_scan_chart", "tool_name": "generate_parameter_scan_chart", "arguments": {"sort_by": "sharpe_ratio"}},
        {"step_name": "generate_strategy_summary_report", "tool_name": "generate_strategy_summary_report", "arguments": {}}
    ],
    "reason": "用户要求完整分析股票数据并生成策略研究结果。"
}
```

第一版 planner 可以先用规则判断，不一定调用 LLM。

例如命中以下关键词时进入 workflow：

```text
完整分析
完整策略报告
策略研究报告
一份完整报告
风险收益、参数扫描、图表、报告
```

后续再考虑 LLM workflow planner。

---

## 7. Workflow Runner 设计

建议新增：

```text
workflow_runner.py
```

它负责真正执行 workflow steps。

核心职责：

```text
1. 接收 workflow_plan
2. 逐步执行 step
3. 每一步都通过 tool_registry / llm_router 这类安全层执行
4. 记录每一步结果
5. 如果某一步失败，停止或进入 fallback
6. 汇总最终结果
7. 生成 workflow trace
```

注意：workflow runner 不应该绕过已有 guardrail。

不推荐：

```text
workflow_runner.py 直接调用 finance_tools.py 里的底层函数
```

推荐：

```text
workflow_runner.py → tool_registry / llm_router → tool handler
```

这样可以复用已有的文件类型检查、参数检查和工具注册机制。

---

## 8. Workflow Trace 设计

Workflow trace 应该能展示：

```text
workflow_name
workflow_reason
current_file_path
current_file_type
steps_total
steps_completed
steps_failed
每一步的 tool_name
每一步的 arguments
每一步的 status
每一步的 output summary
每一步的 report_path / chart_path
失败原因
fallback 信息
```

示例：

```text
Workflow: stock_strategy_research_workflow
Reason: 用户要求完整分析股票数据并生成策略研究报告。
Steps:
  1. analyze_financial_metrics ✅ success
     tool: generate_financial_report
     output: data/output/reports/financial_metrics_report.md
  2. scan_moving_average_parameters ✅ success
     tool: scan_ma_parameters
     sort_by: sharpe_ratio
  3. generate_parameter_scan_chart ✅ success
     output: data/output/charts/parameter_scan_sharpe_ratio.png
  4. generate_strategy_summary_report ✅ success
     output: data/output/reports/strategy_summary_report.md
```

---

## 9. Workflow Result 设计

workflow runner 最终可以返回：

```python
{
    "answer_type": "workflow_result",
    "workflow_name": "stock_strategy_research_workflow",
    "status": "success",
    "summary": "已完成股票策略研究工作流。",
    "steps": [...],
    "outputs": {
        "reports": [...],
        "charts": [...]
    },
    "trace": {...}
}
```

然后 `response_formatter.py` 可以新增对：

```text
answer_type == "workflow_result"
```

的格式化支持。

---

## 10. Workflow Fallback 设计

workflow 里可能失败的情况包括：

```text
当前文件类型不匹配
某个工具不存在
参数解析失败
报告生成失败
图表生成失败
某一步返回 error
```

第一版建议采用简单策略：

```text
关键步骤失败 → 停止 workflow，返回已完成步骤和失败原因
非关键步骤失败 → 记录失败，继续执行后续步骤
```

可以先把所有步骤都视为关键步骤，降低复杂度。

后续再区分：

```text
required step
optional step
```

---

## 11. CLI 接入方式

未来可以让用户自然语言触发 workflow，例如：

```text
帮我完整分析当前股票数据
生成完整策略研究报告
```

执行路径可能是：

```text
main.py
→ run_agent_task()
→ workflow_planner.py 判断是否为 workflow intent
→ workflow_runner.py 执行 workflow
→ response_formatter.py 格式化 workflow_result
→ trace_formatter.py 展示 workflow trace
→ logger.py 记录 workflow 日志
```

当前单步 Tool Calling 路径仍然保留，不应被 workflow 替代。

---

## 12. 与 Skill 的关系

Workflow 和 Skill 不是完全一样的概念。

可以这样理解：

```text
Tool = 单个能力
Skill = 一组相关能力的组合
Workflow = 按顺序执行一组能力的流程
```

例如：

```text
Tool: 生成 MA 回测图表
Skill: 均线策略研究能力
Workflow: 完整执行风险分析 → 参数扫描 → 图表 → 报告 → 总结
```

未来如果新增 `skill_registry.py`，可以让 workflow 引用 skill。

但当前建议先实现 workflow，不急着引入 skill registry。

---

## 13. 测试规划

后续实现时建议新增：

```text
tests/test_workflow_planner.py
tests/test_workflow_runner.py
tests/test_workflow_integration.py
```

测试重点：

```text
1. 用户输入“完整分析”能识别为 workflow
2. 普通单步任务不会误判为 workflow
3. 非股票文件不能执行股票 workflow
4. workflow steps 顺序正确
5. 某一步失败时能返回清晰错误
6. workflow_result 格式稳定
7. trace 包含每一步信息
```

---

## 14. 建议实现顺序

建议后续分三步实现。

### 第一步：最小 planner

新增：

```text
workflow_planner.py
tests/test_workflow_planner.py
```

只判断是否是 `stock_strategy_research_workflow`。

### 第二步：最小 runner

新增：

```text
workflow_runner.py
tests/test_workflow_runner.py
```

先支持按固定步骤执行，并返回 workflow_result。

### 第三步：接入主流程

修改：

```text
llm_agent_runner.py 或 run_agent_task()
response_formatter.py
trace_formatter.py
logger.py
```

让 CLI 可以自然语言触发 workflow。

---

## 15. 当前暂不做的事

第 65 课以及后续早期 workflow 阶段暂不建议做：

```text
不做完全开放式 LLM 自主规划
不接 MCP
不做长期记忆
不自动联网
不让 LLM 直接决定任意 Python 函数调用
不直接重写 main.py
不删除 rule router
不删除 mock selector
```

当前重点是：

```text
在已有工具和 guardrail 基础上，实现一个可控的多步 workflow。
```

---

## 16. 总结

当前项目已经完成 Tool Calling + RAG Agent 原型。

下一阶段的重点是从：

```text
用户一句话 → 一个工具
```

升级为：

```text
用户一个复杂目标 → 多个受控工具步骤 → 汇总结果
```

第一版 workflow 不追求智能复杂，而是追求：

```text
可控
可解释
可测试
可 fallback
可逐步扩展
```
