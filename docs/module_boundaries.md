# Module Boundaries

本文件用于说明 AI Pilot Agent Practice 项目中各模块的职责边界。

当前阶段：v0.3
核心能力：Rule-based Router + LLM Tool Calling + RAG QA + fallback + trace

---

## 1. 总体架构

当前系统包含三条主要路径：

```text
规则模式：
用户输入
→ router.py
→ tool_registry.py
→ 工具执行
→ response_formatter.py

LLM Tool Calling 模式：
用户输入
→ llm_agent_runner.py
→ llm_tool_selector.py
→ real_llm_tool_selector.py / mock_llm_tool_selector.py
→ llm_router.py
→ tool_registry.py
→ 工具执行
→ response_formatter.py

RAG QA 模式：
用户输入
→ llm_agent_runner.py
→ rag_retriever.py
→ rag_qa.py
→ rag_llm_answerer.py
→ response_formatter.py
```

---

## 2. main.py 的职责边界

`main.py` 是 CLI 主入口。

它只负责：

```text
初始化 AppState
打印启动说明
读取用户输入
调用 handle_cli_command 处理系统命令
调用 run_agent_task 执行用户任务
格式化输出
写日志
展示 trace
```

它不应该直接承担：

```text
工具匹配逻辑
LLM prompt 构造
RAG 检索逻辑
具体数据分析计算
回测计算
图表生成
报告生成
```

这些逻辑应交给其他模块。

---

## 3. CLI 层

### cli_state.py

负责保存 CLI 状态：

```text
current_file_path
show_trace
use_llm_mode
llm_selector_mode
use_rag_mode
```

### cli_command_handler.py

负责处理系统命令，例如：

```text
切换文件
查看当前状态
开启/关闭 LLM 模式
使用真实/模拟 LLM
开启/关闭 RAG 模式
开启/关闭轨迹
查看工具
查看日志
检查 LLM 连接
退出
```

CLI 层不负责执行数据分析工具，也不负责调用 LLM 工具选择器。

---

## 4. 工具能力层

工具能力层负责真实计算和文件输出。

| 文件                    | 职责                            |
| --------------------- | ----------------------------- |
| `tools.py`            | 渠道转化数据分析                      |
| `finance_tools.py`    | 金融指标、均线回测、参数扫描、图表、报告          |
| `tool_registry.py`    | 注册工具名称、描述、关键词、文件类型要求和 handler |
| `file_inspector.py`   | 判断当前 CSV 文件类型                 |
| `parameter_parser.py` | 从自然语言中解析 MA 参数和扫描排序指标         |

工具能力层不应该关心用户当前使用规则模式、LLM 模式还是 RAG 模式。

---

## 5. 规则路由层

### router.py

`router.py` 是旧规则路由器。

当前角色：

```text
1. 规则模式下的主路由器
2. LLM 失败后的最终 fallback
3. Rule-based Agent 到 LLM Agent 的演进对照
```

它不是废弃文件，当前不应删除。

但它不再是唯一主路径。开启 LLM 模式后，主要任务会进入 `llm_agent_runner.py`。

---

## 6. LLM Tool Calling 层

### llm_tool_schema.py

负责把 `tool_registry.py` 转成 LLM 可读的 Tool Schema。

### real_llm_tool_selector.py

负责调用 DeepSeek，判断用户意图、选择工具并生成参数。

它只应该返回结构化结果，例如：

```json
{
  "intent_type": "tool_call",
  "tool_name": "generate_backtest_report",
  "arguments": {
    "short_window": 5,
    "long_window": 10
  },
  "reason": "用户要求生成 MA5-MA10 回测报告。"
}
```

它不负责执行工具。

### mock_llm_tool_selector.py

本地规则版 LLM selector。

当前角色：

```text
1. DeepSeek 不可用时的 fallback selector
2. 没有 API Key 时的本地演示方案
3. 对比真实 LLM selector 的教学模块
```

它不是废弃文件，当前不应删除。

### llm_tool_selector.py

统一 selector 入口。

负责根据 mode 选择：

```text
mode="mock" → mock_llm_tool_selector.py
mode="real" → real_llm_tool_selector.py
```

### llm_router.py

负责执行 LLM 返回的 tool call。

它必须做安全校验：

```text
工具是否存在
当前文件类型是否匹配
参数是否合法
是否允许执行
```

LLM 不能绕过 `llm_router.py` 直接执行工具。

### llm_agent_runner.py

LLM Agent 总调度器。

负责：

```text
调用 selector
处理 Tool Calling
处理 RAG QA
处理 fallback
记录 trace metadata
```

它是当前 v0.3 的核心调度模块。

---

## 7. RAG 层

### documents/

本地知识文档目录。

当前主要包含：

```text
ma_strategy_notes.md
agent_tool_usage_notes.md
```

### rag_document_loader.py

负责读取 Markdown / txt 文档并切块。

### rag_retriever.py

关键词检索版 RAG Retriever。

当前还没有使用 embedding 或向量数据库。

### rag_qa.py

RAG QA 入口。

负责：

```text
接收用户问题和 retrieved_chunks
优先调用 LLM 生成回答
LLM 失败时 fallback 到本地规则回答
返回 answer、retrieved_chunks、answer_source
```

### rag_llm_answerer.py

负责调用 DeepSeek，基于检索片段生成自然语言回答。

它不负责检索，也不负责工具执行。

---

## 8. 格式化与日志层

| 文件                      | 职责                                         |
| ----------------------- | ------------------------------------------ |
| `response_formatter.py` | 将工具结果或 RAG QA 结果转成用户可读回复                   |
| `trace_formatter.py`    | 展示规则路由、LLM Tool Calling、RAG QA、fallback 轨迹 |
| `logger.py`             | 记录工具调用日志                                   |

这些模块不应该承担工具选择或业务计算逻辑。

---

## 9. fallback 边界

当前 fallback 关系如下：

```text
Tool Calling fallback：
real selector 失败
→ mock selector
→ rule router

RAG QA fallback：
DeepSeek RAG answer 失败
→ 本地规则 RAG answer

模式 fallback：
LLM 模式关闭
→ 直接使用 rule router
```

---

## 10. 当前不建议删除的文件

| 文件                          | 原因                           |
| --------------------------- | ---------------------------- |
| `router.py`                 | 规则模式和最终 fallback 仍依赖         |
| `mock_llm_tool_selector.py` | real selector 失败时仍依赖         |
| `parameter_parser.py`       | mock selector 和规则 router 仍依赖 |
| `llm_tool_schema.py`        | real selector prompt 仍依赖     |
| `llm_health_check.py`       | 调试 API 环境仍然重要                |

---

## 11. 后续重构方向

当前优先级：

```text
1. 保持现有功能稳定
2. 不急于删除 fallback 文件
3. 先完善文档和测试
4. 再考虑拆分大型文件
```

后续可以考虑：

```text
finance_tools.py 拆分为：
- finance_metrics.py
- backtest_tools.py
- scan_tools.py
- chart_tools.py
- report_tools.py

tests/ 拆分为：
- tests/tools/
- tests/llm/
- tests/rag/
- tests/integration/
```

但当前 v0.3 阶段暂不执行大规模移动，避免破坏已稳定的路径和导入关系。
