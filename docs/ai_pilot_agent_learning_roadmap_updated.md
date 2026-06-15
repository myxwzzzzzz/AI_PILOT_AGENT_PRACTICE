# AI Pilot Agent Learning Roadmap Updated

本文件记录 `AI Pilot Agent Practice` 项目的学习路线和当前 v0.4 阶段状态。

---

## 1. 项目定位

本项目是一个面向 **AI Pilot / Agent Tool Calling / RAG / 数据分析自动化 / 金融策略研究自动化** 的学习型项目。

它不是普通聊天机器人，而是一个逐步构建的 Agent 工程原型，目标是展示：

```text
如何把用户自然语言输入
转换成可控、安全、可追踪的数据分析和金融策略研究工作流。
```

核心原则：

```text
LLM 不直接执行代码；
LLM 负责理解意图、选择工具、生成参数或基于本地知识回答；
Python 负责文件状态、工具校验、参数校验、工具执行、日志和 trace；
RAG 负责把本地知识文档注入回答和工具选择过程；
fallback 保证 API 不可用时项目仍然可以演示和测试。
```

---

## 2. 阶段总览

| 阶段 | 主题 | 状态 |
|---|---|---|
| v0.1 | 基础 CSV 数据分析助手 | 已完成 |
| v0.2 | Tool Registry + 金融指标 + 策略回测 | 已完成并打 tag |
| v0.3 | LLM Tool Calling + DeepSeek + RAG QA | 已完成并打 tag |
| v0.4 | RAG 升级 + pytest + trace + workflow/docs 规划 | 已完成，准备打 tag |

---

## 3. v0.1：基础 CSV 数据分析助手

完成内容：

```text
创建 Python 项目目录
准备 channel_data.csv
实现 CSV 读取
查看字段
查看缺失值
查看统计信息
分析渠道转化率
判断最佳渠道
生成渠道分析 Markdown 报告
建立早期 CLI 主循环
```

---

## 4. v0.2：Tool Registry + 金融策略分析

完成内容：

```text
Tool Registry
Rule Router
File Inspector
Parameter Parser
Trace Formatter
Logger
股票风险收益指标
MA 均线策略回测
回测报告
回测图表
参数扫描
参数扫描报告
参数扫描图表
策略研究总结报告
requirements.txt
.gitignore
v0.2 tag
```

v0.2 的关键价值是：项目从简单脚本升级为规则型 Agent。

---

## 5. v0.3：LLM Tool Calling + DeepSeek + RAG QA

完成内容：

```text
LLM Tool Schema
LLM Router 安全执行层
Mock LLM Selector
Real LLM Selector 接口
DeepSeek 接入
LLM 模式开关
LLM trace 展示
LLM fallback：real → mock → rule
LLM 健康检查
RAG 文档读取与切块
关键词 RAG Retriever
RAG 检索注入 LLM Selector
知识问题走 RAG QA
DeepSeek RAG 回答
RAG 本地 fallback
v0.3 tag
```

v0.3 的关键价值是：项目具备了真正的 **Tool-Calling + RAG Agent 原型**。

---

## 6. v0.4：结构整理、RAG 升级与可展示化

v0.4 阶段目标不是盲目增加功能，而是让项目更稳定、更清晰、更可解释，并为后续 workflow 和 skill 打基础。

### 第 56 课：提交 RAG retrieval router

完成：

```text
新增 rag_retrieval_router.py
上层模块统一调用 retrieve_chunks()
为 keyword / embedding / hybrid 检索扩展提供统一入口
```

### 第 57 课：整理 pytest 测试运行方式

完成：

```text
新增 pytest.ini
新增 tests/conftest.py
requirements.txt 增加 pytest
脚本式测试改成 pytest 函数式测试
真实 DeepSeek 测试默认跳过
支持 python -m pytest 一键回归测试
```

### 第 58 课：配置默认 RAG retrieval mode

完成：

```text
config.py 新增 DEFAULT_RETRIEVAL_MODE = "keyword"
上层模块不再硬编码 mode="keyword"
为后续切换 embedding / hybrid 做准备
```

### 第 59 课：升级 RAG 知识文档

完成：

```text
扩展 MA 策略说明
新增风险指标说明
补充 sort_by 映射规则
新增 RAG QA 示例
提升 keyword 和 embedding 检索材料质量
```

### 第 60 课：Embedding RAG 方案设计

完成：

```text
新增 docs/rag_embedding_design.md
明确为什么先用本地 JSON index
明确暂不接 Chroma / FAISS
设计 embedding indexer / retriever / fallback / 测试方案
```

### 第 61 课：实现最小 embedding indexer

完成：

```text
新增 rag_embedding_indexer.py
新增 tests/test_rag_embedding_indexer.py
读取 documents/
生成 hash-based embedding
保存 data/rag_index/rag_index.json
.gitignore 忽略运行时索引
```

### 第 62 课：实现 embedding retriever

完成：

```text
新增 rag_embedding_retriever.py
读取 rag_index.json
对 query 生成 hash embedding
计算 cosine similarity
rag_retrieval_router.py 支持 mode="embedding"
新增 embedding retriever 测试
```

### 第 63 课：实现 hybrid RAG

完成：

```text
新增 rag_hybrid_retriever.py
融合 keyword 和 embedding 结果
分数归一化
去重排序
embedding index 缺失时 fallback 到 keyword
rag_retrieval_router.py 支持 mode="hybrid"
```

### 第 64 课：RAG trace 优化

完成：

```text
keyword chunk 增加 retrieval_mode
trace 显示 retrieval mode
trace 显示 chunk score / source
trace 显示 hybrid retrieval_sources
trace 显示 keyword_score / embedding_score / embedding_provider
新增 trace formatter 测试
```

### 第 65 课：Agent Workflow 规划

完成：

```text
新增 docs/agent_workflow_design.md
设计 stock_strategy_research_workflow
规划 workflow_planner.py / workflow_runner.py
规划 workflow trace / fallback / 测试方式
```

### 第 66 课：项目展示文档

完成：

```text
新增 docs/project_highlights.md
新增 docs/demo_script.md
整理项目亮点
整理面试和演示脚本
```

### 第 67 课：v0.4 稳定版收尾

目标：

```text
更新 README
更新架构文档
更新使用示例
更新 roadmap
运行全量测试
提交 v0.4 文档收尾
打 v0.4 tag
push main 和 tag
```

---

## 7. 当前核心能力

当前项目支持：

```text
规则模式
LLM Tool Calling 模式
RAG QA 模式
真实 DeepSeek selector
mock selector fallback
rule router fallback
DeepSeek RAG answer
本地规则 RAG answer fallback
keyword retrieval
embedding retrieval
hybrid retrieval
RAG trace
工具调用日志
pytest 测试体系
报告生成
图表生成
参数扫描
策略研究总结
Agent Workflow 设计文档
项目展示文档
```

---

## 8. 当前项目是否算 AI Agent？

当前项目可以定义为：

```text
一个面向数据分析和金融策略研究的 Tool-Calling + RAG AI Agent 原型。
```

它已经具备 Agent 的关键特征：

```text
自然语言输入
工具选择
参数生成
安全执行
RAG 知识增强
fallback
trace
日志
测试体系
```

但它还不是完整的高级自主 Agent，因为尚未实现：

```text
多步 workflow runner
自动任务拆解与连续执行
skill registry
真实 embedding provider
MCP 接入
长期记忆
```

---

## 9. v0.4 后建议方向

建议后续进入 v0.5 规划：

```text
1. 实现 workflow_planner.py
2. 实现 workflow_runner.py
3. 先支持 stock_strategy_research_workflow
4. 把 workflow trace 接入 trace_formatter.py
5. 抽象 skill_registry.py
6. 接入真实 embedding provider
7. 再考虑 Chroma / FAISS / vector DB
8. 最后考虑 MCP 工具接入
```

推荐顺序：

```text
workflow → skill → real embedding → vector DB → MCP
```

---

## 10. v0.4 总结

v0.4 的核心成果是：

```text
项目从 v0.3 的 Tool-Calling + RAG 原型，
进一步升级为结构更清晰、测试更标准、RAG 更完整、trace 更可解释、文档更适合展示的 AI Agent 学习项目。
```

它现在已经适合作为：

```text
AI Pilot 实习项目展示
Agent Tool Calling 学习项目
RAG 入门与进阶项目
数据分析自动化 Demo
金融策略研究自动化 Demo
```
