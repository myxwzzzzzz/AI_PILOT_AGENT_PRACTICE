import os
import pandas as pd
from config import REPORT_DIR

def format_percent(value: float) -> str:
    """
    将小数格式化为百分比字符串。
    例如：0.1767 -> 17.67%
    """
    return f"{value * 100:.2f}%"

def read_csv_file(file_path: str) -> dict:
    """
    读取 CSV 数据文件，校验文件合法性，并返回文件基础信息 + 前 5 行数据预览
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        df = pd.read_csv(file_path)

        return {
            "success": True,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict(orient="records")
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def summarize_csv(file_path: str) -> dict:
    """
    对 CSV 文件做基础统计。
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        df = pd.read_csv(file_path)

        return {
            "success": True,
            "shape": df.shape,
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def save_markdown_report(content: str, output_path: str) -> dict:
    """
    保存 Markdown 报告。
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "message": f"报告已保存到：{output_path}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
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

        # 按渠道汇总数据
        channel_df = (
            df.groupby("channel", as_index=False)
            .agg({
                "visits": "sum",
                "signups": "sum",
                "payments": "sum"
            })
        )

        # 计算转化率，避免除以 0
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

        # 找出表现最好的渠道
        best_signup_channel = channel_df.sort_values(
            by="signup_rate", ascending=False
        ).iloc[0]

        best_payment_channel = channel_df.sort_values(
            by="payment_rate", ascending=False
        ).iloc[0]

        best_signup_to_payment_channel = channel_df.sort_values(
            by="signup_to_payment_rate", ascending=False
        ).iloc[0]

        # 转成便于 Agent 读取的结构
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

def generate_channel_analysis_report(
    file_path: str,
     output_path: str | None = None
) -> dict:
    """
    基于渠道转化率分析结果，自动生成 Markdown 分析报告。
    """
    if output_path is None:
        output_path = str(REPORT_DIR / "channel_analysis_report.md")

    analysis_result = analyze_channel_conversion(file_path)

    if not analysis_result.get("success"):
        return {
            "success": False,
            "error": analysis_result.get("error", "渠道转化率分析失败")
        }

    channel_metrics = analysis_result["channel_metrics"]

    # 按付费转化率从高到低排序，方便报告阅读
    channel_metrics = sorted(
        channel_metrics,
        key=lambda x: x["payment_rate"],
        reverse=True
    )

    best_signup_channel = analysis_result["best_signup_channel"]
    best_payment_channel = analysis_result["best_payment_channel"]
    best_signup_to_payment_channel = analysis_result["best_signup_to_payment_channel"]

    # 生成 Markdown 表格
    table_rows = []
    for item in channel_metrics:
        row = (
            f"| {item['channel']} "
            f"| {int(item['visits'])} "
            f"| {int(item['signups'])} "
            f"| {int(item['payments'])} "
            f"| {format_percent(item['signup_rate'])} "
            f"| {format_percent(item['payment_rate'])} "
            f"| {format_percent(item['signup_to_payment_rate'])} |"
        )
        table_rows.append(row)

    table_content = "\n".join(table_rows)

    # 判断三个最优指标是否都属于同一个渠道
    best_channels = {
        best_signup_channel["channel"],
        best_payment_channel["channel"],
        best_signup_to_payment_channel["channel"]
    }

    if len(best_channels) == 1:
        overall_conclusion = (
            f"{best_payment_channel['channel']}在注册转化率、付费转化率、"
            f"注册到付费转化率三个指标上均表现最好，是当前整体转化质量最高的渠道。"
        )
    else:
        overall_conclusion = (
            f"注册转化率最高的渠道是{best_signup_channel['channel']}，"
            f"付费转化率最高的渠道是{best_payment_channel['channel']}，"
            f"注册到付费转化率最高的渠道是{best_signup_to_payment_channel['channel']}。"
            f"不同渠道在不同转化阶段表现存在差异，建议进一步拆解用户来源和转化链路。"
        )

    report_content = f"""# 渠道转化率分析报告

## 1. 分析目标

本报告基于渠道访问、注册和付费数据，分析不同渠道在用户转化链路中的表现，重点关注以下三个指标：

- 注册转化率 = 注册数 / 访问量
- 付费转化率 = 付费数 / 访问量
- 注册到付费转化率 = 付费数 / 注册数

---

## 2. 总体结论

{overall_conclusion}

具体来看：

- 注册转化率最高的渠道：**{best_signup_channel['channel']}**，注册转化率为 **{format_percent(best_signup_channel['signup_rate'])}**
- 付费转化率最高的渠道：**{best_payment_channel['channel']}**，付费转化率为 **{format_percent(best_payment_channel['payment_rate'])}**
- 注册到付费转化率最高的渠道：**{best_signup_to_payment_channel['channel']}**，注册到付费转化率为 **{format_percent(best_signup_to_payment_channel['signup_to_payment_rate'])}**

---

## 3. 渠道指标明细

| 渠道 | 访问量 | 注册数 | 付费数 | 注册转化率 | 付费转化率 | 注册到付费转化率 |
|---|---:|---:|---:|---:|---:|---:|
{table_content}

---

## 4. 初步业务建议

1. **优先复盘高转化渠道**  
   对表现最好的渠道进行内容、投放策略、用户画像和转化路径复盘，提炼可复制经验。

2. **关注低转化渠道的问题环节**  
   如果某个渠道访问量不低但注册或付费转化率偏低，说明可能存在用户质量、落地页、产品匹配度或转化路径问题。

3. **继续拆分日期维度观察趋势**  
   当前报告基于汇总数据，后续可以进一步按日期分析各渠道转化率变化，判断表现是否稳定。

4. **结合成本数据评估 ROI**  
   当前只分析了转化效率，后续如果加入投放成本，可以进一步计算获客成本和投入产出比。

---

## 5. 工具调用说明

本报告由 Python 工具函数自动生成，主要流程如下：

1. 读取 CSV 数据；
2. 按渠道聚合访问量、注册数、付费数；
3. 计算注册转化率、付费转化率、注册到付费转化率；
4. 识别各指标最优渠道；
5. 自动生成 Markdown 分析报告。
"""

    save_result = save_markdown_report(report_content, output_path)

    if not save_result.get("success"):
        return save_result

    return {
        "success": True,
        "message": f"渠道分析报告已生成：{output_path}",
        "output_path": output_path,
        "summary": {
            "best_signup_channel": best_signup_channel,
            "best_payment_channel": best_payment_channel,
            "best_signup_to_payment_channel": best_signup_to_payment_channel
        }
    }