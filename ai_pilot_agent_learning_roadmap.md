# AI Pilot / Agent 工具调用与流程自动化学习路线

> 这个文件用于在新的 ChatGPT 对话窗口中恢复上下文。  
> 如果上下文窗口耗尽，把这个 Markdown 文件发给新的对话，并说明：  
> **“请根据这个学习路线，继续带我一步一步完成 AI Pilot / Agent 工具调用与流程自动化项目。”**

---

## 1. 学习背景与目标岗位

### 目标岗位

岗位方向：**AI Pilot 实习生 / AI 应用实习生 / Agent 流程自动化实习生**

典型 JD 内容包括：

1. 协助推进大模型、智能 Agent 等 AI 技术在证券公司各场景落地；
2. 基于大模型、OpenClaw 等前沿技术，协助开展自营策略研发、落地实施、优化和迭代；
3. 依托 AI 技术开展数据智能处理、流程自动化优化工作；
4. 输出可行的优化方案，完成迭代升级；
5. 要求掌握 AI 基础理论，熟悉主流大语言模型和智能体应用原理；
6. 有 Qoder、Claude Code 等 AI Coding 工具使用经验者优先；
7. 有大模型、Agent 框架、业务流程优化、量化策略研究、数据处理、风险管理经验者优先。

### 岗位真实画像

这个岗位不是纯算法岗，也不是传统数据分析岗，而是：

**AI 应用落地 + Agent 工具调用 + 业务流程自动化 + 金融数据处理 + 量化策略辅助**

核心能力不是“训练大模型”，而是：

- 能把业务流程拆成可执行步骤；
- 能把步骤封装为 Python 工具；
- 能让大模型/Agent 调用这些工具；
- 能处理数据、文档、指标和报告；
- 能把结果落到证券/投研/策略/风控等业务场景里。

---

## 2. 我的学习目标

最终目标是完成一个可以写进简历、可以面试讲、可以演示的项目：

## 项目名称

**基于大模型 Agent 的证券投研与数据分析流程自动化系统**

### 项目目标

输入一个业务任务，例如：

- “帮我分析这个渠道数据里哪个渠道转化率最高”
- “帮我读取某份研报并提取风险点”
- “帮我分析某只股票的历史收益、波动率和最大回撤”
- “帮我生成一份策略分析报告”

系统能够自动：

1. 判断任务类型；
2. 选择合适工具；
3. 调用 Python 工具执行；
4. 得到结构化结果；
5. 生成 Markdown 报告；
6. 输出工具调用记录和分析结论。

---

## 3. 总体学习路线

学习路线分为 6 个阶段：

| 阶段 | 学习内容 | 目标产出 |
|---|---|---|
| 第 1 阶段 | Tool Calling 基础 | 会写可被 Agent 调用的 Python 工具 |
| 第 2 阶段 | 数据处理工具 | 会读取 CSV / Excel 并做业务分析 |
| 第 3 阶段 | 金融指标工具 | 会计算收益率、波动率、最大回撤、夏普比率 |
| 第 4 阶段 | RAG 文档工具 | 会读取研报/公告/PDF 并做问答或摘要 |
| 第 5 阶段 | Workflow 编排 | 会把多个工具串成稳定、可控的流程 |
| 第 6 阶段 | Agent 自动选择工具 | 做出证券投研自动化 Agent Demo |

---

## 4. 目前已经完成的内容

### 已完成：第 1 阶段基础工具函数

已经创建项目目录：

```text
ai_pilot_agent/
├── main.py
├── tools.py
└── data/
```

其中：

- `tools.py`：存放工具函数；
- `main.py`：测试工具函数；
- `data/`：存放 CSV、Excel、PDF、Markdown 报告等文件。

### 已完成的 3 个基础工具

#### 1. `read_csv_file(file_path: str)`

用途：

- 读取 CSV 文件；
- 返回行数、列名、前 5 行预览；
- 用于让 Agent 初步了解数据结构。

返回示例：

```python
{
    "success": True,
    "rows": 9,
    "columns": ["date", "channel", "visits", "signups", "payments"],
    "preview": [...]
}
```

#### 2. `summarize_csv(file_path: str)`

用途：

- 读取 CSV；
- 返回数据行列数；
- 返回缺失值统计；
- 返回数值字段的描述性统计。

返回示例：

```python
{
    "success": True,
    "shape": (9, 5),
    "columns": ["date", "channel", "visits", "signups", "payments"],
    "missing_values": {...},
    "numeric_summary": {...}
}
```

#### 3. `save_markdown_report(content: str, output_path: str)`

用途：

- 把字符串内容保存为 Markdown 报告；
- 后续用于保存 Agent 自动生成的分析报告。

返回示例：

```python
{
    "success": True,
    "message": "报告已保存到：data/report.md"
}
```

---

## 5. 已经准备的数据文件

在 `data/` 文件夹中创建了测试文件：

```text
data/channel_data.csv
```

内容如下：

```csv
date,channel,visits,signups,payments
2026-05-01,抖音,1200,180,45
2026-05-01,小红书,900,150,38
2026-05-01,百度,700,80,20
2026-05-02,抖音,1300,200,50
2026-05-02,小红书,1000,170,42
2026-05-02,百度,750,85,22
2026-05-03,抖音,1250,190,48
2026-05-03,小红书,1100,210,60
2026-05-03,百度,720,82,18
```

这个数据模拟用户增长 / 渠道分析场景。

字段含义：

| 字段 | 含义 |
|---|---|
| `date` | 日期 |
| `channel` | 渠道 |
| `visits` | 访问量 |
| `signups` | 注册数 |
| `payments` | 付费数 |

---

## 6. 已经验证通过的运行结果

运行命令：

```bash
python main.py
```

结果说明：

1. CSV 成功读取；
2. 成功识别 9 行、5 列；
3. 成功输出字段：`date`、`channel`、`visits`、`signups`、`payments`；
4. 缺失值统计全部为 0；
5. 数值字段成功生成描述性统计；
6. Markdown 报告 `data/report.md` 成功保存。

这说明：

- 项目结构正常；
- pandas 能正确读取数据；
- 中文字段和中文数据没有编码问题；
- 基础工具函数已经可以稳定工作。

---

## 7. 当前正在进入的下一步

下一步是第 2 课：

## 写第一个有业务价值的数据分析工具

工具名称：

```python
analyze_channel_conversion(file_path: str)
```

### 目标

自动分析：

1. 哪个渠道注册转化率最高；
2. 哪个渠道付费转化率最高；
3. 哪个渠道注册到付费转化率最高；
4. 哪个渠道整体表现最好。

### 需要计算的指标

| 指标 | 公式 | 含义 |
|---|---|---|
| 注册转化率 | `signups / visits` | 访问用户中有多少完成注册 |
| 付费转化率 | `payments / visits` | 访问用户中有多少完成付费 |
| 注册到付费转化率 | `payments / signups` | 注册用户中有多少最终付费 |

### 这个工具的业务意义

它把一个业务问题：

> 哪个渠道转化效果最好？

转换成了一个可执行的 Python 工具：

```python
analyze_channel_conversion("data/channel_data.csv")
```

这就是 Agent 工具调用的核心思维：

**业务动作 → Python 工具 → 结构化输出 → 大模型解释 → 报告生成**

---

## 8. 第 2 课要新增的代码

在 `tools.py` 末尾新增：

```python
def analyze_channel_conversion(file_path: str) -> dict:
    """
    分析各渠道的注册转化率、付费转化率和注册到付费转化率。
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        df = pd.read_csv(file_path)

        required_columns = ["channel", "visits", "signups", "payments"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                "success": False,
                "error": f"缺少必要字段：{missing_columns}"
            }

        channel_df = (
            df.groupby("channel", as_index=False)
            .agg({
                "visits": "sum",
                "signups": "sum",
                "payments": "sum"
            })
        )

        channel_df["signup_rate"] = channel_df.apply(
            lambda row: row["signups"] / row["visits"] if row["visits"] != 0 else 0,
            axis=1
        )

        channel_df["payment_rate"] = channel_df.apply(
            lambda row: row["payments"] / row["visits"] if row["visits"] != 0 else 0,
            axis=1
        )

        channel_df["signup_to_payment_rate"] = channel_df.apply(
            lambda row: row["payments"] / row["signups"] if row["signups"] != 0 else 0,
            axis=1
        )

        best_signup_channel = channel_df.sort_values(
            by="signup_rate", ascending=False
        ).iloc[0]

        best_payment_channel = channel_df.sort_values(
            by="payment_rate", ascending=False
        ).iloc[0]

        best_signup_to_payment_channel = channel_df.sort_values(
            by="signup_to_payment_rate", ascending=False
        ).iloc[0]

        channel_metrics = channel_df.to_dict(orient="records")

        return {
            "success": True,
            "channel_metrics": channel_metrics,
            "best_signup_channel": {
                "channel": best_signup_channel["channel"],
                "signup_rate": round(best_signup_channel["signup_rate"], 4)
            },
            "best_payment_channel": {
                "channel": best_payment_channel["channel"],
                "payment_rate": round(best_payment_channel["payment_rate"], 4)
            },
            "best_signup_to_payment_channel": {
                "channel": best_signup_to_payment_channel["channel"],
                "signup_to_payment_rate": round(
                    best_signup_to_payment_channel["signup_to_payment_rate"], 4
                )
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

`main.py` 中需要导入这个新函数：

```python
from tools import (
    read_csv_file,
    summarize_csv,
    save_markdown_report,
    analyze_channel_conversion
)
```

然后调用：

```python
conversion_result = analyze_channel_conversion(file_path)
print("\n渠道转化率分析结果：")
print(conversion_result)
```

---

## 9. 预期运行结果

理论上，基于当前测试数据：

| 指标 | 最优渠道 |
|---|---|
| 注册转化率最高 | 小红书 |
| 付费转化率最高 | 小红书 |
| 注册到付费转化率最高 | 小红书 |

因此程序应该输出：

```python
{
    "success": True,
    "channel_metrics": [...],
    "best_signup_channel": {
        "channel": "小红书",
        "signup_rate": ...
    },
    "best_payment_channel": {
        "channel": "小红书",
        "payment_rate": ...
    },
    "best_signup_to_payment_channel": {
        "channel": "小红书",
        "signup_to_payment_rate": ...
    }
}
```

---

## 10. 后续还需要继续学习的内容

### 第 2 阶段：数据处理工具

要继续补：

1. 渠道转化率分析；
2. 自动生成 Markdown 分析报告；
3. 缺失值和异常值分析；
4. 按日期维度分析趋势；
5. 让工具返回更适合大模型解释的结构化结果。

目标产出：

```text
data/channel_analysis_report.md
```

---

### 第 3 阶段：金融指标工具

要学习：

1. 股票收益率计算；
2. 累计收益率；
3. 波动率；
4. 最大回撤；
5. 夏普比率；
6. 均线策略；
7. 简单回测。

可能新增工具：

```python
calculate_return()
calculate_volatility()
calculate_max_drawdown()
calculate_sharpe_ratio()
calculate_moving_average()
run_simple_backtest()
```

目标产出：

```text
data/strategy_report.md
```

---

### 第 4 阶段：RAG 文档工具

要学习：

1. PDF / TXT / Markdown 文档读取；
2. 文本切分；
3. Embedding；
4. 向量数据库 FAISS / Chroma；
5. 检索 Top-K 片段；
6. 把片段放入 Prompt；
7. 返回带来源的回答；
8. 减少幻觉。

可能新增工具：

```python
read_pdf_text()
split_text_into_chunks()
build_vector_store()
retrieve_relevant_chunks()
answer_question_with_context()
```

目标产出：

```text
金融研报 / 公告 / 财报知识库问答 Demo
```

---

### 第 5 阶段：Workflow 编排

要学习：

1. Workflow 和 Agent 的区别；
2. 顺序流程；
3. 条件分支；
4. 失败重试；
5. 人工确认；
6. 工具调用日志；
7. LangGraph 基础。

示例流程：

```text
用户输入任务
→ 判断任务类型
→ 如果是数据分析：调用 CSV / Excel 工具
→ 如果是文档分析：调用 RAG 工具
→ 如果是策略分析：调用金融指标工具
→ 生成报告
→ 保存结果
```

目标产出：

```python
workflow.py
```

---

### 第 6 阶段：Agent 自动选择工具

要学习：

1. Agent 的基本结构；
2. ReAct 思路；
3. Tool Selection；
4. 工具描述优化；
5. 状态管理；
6. 错误恢复；
7. Human-in-the-loop；
8. MCP 基础概念；
9. AI Coding 工具辅助开发。

目标产出：

```python
agent.py
```

最终效果：

用户输入自然语言任务，例如：

```text
帮我分析这个渠道数据，找出表现最好的渠道，并生成一份报告。
```

Agent 自动：

1. 判断任务是数据分析；
2. 调用 `read_csv_file()`；
3. 调用 `analyze_channel_conversion()`；
4. 调用 `save_markdown_report()`；
5. 输出最终结论和报告路径。

---

## 11. 项目总体架构设想

### 初版架构

```text
用户输入
  ↓
任务解析
  ↓
工具选择
  ↓
Python 工具执行
  ↓
结构化结果
  ↓
大模型生成解释
  ↓
Markdown 报告输出
```

### 中期架构

```text
用户输入
  ↓
Router / 任务分类
  ├── 数据分析任务 → CSV / Excel 工具
  ├── 文档分析任务 → RAG 工具
  ├── 金融策略任务 → 金融指标 / 回测工具
  └── 报告生成任务 → Markdown 工具
  ↓
Workflow 编排
  ↓
工具调用日志
  ↓
人工确认，高风险动作
  ↓
最终报告
```

### 最终项目架构

```text
ai_pilot_agent/
├── main.py
├── agent.py
├── workflow.py
├── tools.py
├── data_tools.py
├── finance_tools.py
├── rag_tools.py
├── report_tools.py
├── prompts/
│   ├── system_prompt.md
│   ├── report_prompt.md
│   └── analysis_prompt.md
├── data/
│   ├── channel_data.csv
│   ├── stock_price.csv
│   ├── reports/
│   └── output/
├── docs/
│   ├── project_intro.md
│   ├── architecture.md
│   └── interview_notes.md
└── README.md
```

---

## 12. 推荐技术栈

### 当前阶段

```text
Python
pandas
Markdown
```

### 下一阶段

```text
FastAPI
LangChain
LangGraph
FAISS / Chroma
DeepSeek / 通义千问 / OpenAI API
pydantic
```

### 金融数据阶段

```text
pandas
numpy
matplotlib
akshare / tushare
backtrader，可选
```

### 项目展示阶段

```text
Streamlit
FastAPI
简单前端
Markdown 报告
```

### AI Coding 工具

可以了解并尝试：

```text
Qoder
Claude Code
Cursor
GitHub Copilot
Codex
```

学习重点不是“让 AI 替你写代码”，而是：

- 用 AI Coding 工具生成初版；
- 人工检查逻辑；
- 补异常处理；
- 写测试样例；
- 生成 README；
- 控制 AI 不乱改文件。

---

## 13. 面试时可以这样描述当前项目

### 简短版本

> 我在做一个基于大模型 Agent 的证券投研与数据分析自动化项目。当前阶段先从 Tool Calling 的底层能力做起，把读取 CSV、数据统计、报告保存等业务动作封装为 Python 工具，并统一返回结构化结果。下一步会继续封装渠道转化率分析、金融指标计算、RAG 文档问答和 Workflow 编排，最终让 Agent 根据自然语言任务自动选择工具并生成报告。

### 针对 AI Pilot 岗位版本

> 我理解 AI Pilot 岗位的关键不是单纯调用大模型，而是把证券业务里的投研、数据处理、策略分析、风控报告等重复流程拆成可执行工具，再由 Agent 通过工具调用和 Workflow 编排完成自动化。我现在正在做一个证券投研与数据分析流程自动化系统，先实现 CSV 数据读取、缺失值统计、指标计算和 Markdown 报告生成，后续会加入金融指标、RAG 文档检索和 Agent 自动路由能力。

---

## 14. 学习方法

### 每一步都遵循这个闭环

```text
学一个概念
→ 写一个工具函数
→ 跑一个测试样例
→ 看结构化输出
→ 思考它对应什么业务场景
→ 把它写成 README / 面试表达
```

### 不要一开始就学复杂框架

当前阶段不要急着学：

- 多 Agent；
- AutoGPT；
- 复杂 MCP Server；
- 分布式部署；
- 大模型微调；
- 高频量化策略。

先把这几个基础打稳：

1. Python 工具函数；
2. pandas 数据处理；
3. 结构化返回；
4. 错误处理；
5. Markdown 报告；
6. 任务拆解；
7. 工具调用流程。

---

## 15. 下一次继续学习时的提示词

如果换了新窗口，可以直接发这句话：

> 我正在学习 AI Pilot / Agent 工具调用与流程自动化项目。这是我的学习进度 Markdown。请先阅读文件内容，然后从“第 2 课：写渠道转化率分析工具 analyze_channel_conversion”继续带我学习。请一步一步给我代码、解释和任务。

---

## 16. 当前下一步任务清单

继续学习时，从这里开始：

1. 在 `tools.py` 增加 `analyze_channel_conversion(file_path: str)`；
2. 在 `main.py` 导入并调用它；
3. 运行 `python main.py`；
4. 检查输出里的：
   - `channel_metrics`
   - `best_signup_channel`
   - `best_payment_channel`
   - `best_signup_to_payment_channel`
5. 把运行结果发给 ChatGPT；
6. 下一步继续做：
   - 自动生成渠道分析 Markdown 报告；
   - 格式化百分比；
   - 增加业务解释；
   - 为后续 Agent 调用做准备。

---

## 17. 当前学习状态一句话总结

目前已经完成：

**项目结构搭建 + CSV 读取工具 + CSV 统计工具 + Markdown 保存工具 + 运行验证。**

下一步要完成：

**渠道转化率分析工具，并开始把业务分析逻辑封装成 Agent 可调用工具。**
