# AI Pilot Agent Practice

一个面向 **AI Pilot / Agent Tool Calling / RAG 知识问答 / 数据分析自动化 / 金融策略研究自动化** 的 Python 学习项目。

这个项目不是普通聊天机器人，也不是单一数据分析脚本。它的目标是展示：

```text
如何把用户自然语言输入
转换成可控、安全、可追踪的数据分析和金融策略研究工作流
```

当前项目已经完成从规则型 CSV 助手到 **Tool-Calling + RAG AI Agent 原型** 的演进，并在 v0.4 阶段补齐了测试体系、RAG 检索抽象、embedding / hybrid RAG 原型、trace 可解释性和展示文档。

---

## 1. 当前版本状态

```text
当前稳定里程碑：v0.4
当前主分支：main
当前定位：Tool-Calling + RAG AI Agent 原型
```

v0.4 阶段在 v0.3 的基础上重点完成：

```text
CLI 模块边界整理
pytest 统一测试体系
RAG retrieval router 抽象
默认 retrieval mode 配置化
RAG 知识文档质量升级
embedding RAG 设计文档
本地 hash-based embedding indexer
embedding retriever
hybrid retriever
RAG trace 优化
Agent Workflow 设计文档
项目展示文档
```

---

## 2. 项目核心原则

```text
LLM 不直接执行代码；
LLM 负责理解意图、选择工具、生成参数，或基于本地文档生成回答；
Python 负责状态管理、文件校验、参数校验、工具执行、日志和 trace；
RAG 负责把本地知识文档注入回答和工具选择过程；
fallback 保证没有 API 或网络失败时项目仍然可运行。
```

这意味着：即使 LLM 返回了工具名和参数，系统也必须经过 Python 侧的安全执行层，检查工具是否存在、文件类型是否匹配、参数是否合法，然后才会执行真实工具。

---

## 3. 当前核心能力

### 3.1 规则模式

不使用 LLM，直接通过规则 router 匹配工具。

```text
用户输入
→ main.py
→ router.py
→ tool_registry.py
→ file_inspector.py
→ parameter_parser.py
→ tools.py / finance_tools.py
→ response_formatter.py
→ logger.py
```

适合：

```text
基础演示
无 API Key 环境
稳定回归测试
LLM fallback 最终路径
```

---

### 3.2 LLM Tool Calling 模式

用户输入：

```text
开启LLM模式
```

系统默认使用真实 DeepSeek selector。LLM 只负责选择工具和生成参数，不直接执行工具。

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
→ logger.py
```

如果 DeepSeek 不可用：

```text
real selector 失败
→ mock selector
→ rule router
```

---

### 3.3 RAG QA 模式

用户输入：

```text
开启LLM模式
开启RAG模式
```

知识性问题会走 RAG QA，而不是工具执行。

```text
用户问题
→ llm_agent_runner.py
→ rag_retrieval_router.py
→ keyword / embedding / hybrid retriever
→ rag_qa.py
→ rag_llm_answerer.py
→ DeepSeek 回答或本地 fallback 回答
```

示例问题：

```text
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
如果用户问最大回撤，sort_by 应该是什么？
夏普比率高说明什么？
```

---

## 4. RAG 检索能力

当前 RAG 已支持三种检索模式：

| 模式 | 文件 | 说明 |
|---|---|---|
| keyword | `rag_retriever.py` | 基于关键词打分，稳定、可解释，是当前默认模式 |
| embedding | `rag_embedding_retriever.py` | 基于本地 hash embedding index 的相似度检索 |
| hybrid | `rag_hybrid_retriever.py` | 融合 keyword 和 embedding 结果，去重后重新排序 |

统一入口：

```text
rag_retrieval_router.py
```

默认模式由 `config.py` 控制：

```python
DEFAULT_RETRIEVAL_MODE = "keyword"
```

embedding index 构建器：

```bash
python rag_embedding_indexer.py
```

默认生成运行时索引：

```text
data/rag_index/rag_index.json
```

该索引文件属于运行时产物，不提交 Git。

---

## 5. 支持的数据任务

### 渠道转化分析

适用于字段：

```text
date, channel, visits, signups, payments
```

支持：

```text
读取 CSV
查看字段
查看缺失值
查看统计信息
分析渠道转化率
判断表现最好的渠道
生成渠道分析报告
```

### 金融指标分析

适用于字段：

```text
date, close
```

支持：

```text
总收益率
年化波动率
最大回撤
夏普比率
金融指标报告
```

### 均线策略研究

支持：

```text
MA 策略回测
回测报告
净值曲线图
回撤曲线图
参数扫描
参数扫描报告
参数扫描图表
策略研究总结报告
```

---

## 6. 安装与运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置 DeepSeek API Key

PowerShell 当前窗口：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

没有 API Key 时，仍然可以使用：

```text
规则模式
模拟 LLM 模式
RAG 本地 fallback
```

### 启动主程序

```bash
python main.py
```

---

## 7. 常用命令

### 系统命令

```text
查看当前状态
查看工具
查看日志
开启轨迹
关闭轨迹
退出
```

### 文件切换

```text
切换文件 data/channel_data.csv
切换文件 data/channel_data_new.csv
切换文件 data/stock_price.csv
切换文件 data/stock_price_strategy.csv
```

### LLM / RAG 模式

```text
开启LLM模式
关闭LLM模式
开启模拟LLM模式
使用真实LLM
开启RAG模式
关闭RAG模式
检查LLM连接
```

### 示例任务

```text
分析渠道转化率
生成渠道分析报告
分析风险收益
生成金融指标报告
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
生成 MA5-MA10 回测图表
扫描均线参数
按收益率生成参数扫描图表
按最大回撤生成参数扫描报告
生成策略研究总结报告
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
```

---

## 8. 测试

当前项目使用 pytest 统一运行测试。

完整测试：

```bash
python -m pytest
```

单个测试文件：

```bash
python -m pytest tests/test_rag_retrieval_router.py
```

真实 DeepSeek 集成测试默认跳过，避免误调用 API。需要显式开启：

```powershell
$env:RUN_REAL_LLM_TESTS="1"
$env:DEEPSEEK_API_KEY="你的 key"
python -m pytest tests/test_deepseek_real_selector.py
```

---

## 9. 项目目录概览

```text
ai_pilot_agent/
├─ main.py
├─ cli_state.py
├─ cli_command_handler.py
├─ router.py
├─ tool_registry.py
├─ llm_agent_runner.py
├─ llm_tool_selector.py
├─ llm_router.py
├─ real_llm_tool_selector.py
├─ mock_llm_tool_selector.py
├─ rag_document_loader.py
├─ rag_retriever.py
├─ rag_embedding_indexer.py
├─ rag_embedding_retriever.py
├─ rag_hybrid_retriever.py
├─ rag_retrieval_router.py
├─ rag_qa.py
├─ rag_llm_answerer.py
├─ trace_formatter.py
├─ response_formatter.py
├─ logger.py
├─ tools.py
├─ finance_tools.py
├─ documents/
├─ docs/
├─ data/
└─ tests/
```

---

## 10. 当前项目定位

这是一个 **Tool-Calling + RAG AI Agent 原型**。

它已经具备：

```text
本地工具注册
规则工具路由
LLM 工具选择
Python 安全执行
RAG 知识问答
keyword / embedding / hybrid retrieval
fallback 容错
trace 可解释性
pytest 回归测试
报告和图表生成
```

它还不是完整的高级自主 Agent。后续可以继续升级：

```text
多步 workflow runner
skill registry
真实 embedding provider
向量数据库
MCP 工具接入
更完整的项目展示文档
```
