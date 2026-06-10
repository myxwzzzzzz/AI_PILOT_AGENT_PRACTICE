# AI Pilot Agent Practice

一个面向 **AI Pilot / Agent 工具调用 / 数据分析自动化** 场景的学习型项目。

项目从最基础的 CSV 数据分析助手开始，逐步演进为支持：

* Rule-based Router
* Tool Registry
* 文件类型识别
* 金融指标分析
* 均线策略回测
* 参数扫描
* 图表生成
* Markdown 报告生成
* LLM Tool Calling
* DeepSeek 真实大模型接入
* RAG 文档检索
* RAG 知识问答
* fallback 容错机制
* 工具调用 trace
* 工具日志记录

的 AI Pilot Agent 原型系统。

---

## 1. 项目目标

本项目目标不是简单调用大模型聊天，而是构建一个具有明确边界和安全执行逻辑的 Agent 系统。

核心思想是：

```text
LLM 负责理解用户意图、选择工具、生成参数或基于文档生成回答；
Python 负责状态管理、文件校验、参数校验、工具执行、日志和 trace；
RAG 负责把本地知识文档注入回答和工具选择过程。
```

也就是说，本项目中的 LLM 不直接执行代码，也不直接操作文件，而是作为“决策层”参与 Agent 工作流。

---

## 2. 当前版本状态：v0.3

当前项目已经从最初的 Rule-based Agent Prototype，升级为支持 **LLM Tool Calling + RAG QA** 的 AI Pilot Agent 原型。

v0.3 版本新增能力包括：

* 接入 DeepSeek `deepseek-v4-pro` 作为真实 LLM Selector；
* 支持 OpenAI-compatible API 调用方式；
* 支持 LLM 根据用户自然语言选择工具并生成参数；
* 保留 Python 侧安全执行层，包括工具存在性校验、文件类型校验和参数合法性校验；
* 支持 LLM 调用失败时自动 fallback 到 mock selector 或旧规则 router；
* 新增 LLM API 健康检查工具，用于检查 API Key、模型连接和 JSON 返回能力；
* 新增本地 RAG 文档层，支持读取 `documents/` 下的 Markdown / txt 知识文档；
* 新增关键词检索版 RAG Retriever；
* 支持知识性问题走 RAG QA，执行性问题走 Tool Calling；
* 支持 DeepSeek 基于 RAG 检索片段生成自然语言回答；
* DeepSeek 不可用时，RAG QA 会 fallback 到本地规则回答。

当前系统已经具备三条主要执行路径：

```text
规则模式：
用户输入 → router.py → 工具执行

LLM Tool Calling 模式：
用户输入 → DeepSeek / mock selector → llm_router.py → 工具执行

RAG QA 模式：
知识性问题 → RAG 检索 → DeepSeek 生成回答 → 本地知识片段溯源
```

---

## 3. 当前支持的数据能力

### 3.1 渠道转化分析

适用于包含以下字段的 CSV：

```text
date, channel, visits, signups, payments
```

支持能力：

* 读取 CSV 文件；
* 查看字段、缺失值和统计信息；
* 分析各渠道访问量、注册量、支付量；
* 计算注册率、支付率、注册到支付转化率；
* 判断表现最好的渠道；
* 生成渠道分析 Markdown 报告。

---

### 3.2 股票价格与风险收益分析

适用于包含以下字段的 CSV：

```text
date, close
```

支持能力：

* 读取股票价格数据；
* 计算总收益率；
* 计算年化波动率；
* 计算最大回撤；
* 计算夏普比率；
* 生成金融指标报告。

---

### 3.3 均线策略回测

支持基于股票价格数据运行 MA 均线策略，例如：

```text
MA3-MA5
MA5-MA10
MA3-MA10
```

支持能力：

* 运行均线策略回测；
* 生成回测 Markdown 报告；
* 生成策略净值曲线；
* 生成最大回撤曲线；
* 扫描多个均线参数组合；
* 按夏普比率、策略收益率、超额收益、最大回撤排序；
* 生成参数扫描图表；
* 生成策略研究总结报告。

---

## 4. LLM Tool Calling 设计

项目中的 LLM Tool Calling 并不是让大模型直接执行任务，而是让大模型返回结构化工具调用结果。

示例：

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

然后 Python 系统会继续执行：

```text
检查工具是否存在
→ 检查当前文件类型是否匹配
→ 校验参数是否合法
→ 执行真实 Python 工具函数
→ 格式化回复
→ 记录 trace 和日志
```

这样可以避免 LLM 直接拥有执行权，提高系统可控性。

---

## 5. RAG QA 设计

RAG 模式用于处理知识性问题，例如：

```text
MA5-MA10 策略适合震荡行情吗？
最大回撤是什么意思？
如果用户问最大回撤，sort_by 应该是什么？
```

处理流程：

```text
用户输入
→ 本地 intent guard 判断是否为知识问答
→ 检索 documents/ 下的相关文档片段
→ DeepSeek 基于检索片段生成回答
→ 如果 DeepSeek 不可用，fallback 到本地规则回答
→ 输出答案和参考片段
```

示例回答会附带本地知识来源：

```text
参考的本地知识片段：
- ma_strategy_notes.md::chunk_0
- agent_tool_usage_notes.md::chunk_0
```

---

## 6. 项目目录结构

当前核心结构如下：

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
├─ rag_qa.py
├─ rag_llm_answerer.py
├─ file_inspector.py
├─ parameter_parser.py
├─ response_formatter.py
├─ trace_formatter.py
├─ logger.py
├─ tools.py
├─ finance_tools.py
├─ requirements.txt
├─ README.md
├─ data/
│  ├─ channel_data.csv
│  ├─ channel_data_new.csv
│  ├─ stock_price.csv
│  ├─ stock_price_strategy.csv
│  ├─ logs/
│  └─ output/
│     ├─ reports/
│     └─ charts/
├─ documents/
│  ├─ ma_strategy_notes.md
│  └─ agent_tool_usage_notes.md
├─ docs/
│  ├─ architecture.md
│  ├─ usage_example.md
│  └─ ai_pilot_agent_learning_roadmap_updated.md
└─ tests/
```

---

## 7. v0.3 核心模块说明

| 文件                          | 作用                                                |
| --------------------------- | ------------------------------------------------- |
| `main.py`                   | 命令行交互入口，负责模式切换、用户输入、文件状态和结果展示                     |
| `router.py`                 | 旧规则路由器，作为规则模式和最终 fallback 保留                      |
| `tool_registry.py`          | 工具注册表，统一管理工具名称、描述、关键词、文件类型要求和 handler             |
| `llm_tool_schema.py`        | 将工具注册表转换为 LLM 可读 Tool Schema                      |
| `mock_llm_tool_selector.py` | 本地规则版 LLM selector，用于 API 不可用时 fallback           |
| `real_llm_tool_selector.py` | DeepSeek 真实 LLM selector，根据用户输入和 Tool Schema 选择工具 |
| `llm_tool_selector.py`      | mock / real selector 的统一入口                        |
| `llm_router.py`             | LLM Tool Call 的安全执行层，负责工具校验、文件类型校验和参数校验           |
| `llm_agent_runner.py`       | LLM Agent 总调度器，负责 Tool Calling、RAG QA 和 fallback  |
| `llm_health_check.py`       | DeepSeek API 健康检查工具                               |
| `rag_document_loader.py`    | 读取 `documents/` 下的本地知识文档并切块                       |
| `rag_retriever.py`          | 关键词检索版 RAG Retriever                              |
| `rag_qa.py`                 | RAG QA 入口，负责知识问答路径                                |
| `rag_llm_answerer.py`       | 使用 DeepSeek 基于 RAG 检索片段生成自然语言回答                   |
| `file_inspector.py`         | 根据 CSV 字段识别当前文件类型                                 |
| `parameter_parser.py`       | 从自然语言中解析 MA 参数和扫描排序指标                             |
| `tools.py`                  | 渠道数据分析工具                                          |
| `finance_tools.py`          | 金融指标、均线回测、参数扫描、图表和报告生成工具                          |
| `response_formatter.py`     | 将工具结果或 RAG QA 结果格式化为用户可读回复                        |
| `trace_formatter.py`        | 展示规则路由、LLM Tool Calling、RAG QA 和 fallback 轨迹      |
| `logger.py`                 | 记录工具调用日志                                          |
| `config.py`                 | 统一管理数据、输出、日志、图表、报告和文档路径                           |

---

## 8. 安装与运行

### 8.1 安装依赖

```bash
pip install -r requirements.txt
```

如果手动安装依赖，至少需要：

```bash
pip install pandas matplotlib openai
```

---

### 8.2 设置 DeepSeek API Key

真实 LLM 模式依赖环境变量：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

注意：PowerShell 中这样设置的环境变量只对当前窗口有效。

如果没有设置 API Key，系统仍然可以运行规则模式、mock LLM 模式和部分 RAG fallback 功能。

---

### 8.3 启动主程序

```bash
python main.py
```

---

## 9. 常用命令示例

### 9.1 文件切换

```text
切换文件 data/channel_data.csv
切换文件 data/channel_data_new.csv
切换文件 data/stock_price.csv
切换文件 data/stock_price_strategy.csv
```

---

### 9.2 规则数据分析

```text
读取这个 CSV 文件
查看统计信息
分析渠道转化率
生成渠道分析报告
分析风险收益
生成金融指标报告
```

---

### 9.3 均线策略任务

```text
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
生成 MA5-MA10 回测图表
扫描均线参数
按收益率生成参数扫描图表
按最大回撤生成参数扫描报告
生成策略研究总结报告
```

---

### 9.4 LLM 与 RAG 模式

```text
开启LLM模式
关闭LLM模式
使用真实LLM
使用模拟LLM
开启RAG模式
关闭RAG模式
检查LLM连接
开启轨迹
关闭轨迹
```

---

### 9.5 RAG 知识问答

```text
MA5-MA10 策略适合震荡行情吗？
最大回撤是什么意思？
如果用户问最大回撤，sort_by 应该是什么？
夏普比率高说明什么？
```

---

## 10. fallback 机制

系统支持多层 fallback：

```text
DeepSeek Tool Selector 失败
→ mock selector
→ 旧规则 router

DeepSeek RAG Answer 失败
→ 本地规则 RAG 回答

LLM 模式关闭
→ 直接使用规则 router
```

这使得项目在没有 API Key、网络不可用、公司 WiFi 限制 API 访问等情况下仍然可以演示核心功能。

---

## 11. LLM 健康检查

可以在主程序中输入：

```text
检查LLM连接
```

系统会检查：

```text
DEEPSEEK_API_KEY 是否存在
DeepSeek API 是否能连接
模型是否能返回合法 JSON
请求耗时
失败阶段和失败原因
```

常见失败示例：

```text
调用 DeepSeek API 失败：Connection error.
```

这通常与网络环境、代理、公司 WiFi、防火墙或 API 域名访问限制有关，不一定是代码问题。

---

## 12. 输出文件

生成结果默认保存在：

```text
data/output/reports/
data/output/charts/
data/logs/
```

其中：

* Markdown 报告保存在 `data/output/reports/`
* PNG 图表保存在 `data/output/charts/`
* 工具调用日志保存在 `data/logs/tool_calls.jsonl`

这些运行时输出通常不建议提交到 GitHub。

---

## 13. 当前版本定位

当前项目适合作为：

```text
AI Pilot 实习项目原型
Agent 工具调用学习项目
LLM Tool Calling 练习项目
RAG 入门项目
数据分析自动化 CLI Demo
```

项目重点不在预测模型准确率，而在展示：

```text
如何把自然语言输入
转换成可控、安全、可追踪的数据分析工作流
```

---

## 14. 下一阶段计划

下一阶段不继续盲目增加新功能，而是进行项目结构收敛：

```text
第 49 课：项目结构盘点，区分核心文件、fallback 文件和 legacy 文件
第 50 课：清理 main.py，拆分命令处理和任务执行逻辑
第 51 课：整理 LLM / RAG / Tool Calling 模块边界
第 52 课：全量回归测试
第 53 课：更新架构文档和使用示例
第 54 课：打 v0.3 tag 并推送 GitHub
第 55 课：再考虑 embedding / 向量检索 / 多文档知识库
```
