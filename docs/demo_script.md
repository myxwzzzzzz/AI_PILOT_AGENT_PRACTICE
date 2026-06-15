# AI Pilot Agent Practice Demo Script

本文件用于准备 `AI Pilot Agent Practice` 项目的演示流程。目标是让观看者在较短时间内理解：这个项目不是普通聊天机器人，而是一个可以调用工具、检索知识、生成报告、展示 trace 的 AI Agent 原型。

---

## 1. Demo 前准备

### 1.1 进入项目目录

```powershell
cd D:\Vibecoding\ai_pilot_agent
```

### 1.2 激活 conda 环境

```powershell
conda activate IND5003
```

### 1.3 运行测试

```powershell
python -m pytest
```

预期结果：

```text
大部分测试 passed，真实 DeepSeek 集成测试默认 skipped。
```

### 1.4 启动主程序

```powershell
python main.py
```

---

## 2. Demo 总体讲解开场

可以这样介绍：

```text
这个项目是一个 AI Pilot Agent 原型。它的目标不是让模型自由聊天，而是把用户自然语言任务转换成可控、安全、可追踪的 Python 工具调用流程。项目支持规则路由、DeepSeek Tool Calling、本地 RAG 知识问答、fallback、trace、日志和 pytest 测试。
```

---

## 3. Demo 1：规则模式下的渠道分析

### 3.1 命令

```text
查看当前状态
切换文件 data/channel_data.csv
分析渠道转化率
哪个渠道表现最好
生成渠道分析报告
```

### 3.2 讲解重点

这部分展示项目的基础工具能力：

```text
读取 CSV
识别渠道数据
执行渠道聚合分析
计算注册率和支付率
生成 Markdown 报告
```

可以说明：

```text
即使不开 LLM，项目也可以通过规则 router 稳定运行。这是系统的 fallback 基线。
```

---

## 4. Demo 2：金融策略研究工具

### 4.1 命令

```text
切换文件 data/stock_price_strategy.csv
分析风险收益
运行 MA5-MA10 回测
生成 MA5-MA10 回测图表
扫描均线参数
生成策略研究总结报告
```

### 4.2 讲解重点

这部分展示项目不是简单 CSV 读取，而是具备金融策略研究能力：

```text
收益率分析
最大回撤
夏普比率
均线策略回测
参数扫描
图表生成
策略总结报告
```

可以说明：

```text
项目重点不是预测股票，而是展示如何把金融分析任务封装成可被 Agent 调用的工具。
```

---

## 5. Demo 3：LLM Tool Calling

### 5.1 命令

```text
开启LLM模式
开启轨迹
生成 MA5-MA10 回测报告
```

### 5.2 讲解重点

这部分展示 DeepSeek selector 如何参与工具选择。

可以说明执行路径：

```text
用户输入
→ llm_agent_runner.py
→ llm_tool_selector.py
→ real_llm_tool_selector.py
→ DeepSeek 返回 tool_name 和 arguments
→ llm_router.py 做安全检查
→ Python 工具执行
→ trace 展示过程
```

重点强调：

```text
LLM 不直接执行代码。
LLM 只负责理解意图和生成结构化 tool call。
真正执行前仍然由 Python 检查工具、文件类型和参数。
```

---

## 6. Demo 4：模拟 LLM fallback

### 6.1 命令

```text
开启模拟LLM模式
生成 MA5-MA10 回测报告
```

### 6.2 讲解重点

这部分展示 fallback 设计。

可以说明：

```text
如果真实 DeepSeek 不可用，项目仍然可以通过 mock selector 演示 LLM Tool Calling 链路。
mock selector 也适合本地测试和离线演示。
```

---

## 7. Demo 5：RAG QA 知识问答

### 7.1 命令

```text
使用真实LLM
开启RAG模式
开启轨迹
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
如果用户问最大回撤，sort_by 应该是什么？
```

### 7.2 讲解重点

这部分展示 RAG 能力。

可以说明：

```text
知识性问题不会走数据分析工具，而是走 RAG QA。
系统会从 documents/ 本地知识文档中检索相关片段，再生成回答。
```

重点展示 trace 中的信息：

```text
retrieval_mode
retrieved_chunks
source
score
answer_source
fallback 信息
```

---

## 8. Demo 6：RAG retrieval mode 扩展能力

当前默认 retrieval mode 是：

```text
keyword
```

但项目已经支持：

```text
embedding
hybrid
```

可以这样讲：

```text
keyword retrieval 适合明确关键词，比如 sort_by、最大回撤；
embedding retrieval 是为了后续语义检索做准备；
hybrid retrieval 会合并 keyword 和 embedding 的结果。
当前默认仍然保持 keyword，是为了主路径稳定。
```

如果要演示 embedding index，可以在主程序外运行：

```powershell
python rag_embedding_indexer.py
```

它会生成：

```text
data/rag_index/rag_index.json
```

该文件是运行时产物，不提交 Git。

---

## 9. Demo 讲解收尾

可以这样总结：

```text
这个项目已经实现了一个 Tool-Calling + RAG 的 AI Agent 原型。它具备工具注册、LLM 工具选择、安全执行、本地知识检索、fallback、trace、logger 和 pytest 回归测试。后续可以继续升级为多步 Agent Workflow，让系统自动把复杂分析任务拆成多个工具步骤执行。
```

---

## 10. 面试问答准备

### Q1：这个项目为什么算 Agent？

可以回答：

```text
因为它不是单纯聊天，而是可以根据用户自然语言选择工具、生成参数、执行任务、检索知识、展示 trace，并在 LLM 失败时 fallback。它具备 Tool Calling、RAG 和安全执行这些 Agent 原型的核心能力。
```

### Q2：为什么不让 LLM 直接执行代码？

可以回答：

```text
为了安全和可控。LLM 只返回 tool_name 和 arguments，真正执行前由 Python 检查工具是否存在、文件类型是否匹配、参数是否合法。这样可以避免 LLM 产生不可控执行。
```

### Q3：为什么保留规则 router？

可以回答：

```text
规则 router 是 LLM 关闭时的主路径，也是 LLM 失败后的最终 fallback。它保证项目在没有 API Key 或网络失败时仍然可以演示和测试。
```

### Q4：为什么当前默认还是 keyword retrieval？

可以回答：

```text
因为 keyword retrieval 当前最稳定、最可解释。embedding 和 hybrid 已经实现，但当前 hash-based embedding 主要用于搭建工程结构。未来接入真实 embedding 后，可以再评估是否切换默认模式。
```

### Q5：下一步准备做什么？

可以回答：

```text
下一步是把多个单步工具串成 Agent Workflow，比如让用户一句话触发完整股票策略研究流程，包括风险收益分析、参数扫描、图表生成和总结报告。
```
