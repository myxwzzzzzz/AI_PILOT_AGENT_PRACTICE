# AI Pilot Agent Learning Roadmap

本 Roadmap 记录 AI Pilot Agent Practice 项目的学习和开发路径。

项目目标是从一个最小可用的 CSV 数据分析脚本，逐步演进为支持 Tool Calling、LLM Agent、RAG QA、fallback、trace 和报告生成的 AI Pilot Agent 原型。

---

## 1. 总体学习目标

通过本项目，逐步掌握：

```text
Python 数据分析
CSV 文件处理
规则路由
工具注册表
文件类型识别
参数解析
金融指标计算
策略回测
图表生成
Markdown 报告
LLM Tool Calling
大模型 API 接入
RAG 文档检索
RAG 知识问答
Agent fallback
Agent trace
项目结构整理
```

最终目标是形成一个可以用于展示的 AI Pilot / Agent 工具调用项目。

---

## 2. 当前版本总览

当前版本：**v0.3**

当前状态：

```text
Rule-based Agent
→ Tool Registry Agent
→ Finance Analysis Agent
→ LLM Tool Calling Agent
→ DeepSeek Agent
→ RAG QA Agent
```

当前系统已经支持三种主要路径：

```text
规则模式：
用户输入 → router.py → 工具执行

LLM Tool Calling 模式：
用户输入 → DeepSeek / mock selector → llm_router.py → 工具执行

RAG QA 模式：
知识性问题 → RAG 检索 → DeepSeek 生成回答 → 本地知识片段溯源
```

---

## 3. v0.1 阶段：基础 CSV 数据分析助手

### 阶段目标

构建最小可用的数据分析助手。

用户可以通过命令行输入自然语言，系统读取 CSV 并执行基础数据分析任务。

### 已完成内容

| 课程 / 阶段 | 内容                     | 状态  |
| ------- | ---------------------- | --- |
| 基础环境搭建  | 创建 Python 项目、虚拟环境和基础目录 | 已完成 |
| CSV 读取  | 支持读取渠道转化 CSV 文件        | 已完成 |
| 数据概览    | 支持字段查看、缺失值检查和统计信息      | 已完成 |
| 渠道转化分析  | 计算访问、注册、支付和转化率         | 已完成 |
| 渠道报告    | 生成渠道分析 Markdown 报告     | 已完成 |
| CLI 交互  | 支持循环输入用户问题             | 已完成 |

### 阶段成果

系统可以处理如下任务：

```text
读取这个 CSV 文件
查看统计信息
分析渠道转化率
生成渠道分析报告
```

---

## 4. v0.2 阶段：工具注册表 + 金融策略分析

### 阶段目标

从简单数据分析助手升级为支持 Tool Registry、文件类型识别、金融指标分析和策略回测的 Rule-based Agent。

### 已完成内容

| 课程 / 阶段          | 内容                          | 状态  |
| ---------------- | --------------------------- | --- |
| Tool Registry    | 建立统一工具注册表                   | 已完成 |
| File Inspector   | 根据 CSV 字段识别文件类型             | 已完成 |
| Router Guardrail | 加入文件类型校验                    | 已完成 |
| Trace            | 展示工具调用轨迹                    | 已完成 |
| Logger           | 记录工具调用日志                    | 已完成 |
| 股票指标分析           | 计算收益率、波动率、最大回撤、夏普比率         | 已完成 |
| 均线策略回测           | 支持 MA 短长均线策略                | 已完成 |
| MA 参数解析          | 支持从自然语言解析 MA5-MA10 等参数      | 已完成 |
| 回测报告             | 生成均线策略回测 Markdown 报告        | 已完成 |
| 参数扫描             | 扫描多组 MA 参数组合                | 已完成 |
| 参数扫描报告           | 生成参数扫描 Markdown 报告          | 已完成 |
| 图表生成             | 生成净值曲线、回撤曲线和参数扫描图表          | 已完成 |
| 策略研究总结           | 生成综合策略研究总结报告                | 已完成 |
| 输出目录规范           | 统一 reports、charts、logs 输出目录 | 已完成 |
| requirements     | 整理依赖文件                      | 已完成 |
| .gitignore       | 忽略缓存、日志和运行时输出               | 已完成 |
| 测试文件             | 增加多个功能测试脚本                  | 已完成 |

### 阶段成果

系统可以处理如下任务：

```text
分析风险收益
生成金融指标报告
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
生成 MA5-MA10 回测图表
扫描均线参数
按收益率生成参数扫描图表
生成策略研究总结报告
```

### v0.2 核心设计

```text
用户输入
→ router.py
→ tool_registry.py
→ file_inspector.py
→ parameter_parser.py
→ 工具执行
→ response_formatter.py
→ trace_formatter.py
→ logger.py
```

---

## 5. v0.3 阶段：LLM Tool Calling + RAG QA

更新时间：2026-06-10

当前项目已经完成从 Rule-based Agent 到 LLM Agent 原型的升级。

### 已完成能力

| 课程     | 内容                                         | 状态  |
| ------ | ------------------------------------------ | --- |
| 第 34 课 | 将 Tool Registry 转换为 LLM 可读 Tool Schema     | 已完成 |
| 第 35 课 | 新增 `llm_router.py`，支持模拟 LLM Tool Call 安全执行 | 已完成 |
| 第 36 课 | 新增 mock LLM Tool Selector                  | 已完成 |
| 第 37 课 | 主助手支持 LLM 模式开关                             | 已完成 |
| 第 38 课 | 建立真实 LLM Selector 接口骨架                     | 已完成 |
| 第 39 课 | 统一 mock / real LLM Selector 调用入口           | 已完成 |
| 第 40 课 | 接入 DeepSeek `deepseek-v4-pro` 真实 LLM       | 已完成 |
| 第 41 课 | 优化 LLM Tool Calling trace 展示               | 已完成 |
| 第 42 课 | 增加 LLM 失败 fallback 机制                      | 已完成 |
| 第 43 课 | 增加 DeepSeek API 健康检查工具                     | 已完成 |
| 第 44 课 | 建立 RAG 文档读取与切块层                            | 已完成 |
| 第 45 课 | 实现关键词检索版 RAG Retriever                     | 已完成 |
| 第 46 课 | 将 RAG 检索结果注入 LLM Selector                  | 已完成 |
| 第 47 课 | 支持知识性问题走 RAG QA，执行性问题走 Tool Calling        | 已完成 |
| 第 48 课 | 使用 DeepSeek 基于 RAG 文档片段生成自然语言回答            | 已完成 |

---

## 6. v0.3 新增核心模块

| 文件                          | 作用                                               |
| --------------------------- | ------------------------------------------------ |
| `llm_tool_schema.py`        | 将工具注册表转换成 LLM 可读 Tool Schema                     |
| `llm_router.py`             | LLM Tool Call 安全执行层                              |
| `mock_llm_tool_selector.py` | 本地规则版 LLM selector，用于 fallback                   |
| `real_llm_tool_selector.py` | DeepSeek 真实 LLM selector                         |
| `llm_tool_selector.py`      | mock / real selector 统一入口                        |
| `llm_agent_runner.py`       | LLM Agent 总调度器，负责 Tool Calling、RAG QA 和 fallback |
| `llm_health_check.py`       | DeepSeek API 健康检查                                |
| `rag_document_loader.py`    | 本地文档读取与切块                                        |
| `rag_retriever.py`          | 关键词检索版 RAG Retriever                             |
| `rag_qa.py`                 | RAG QA 入口                                        |
| `rag_llm_answerer.py`       | DeepSeek RAG 回答生成器                               |
| `documents/`                | 本地知识文档目录                                         |

---

## 7. v0.3 当前系统能力边界

当前 Agent 可以处理三类任务。

### 7.1 规则工具任务

在不开启 LLM 模式时，系统仍可使用旧 `router.py` 基于关键词匹配执行数据分析、回测、报告和图表任务。

示例：

```text
读取这个 CSV 文件
查看统计信息
分析渠道转化率
生成金融指标报告
生成 MA5-MA10 回测报告
```

---

### 7.2 LLM Tool Calling 任务

开启 LLM 模式后，系统可以使用 DeepSeek 根据用户自然语言选择工具，并由 Python 安全执行层完成文件校验、参数校验和工具调用。

示例：

```text
开启LLM模式
使用真实LLM
生成 MA5-MA10 回测报告
按收益率生成参数扫描图表
```

LLM 负责：

```text
理解用户意图
选择工具
生成参数
```

Python 负责：

```text
检查工具是否存在
检查文件类型是否匹配
检查参数是否合法
执行真实工具
记录 trace 和日志
```

---

### 7.3 RAG 知识问答任务

开启 RAG 模式后，系统可以检索 `documents/` 下的本地知识文档，并使用 DeepSeek 基于检索片段生成回答。

示例：

```text
开启RAG模式
MA5-MA10 策略适合震荡行情吗？
最大回撤是什么意思？
如果用户问最大回撤，sort_by 应该是什么？
```

RAG QA 流程：

```text
用户问题
→ 本地知识问答 intent guard
→ rag_retriever.py 检索相关文档片段
→ rag_llm_answerer.py 调用 DeepSeek 生成回答
→ 如果 DeepSeek 失败，fallback 到本地规则回答
→ response_formatter.py 输出答案和参考片段
```

---

## 8. fallback 机制

当前系统已经支持多层 fallback。

### 8.1 Tool Calling fallback

```text
DeepSeek real selector 失败
→ mock selector
→ 旧规则 router
```

### 8.2 RAG QA fallback

```text
DeepSeek RAG 回答失败
→ 本地规则回答
```

### 8.3 网络异常处理

如果出现：

```text
Connection error
```

系统不会崩溃，而是保留本地可运行能力。

这对于以下环境很重要：

```text
公司 WiFi
代理不稳定
API 域名不可达
API Key 未设置
DeepSeek 服务暂时不可用
```

---

## 9. 当前关键命令

### 9.1 模式切换

```text
开启LLM模式
关闭LLM模式
使用真实LLM
使用模拟LLM
开启RAG模式
关闭RAG模式
开启轨迹
关闭轨迹
检查LLM连接
```

### 9.2 数据分析任务

```text
读取这个 CSV 文件
查看统计信息
分析渠道转化率
生成渠道分析报告
分析风险收益
生成金融指标报告
```

### 9.3 策略任务

```text
运行 MA5-MA10 回测
生成 MA5-MA10 回测报告
生成 MA5-MA10 回测图表
扫描均线参数
按收益率生成参数扫描图表
按最大回撤生成参数扫描报告
生成策略研究总结报告
```

### 9.4 RAG QA 任务

```text
MA5-MA10 策略适合震荡行情吗？
最大回撤是什么意思？
如果用户问最大回撤，sort_by 应该是什么？
夏普比率高说明什么？
```

---

## 10. 当前项目风险和技术债

当前 v0.3 功能已经较多，下一阶段需要做结构收敛。

主要技术债包括：

```text
main.py 中命令处理逻辑逐渐变长
router.py 和 llm_agent_runner.py 同时存在，需要明确边界
mock selector、real selector、rule router 的 fallback 关系需要文档化
tests/ 文件数量增多，需要分组整理
部分文档和旧说明需要更新
RAG 目前仍是关键词检索，尚未接入 embedding 或向量数据库
```

---

## 11. 后续阶段计划

下一阶段不继续横向扩展新功能，而是先进行项目结构收敛。

| 后续课程   | 内容                                           | 目的         |
| ------ | -------------------------------------------- | ---------- |
| 第 49 课 | 项目结构盘点，区分核心文件、fallback 文件和 legacy 文件         | 降低项目复杂度    |
| 第 50 课 | 清理 `main.py`，拆分命令处理和任务执行逻辑                   | 提升可维护性     |
| 第 51 课 | 整理 LLM / RAG / Tool Calling 模块边界             | 形成清晰架构     |
| 第 52 课 | 全量回归测试：规则模式、真实 LLM、RAG QA、fallback           | 保证稳定性      |
| 第 53 课 | 更新 README、architecture.md 和 usage_example.md | 准备 v0.3 文档 |
| 第 54 课 | 打 v0.3 tag 并推送 GitHub                        | 固化阶段成果     |
| 第 55 课 | 再考虑 embedding / 向量检索 / 多文档知识库                | 进入更高级 RAG  |

---

## 12. v0.3 阶段总结

v0.3 的核心成果是：

```text
项目已经不再只是一个规则数据分析脚本，
而是一个具备 LLM Tool Calling、RAG QA、fallback、trace 和本地工具执行能力的 AI Pilot Agent 原型。
```

当前最重要的架构原则是：

```text
LLM 不直接执行任务；
LLM 只负责意图理解、工具选择、参数生成或基于文档回答；
Python 负责安全校验、工具执行、状态管理和结果输出；
RAG 为知识问答和工具选择提供本地上下文。
```

这为后续进入更高级的 Agent Workflow、RAG 向量检索和多工具规划打下了基础。
