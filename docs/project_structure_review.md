# Project Structure Review

本文件用于记录 AI Pilot Agent Practice 项目的当前文件结构、模块职责和后续清理计划。

当前阶段：v0.3
当前重点：LLM Tool Calling + RAG QA + fallback + trace

---

## 1. 当前结构判断

当前项目已经从一个简单 CSV 分析脚本演进为多路径 Agent 系统。

系统现在存在三条主要执行路径：

```text
规则模式：
用户输入 → router.py → 工具执行

LLM Tool Calling 模式：
用户输入 → llm_agent_runner.py → llm_tool_selector.py → real/mock selector → llm_router.py → 工具执行

RAG QA 模式：
知识性问题 → llm_agent_runner.py → rag_retriever.py → rag_qa.py → rag_llm_answerer.py → 回答生成
```

因此，当前文件数量变多是正常现象，但需要明确哪些是核心文件、哪些是 fallback 文件、哪些是后续可整理对象。

---

## 2. 核心入口文件

| 文件                 | 当前作用                                               | 处理建议                |
| ------------------ | -------------------------------------------------- | ------------------- |
| `main.py`          | CLI 主入口，负责用户输入、模式切换、文件状态和结果展示                      | 保留，但需要在后续课程拆分命令处理逻辑 |
| `config.py`        | 统一管理 data、output、reports、charts、logs、documents 等路径 | 保留                  |
| `requirements.txt` | 项目依赖声明                                             | 保留并持续维护             |
| `.gitignore`       | 忽略缓存、日志、输出文件                                       | 保留                  |

---

## 3. 工具能力层

| 文件                      | 当前作用                                  | 处理建议                       |
| ----------------------- | ------------------------------------- | -------------------------- |
| `tools.py`              | 渠道转化数据分析工具                            | 保留                         |
| `finance_tools.py`      | 金融指标、均线回测、参数扫描、图表、报告工具                | 保留，但后续可考虑拆分为多个 finance 子模块 |
| `tool_registry.py`      | 工具注册表，连接自然语言任务和工具 handler             | 保留                         |
| `file_inspector.py`     | 判断当前 CSV 文件类型                         | 保留                         |
| `parameter_parser.py`   | 解析 MA 参数和扫描排序指标                       | 保留                         |
| `response_formatter.py` | 格式化工具结果和 RAG QA 结果                    | 保留                         |
| `trace_formatter.py`    | 格式化规则路由、LLM Tool Calling、RAG QA trace | 保留                         |
| `logger.py`             | 写入工具调用日志                              | 保留                         |

---

## 4. 规则路由与 fallback 层

| 文件                          | 当前作用                                          | 处理建议     |
| --------------------------- | --------------------------------------------- | -------- |
| `router.py`                 | 旧规则路由器；在不开启 LLM 模式时使用；也作为 LLM 失败后的最终 fallback | 暂时保留，不删除 |
| `mock_llm_tool_selector.py` | 本地规则模拟 LLM selector；DeepSeek 不可用时 fallback    | 暂时保留，不删除 |

说明：

`router.py` 和 `mock_llm_tool_selector.py` 看起来像旧文件，但当前仍然有实际价值：

```text
1. 支持无 API Key 的本地演示
2. 支持 DeepSeek 网络失败时 fallback
3. 作为规则 Agent 到 LLM Agent 的演进对照
```

因此当前阶段不建议删除。后续可以考虑将它们标注为 fallback 模块，而不是 legacy 模块。

---

## 5. LLM Tool Calling 层

| 文件                          | 当前作用                                             | 处理建议             |
| --------------------------- | ------------------------------------------------ | ---------------- |
| `llm_tool_schema.py`        | 将 Tool Registry 转换成 LLM 可读 Tool Schema           | 保留               |
| `llm_router.py`             | 接收 LLM tool_call，做工具存在性、文件类型、参数校验并执行工具           | 保留               |
| `llm_tool_selector.py`      | mock / real selector 的统一入口                       | 保留               |
| `real_llm_tool_selector.py` | DeepSeek 真实 LLM selector                         | 保留               |
| `llm_agent_runner.py`       | LLM Agent 总调度器，负责 Tool Calling、RAG QA 和 fallback | 保留，当前是 v0.3 核心模块 |
| `llm_health_check.py`       | 检查 DeepSeek API Key、连接和 JSON 返回能力                | 保留               |

---

## 6. RAG 层

| 文件 / 目录                  | 当前作用                             | 处理建议 |
| ------------------------ | -------------------------------- | ---- |
| `documents/`             | 本地知识文档目录                         | 保留   |
| `rag_document_loader.py` | 读取 Markdown / txt 文档并切块          | 保留   |
| `rag_retriever.py`       | 关键词检索版 RAG Retriever             | 保留   |
| `rag_qa.py`              | RAG QA 总入口，负责优先 LLM 回答、失败后本地规则回答 | 保留   |
| `rag_llm_answerer.py`    | 使用 DeepSeek 基于 RAG 检索片段生成自然语言回答  | 保留   |

说明：

当前 RAG 仍是关键词检索版本，尚未进入 embedding / 向量数据库阶段。
但当前结构已经足够支持最小可用 RAG QA。

---

## 7. 数据与输出目录

| 路径                              | 当前作用               | 处理建议    |
| ------------------------------- | ------------------ | ------- |
| `data/channel_data.csv`         | 渠道转化样例数据           | 保留      |
| `data/channel_data_new.csv`     | 第二份渠道转化样例数据        | 保留      |
| `data/stock_price.csv`          | 基础股票价格样例数据         | 保留      |
| `data/stock_price_strategy.csv` | 均线策略回测样例数据         | 保留      |
| `data/output/reports/`          | 运行时生成的 Markdown 报告 | 不提交 Git |
| `data/output/charts/`           | 运行时生成的图表           | 不提交 Git |
| `data/logs/`                    | 工具调用日志             | 不提交 Git |

---

## 8. 测试文件

当前 `tests/` 下包含多个阶段性测试文件。

| 类型      | 示例                                                                    | 处理建议                |
| ------- | --------------------------------------------------------------------- | ------------------- |
| 金融工具测试  | `test_finance_tools.py`, `test_backtest.py`                           | 保留                  |
| 图表与报告测试 | `test_charts.py`, `test_parameter_scan_chart.py`                      | 保留                  |
| LLM 测试  | `test_llm_router.py`, `test_llm_tool_selector.py`                     | 保留                  |
| RAG 测试  | `test_rag_retriever.py`, `test_rag_qa.py`, `test_rag_llm_answerer.py` | 保留                  |
| 骨架/过渡测试 | `test_real_llm_selector_skeleton.py`                                  | 后续可考虑标记为 legacy 或删除 |

后续建议：

```text
tests/
├─ test_tools_*.py
├─ test_llm_*.py
├─ test_rag_*.py
└─ test_integration_*.py
```

当前阶段先不移动，避免影响路径和导入。

---

## 9. 当前不建议删除的文件

以下文件虽然看起来像过渡文件，但当前仍建议保留：

| 文件                          | 不删除原因                         |
| --------------------------- | ----------------------------- |
| `router.py`                 | 规则模式和最终 fallback 仍然依赖         |
| `mock_llm_tool_selector.py` | DeepSeek 不可用时 fallback 仍然依赖   |
| `llm_tool_schema.py`        | real selector prompt 仍然依赖     |
| `llm_health_check.py`       | 调试 API 连接问题很重要                |
| `parameter_parser.py`       | mock selector 和规则 router 仍然依赖 |

---

## 10. 后续可清理方向

后续建议按以下顺序清理：

### 第一步：清理 `main.py`

当前 `main.py` 承担了太多职责：

```text
启动提示
命令解析
文件切换
模式切换
LLM 健康检查
任务执行
结果展示
trace 展示
日志记录
```

后续可拆分为：

```text
cli_commands.py       处理命令解析和模式切换
cli_state.py          管理 current_file_path、use_llm_mode、use_rag_mode
main.py               只保留主循环
```

---

### 第二步：明确 fallback 模块命名

当前：

```text
router.py
mock_llm_tool_selector.py
```

建议暂时保留名称，但在文档中标注为 fallback。

后续如果要更清楚，可以考虑：

```text
router.py → rule_router.py
mock_llm_tool_selector.py → fallback_mock_selector.py
```

但重命名会影响 import，暂时不建议立即进行。

---

### 第三步：整理 tests

后续可以把测试文件分组：

```text
tests/
├─ tools/
├─ llm/
├─ rag/
└─ integration/
```

当前先不移动。

---

### 第四步：考虑拆分 `finance_tools.py`

`finance_tools.py` 当前承担：

```text
股票指标计算
均线回测
参数扫描
报告生成
图表生成
策略总结
```

后续可以拆为：

```text
finance_metrics.py
backtest_tools.py
scan_tools.py
chart_tools.py
report_tools.py
```

但当前不急，避免过早重构。

---

## 11. 当前推荐结论

当前 v0.3 阶段，建议：

```text
不删除核心文件
不删除 fallback 文件
不移动 tests
先清理 main.py
再整理文档
最后再考虑模块拆分
```

下一步优先级：

```text
1. 清理 main.py
2. 明确模式切换和命令处理边界
3. 全量回归测试
4. 打 v0.3 稳定标签
```
