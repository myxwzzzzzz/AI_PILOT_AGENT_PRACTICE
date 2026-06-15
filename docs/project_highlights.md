# AI Pilot Agent Practice Project Highlights

本文件用于总结 `AI Pilot Agent Practice` 项目的展示亮点，适合用于 README 补充、面试讲解、实习申请项目介绍或项目复盘。

---

## 1. 项目一句话介绍

`AI Pilot Agent Practice` 是一个面向 **AI Agent Tool Calling、RAG 知识问答、数据分析自动化、金融策略研究自动化** 的 Python 学习项目。

它展示了如何把用户自然语言输入转换成可控、安全、可追踪的数据分析和策略研究工作流。

---

## 2. 项目不是普通聊天机器人

本项目的重点不是让模型自由聊天，而是让 Agent 能够：

```text
理解用户意图
选择合适工具
解析执行参数
检查文件类型
安全调用 Python 工具
生成报告和图表
检索本地知识文档
输出可追踪的 trace
在 LLM 或网络失败时 fallback
```

核心思想是：

```text
LLM 负责理解和决策；
Python 负责校验和执行；
RAG 负责提供本地知识依据；
fallback 负责保证系统稳定；
trace 和 logger 负责可解释和可调试。
```

---

## 3. 当前项目能力总览

### 3.1 数据分析能力

项目可以处理渠道转化数据，例如：

```text
读取 CSV
查看字段
查看缺失值
查看统计信息
分析渠道转化率
判断表现最好的渠道
生成渠道分析报告
```

### 3.2 金融策略研究能力

项目可以处理股票价格数据，例如：

```text
计算收益率
计算年化波动率
计算最大回撤
计算夏普比率
生成金融指标报告
运行 MA 均线策略回测
生成回测报告
生成净值曲线和回撤曲线
扫描 MA 参数组合
生成参数扫描报告和图表
生成策略研究总结报告
```

### 3.3 Tool Calling 能力

项目支持两类工具选择路径：

```text
规则模式：router.py 根据关键词选择工具
LLM 模式：DeepSeek selector 根据用户意图选择工具
```

LLM 不直接执行代码，只返回结构化 tool call，例如：

```json
{
  "intent_type": "tool_call",
  "tool_name": "generate_backtest_report",
  "arguments": {
    "short_window": 5,
    "long_window": 10
  },
  "reason": "用户要求生成 MA5-MA10 回测报告"
}
```

然后由 Python 的安全执行层检查工具名、文件类型和参数，再调用真实工具。

### 3.4 RAG 知识问答能力

项目支持本地知识文档问答，例如：

```text
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
夏普比率高说明什么？
如果用户问最大回撤，sort_by 应该是什么？
```

RAG 目前支持：

```text
keyword retrieval
embedding retrieval
hybrid retrieval
```

默认仍然使用 keyword retrieval，embedding 和 hybrid 作为扩展能力保留。

### 3.5 fallback 能力

项目有多层 fallback：

```text
真实 DeepSeek selector 失败
→ mock selector
→ rule router

DeepSeek RAG answer 失败
→ 本地规则 RAG answer

hybrid retrieval 的 embedding index 缺失
→ fallback 到 keyword retrieval
```

### 3.6 trace 和 logger 能力

项目可以展示：

```text
用户请求走了哪条路径
LLM selector 使用了哪种模式
选择了哪个工具
生成了哪些参数
文件类型检查是否通过
是否发生 fallback
RAG 使用了哪种 retrieval mode
检索到了哪些 chunks
每个 chunk 的 score 和 source
```

这让 Agent 的行为不是黑盒，而是可以调试和解释。

### 3.7 测试体系

项目已经从脚本式测试升级为 pytest 测试体系。

现在可以通过：

```bash
python -m pytest
```

运行完整回归测试。

真实 DeepSeek 集成测试默认跳过，避免误调用真实 API。

---

## 4. 项目架构亮点

### 4.1 Tool Registry

`tool_registry.py` 统一登记工具信息，包括：

```text
工具名
工具描述
关键词
所需文件类型
handler
```

它连接了规则 router、LLM schema 和安全执行层。

### 4.2 安全执行层

`llm_router.py` 不信任 LLM 返回结果，而是执行前检查：

```text
tool_name 是否存在
当前文件类型是否匹配
arguments 是否合法
```

这样可以避免 LLM 绕过 Python 控制直接执行代码。

### 4.3 RAG Retrieval Router

`rag_retrieval_router.py` 是 RAG 检索统一入口。

上层模块只调用统一入口，不直接依赖具体检索器：

```text
上层模块
→ rag_retrieval_router.py
→ keyword / embedding / hybrid retriever
```

这让后续扩展向量数据库、真实 embedding 或 hybrid rerank 更容易。

### 4.4 配置化默认检索模式

默认检索模式集中在 `config.py` 中管理：

```python
DEFAULT_RETRIEVAL_MODE = "keyword"
```

这避免了在多个模块中硬编码 `mode="keyword"`。

### 4.5 pytest 工程化测试

通过 `pytest.ini` 和 `tests/conftest.py`，测试不再需要每个文件重复维护 `sys.path`。

---

## 5. 可以重点展示的 Demo 路线

### Demo 1：规则模式渠道分析

```text
查看当前状态
切换文件 data/channel_data.csv
分析渠道转化率
生成渠道分析报告
```

展示重点：

```text
规则 router
CSV 工具调用
报告生成
```

### Demo 2：金融策略工具调用

```text
切换文件 data/stock_price_strategy.csv
运行 MA5-MA10 回测
生成 MA5-MA10 回测图表
扫描均线参数
生成策略研究总结报告
```

展示重点：

```text
金融工具能力
参数解析
图表生成
报告生成
```

### Demo 3：LLM Tool Calling

```text
开启LLM模式
开启轨迹
生成 MA5-MA10 回测报告
```

展示重点：

```text
DeepSeek selector
tool call JSON
Python 安全执行
trace 展示
fallback 设计
```

### Demo 4：RAG QA

```text
开启LLM模式
开启RAG模式
开启轨迹
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
```

展示重点：

```text
本地知识文档检索
RAG answer
retrieved chunks
RAG trace
```

---

## 6. 当前项目可以如何对外描述

### 简短版本

```text
这是一个 Tool-Calling + RAG 的 AI Agent 学习项目，支持数据分析、金融策略研究、DeepSeek 工具选择、本地知识问答、fallback、trace 和 pytest 回归测试。
```

### 面试版本

```text
我做了一个 AI Pilot Agent 原型项目。它不是普通聊天机器人，而是把自然语言任务转换成可控的 Python 工具调用流程。项目支持规则路由和 DeepSeek Tool Calling，两者都通过 tool registry 和安全执行层调用数据分析、金融指标、均线回测、参数扫描和报告生成工具。同时，我加入了本地 RAG 知识问答，并逐步扩展了 keyword、embedding 和 hybrid retrieval。为了提高工程稳定性，我还实现了 fallback、trace、logger 和 pytest 回归测试。
```

### 技术亮点版本

```text
项目重点展示 Agent 工程能力：
1. LLM 不直接执行代码，只返回结构化 tool call；
2. Python 负责工具注册、文件类型校验、参数校验和安全执行；
3. RAG 使用本地文档提供知识依据；
4. fallback 保证无 API 或网络失败时系统仍可运行；
5. trace 和 logger 提供可解释、可调试的执行路径；
6. pytest 提供稳定回归测试。
```

---

## 7. 当前仍然可以继续升级的方向

后续可以继续做：

```text
Agent Workflow：把多个工具自动串成完整任务流程
Skill Registry：把工具、文档和流程组合成可复用 skill
真实 embedding provider：替换当前 hash-based embedding
Vector DB：引入 Chroma 或 FAISS
MCP：用标准协议连接外部工具和数据源
项目展示文档和演示视频
v0.4 稳定版 tag
```

---

## 8. 项目价值总结

本项目的价值不在于某一个单点功能，而在于完整展示了一个 Agent 原型如何从简单脚本逐步演进为：

```text
有工具
有路由
有 LLM selector
有安全执行
有 RAG
有 fallback
有 trace
有 logger
有测试
有报告输出
可继续扩展 workflow 和 skill
```

它适合作为 AI Agent 工程学习、AI Pilot 实习申请、数据分析自动化 Demo 和金融策略研究自动化 Demo 的项目案例。
