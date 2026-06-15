# 使用示例

本文档给出 v0.4 阶段的常用演示流程。

---

## 1. 启动项目

```bash
python main.py
```

启动后可以先查看状态：

```text
查看当前状态
查看工具
```

---

## 2. 规则模式演示

规则模式默认开启，不需要 API Key。

```text
切换文件 data/channel_data.csv
读取这个 CSV 文件
查看统计信息
分析渠道转化率
哪个渠道表现最好
生成渠道分析报告
```

演示重点：

```text
系统可以根据自然语言选择本地工具；
不依赖 LLM；
适合展示基础工具能力和 fallback 能力。
```

---

## 3. 金融指标分析演示

```text
切换文件 data/stock_price.csv
分析风险收益
生成金融指标报告
```

系统会基于 `date, close` 字段识别股票价格数据，并计算：

```text
总收益率
年化波动率
最大回撤
夏普比率
```

---

## 4. 均线策略回测演示

```text
切换文件 data/stock_price_strategy.csv
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
生成 MA5-MA10 回测图表
```

演示重点：

```text
自然语言参数解析：MA5-MA10 → short_window=5, long_window=10
文件类型校验：必须是股票价格数据
报告和图表输出：Markdown + PNG
```

---

## 5. 参数扫描演示

```text
扫描均线参数
按收益率生成参数扫描图表
按最大回撤生成参数扫描报告
按夏普生成参数扫描图表
生成策略研究总结报告
```

常见 sort_by 映射：

```text
收益率 → strategy_total_return
最大回撤 → max_drawdown
夏普 → sharpe_ratio
```

---

## 6. Trace 演示

开启轨迹：

```text
开启轨迹
```

然后执行：

```text
运行 MA5-MA10 回测
```

可以观察：

```text
匹配到哪个工具
解析出哪些参数
当前文件类型是否匹配
工具执行是否成功
```

---

## 7. LLM Tool Calling 演示

先设置 DeepSeek API Key：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

启动后输入：

```text
开启LLM模式
开启轨迹
切换文件 data/stock_price_strategy.csv
生成 MA5-MA10 回测报告
```

演示重点：

```text
DeepSeek 负责理解意图和选择工具；
Python 负责检查和执行；
LLM 不直接执行代码。
```

如果没有 API Key，可以演示模拟 LLM：

```text
开启模拟LLM模式
生成 MA5-MA10 回测报告
```

---

## 8. RAG QA 演示

开启：

```text
开启LLM模式
开启RAG模式
开启轨迹
```

然后提问：

```text
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
如果用户问最大回撤，sort_by 应该是什么？
夏普比率高说明什么？
```

演示重点：

```text
知识性问题不会走数据分析工具；
系统会先检索 documents/ 下的本地文档；
回答会附带参考片段；
trace 会显示 retrieval mode、chunk score 和 source。
```

---

## 9. Embedding Index 构建演示

构建本地 RAG embedding index：

```bash
python rag_embedding_indexer.py
```

生成：

```text
data/rag_index/rag_index.json
```

该文件是运行时产物，不提交 Git。

---

## 10. Retrieval Router 开发者演示

可以通过测试验证三种 retrieval mode：

```bash
python -m pytest tests/test_rag_retrieval_router.py
python -m pytest tests/test_rag_embedding_retriever.py
python -m pytest tests/test_rag_hybrid_retriever.py
```

当前默认模式仍然是：

```python
DEFAULT_RETRIEVAL_MODE = "keyword"
```

原因：keyword 最稳定，embedding / hybrid 作为扩展能力保留。

---

## 11. 全量测试

```bash
python -m pytest
```

真实 DeepSeek 集成测试默认跳过。如果需要运行：

```powershell
$env:RUN_REAL_LLM_TESTS="1"
$env:DEEPSEEK_API_KEY="你的 key"
python -m pytest tests/test_deepseek_real_selector.py
```

---

## 12. 面试演示推荐顺序

```text
1. 说明项目目标：自然语言 → 安全工具调用 → 数据分析 / 策略研究
2. 展示规则模式：无 API Key 也能跑
3. 展示金融工具：指标、回测、报告、图表
4. 展示 LLM Tool Calling：LLM 只选工具，Python 执行
5. 展示 RAG QA：基于本地知识回答
6. 展示 trace：解释 Agent 为什么这么做
7. 展示 pytest：说明项目有回归测试体系
8. 说明后续规划：workflow、skill、真实 embedding、MCP
```
