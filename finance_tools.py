import os
import math
import pandas as pd
from config import REPORT_DIR, CHART_DIR,ensure_output_dirs
import matplotlib.pyplot as plt
from pathlib import Path

def format_percent(value: float) -> str:
    """
    将小数格式化为百分比字符串。
    """
    return f"{value * 100:.2f}%"


def read_stock_price_data(file_path: str) -> dict:
    """
    读取股票价格数据，并返回基础信息。
    要求 CSV 至少包含 date 和 close 两列。
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        df = pd.read_csv(file_path)

        required_columns = ["date", "close"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                "success": False,
                "error": f"缺少必要字段：{missing_columns}"
            }

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        return {
            "success": True,
            "rows": len(df),
            "start_date": str(df["date"].iloc[0].date()),
            "end_date": str(df["date"].iloc[-1].date()),
            "start_close": float(df["close"].iloc[0]),
            "end_close": float(df["close"].iloc[-1]),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict(orient="records")
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def calculate_stock_metrics(file_path: str, risk_free_rate: float = 0.0) -> dict:
    """
    计算股票或策略净值的基础金融指标。

    指标包括：
    - 区间收益率
    - 日收益率序列
    - 年化波动率
    - 最大回撤
    - 夏普比率
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        df = pd.read_csv(file_path)

        required_columns = ["date", "close"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                "success": False,
                "error": f"缺少必要字段：{missing_columns}"
            }

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        if len(df) < 2:
            return {
                "success": False,
                "error": "数据量不足，至少需要 2 条价格数据"
            }

        df["daily_return"] = df["close"].pct_change()

        start_close = df["close"].iloc[0]
        end_close = df["close"].iloc[-1]

        total_return = end_close / start_close - 1

        daily_returns = df["daily_return"].dropna()

        if len(daily_returns) == 0:
            return {
                "success": False,
                "error": "无法计算日收益率"
            }

        daily_return_mean = daily_returns.mean()
        daily_return_std = daily_returns.std()

        annualized_volatility = daily_return_std * math.sqrt(252)

        # 最大回撤
        df["cum_value"] = df["close"] / start_close
        df["running_max"] = df["cum_value"].cummax()
        df["drawdown"] = df["cum_value"] / df["running_max"] - 1
        max_drawdown = df["drawdown"].min()

        # 夏普比率：这里使用简单版本
        # 假设 risk_free_rate 是年化无风险利率
        annualized_return = daily_return_mean * 252

        if daily_return_std == 0:
            sharpe_ratio = None
        else:
            sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

        best_day = df.loc[df["daily_return"].idxmax()]
        worst_day = df.loc[df["daily_return"].idxmin()]

        return {
            "success": True,
            "start_date": str(df["date"].iloc[0].date()),
            "end_date": str(df["date"].iloc[-1].date()),
            "start_close": round(float(start_close), 4),
            "end_close": round(float(end_close), 4),
            "total_return": round(float(total_return), 6),
            "annualized_volatility": round(float(annualized_volatility), 6),
            "max_drawdown": round(float(max_drawdown), 6),
            "sharpe_ratio": round(float(sharpe_ratio), 6) if sharpe_ratio is not None else None,
            "best_day": {
                "date": str(best_day["date"].date()),
                "daily_return": round(float(best_day["daily_return"]), 6)
            },
            "worst_day": {
                "date": str(worst_day["date"].date()),
                "daily_return": round(float(worst_day["daily_return"]), 6)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_stock_metrics_report(
    file_path: str,
    output_path: str | None = None
) -> dict:
    """
    基于股票价格数据，生成 Markdown 风险收益分析报告。
    """
    if output_path is None:
        output_path = str(REPORT_DIR / "stock_metrics_report.md")


    metrics_result = calculate_stock_metrics(file_path)

    if not metrics_result.get("success"):
        return {
            "success": False,
            "error": metrics_result.get("error", "金融指标计算失败")
        }

    total_return = metrics_result["total_return"]
    annualized_volatility = metrics_result["annualized_volatility"]
    max_drawdown = metrics_result["max_drawdown"]
    sharpe_ratio = metrics_result["sharpe_ratio"]

    if total_return > 0:
        return_conclusion = "该标的在统计区间内取得正收益。"
    elif total_return < 0:
        return_conclusion = "该标的在统计区间内出现负收益。"
    else:
        return_conclusion = "该标的在统计区间内收益基本持平。"

    if max_drawdown < -0.1:
        risk_conclusion = "最大回撤相对较高，需要关注下行风险。"
    else:
        risk_conclusion = "最大回撤相对可控，但仍需结合更长时间周期判断风险。"

    if sharpe_ratio is None:
        sharpe_text = "无法计算"
    else:
        sharpe_text = f"{sharpe_ratio:.4f}"

    report_content = f"""# 股票/策略风险收益分析报告

## 1. 数据区间

- 开始日期：{metrics_result["start_date"]}
- 结束日期：{metrics_result["end_date"]}
- 起始价格：{metrics_result["start_close"]}
- 结束价格：{metrics_result["end_close"]}

---

## 2. 核心指标

| 指标 | 数值 |
|---|---:|
| 区间收益率 | {format_percent(total_return)} |
| 年化波动率 | {format_percent(annualized_volatility)} |
| 最大回撤 | {format_percent(max_drawdown)} |
| 夏普比率 | {sharpe_text} |

---

## 3. 最佳与最差单日表现

- 最佳单日：{metrics_result["best_day"]["date"]}，日收益率 {format_percent(metrics_result["best_day"]["daily_return"])}
- 最差单日：{metrics_result["worst_day"]["date"]}，日收益率 {format_percent(metrics_result["worst_day"]["daily_return"])}

---

## 4. 初步结论

{return_conclusion}

{risk_conclusion}

---

## 5. 后续可优化方向

1. 增加更长时间区间的数据；
2. 加入基准指数进行超额收益分析；
3. 增加换手率、胜率、盈亏比等策略指标；
4. 结合行业、市场环境和基本面数据进行解释；
5. 后续可以让 Agent 自动读取行情数据、计算指标并生成策略分析报告。
"""

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return {
            "success": True,
            "message": f"金融指标报告已生成：{output_path}",
            "output_path": output_path,
            "summary": {
                "total_return": total_return,
                "annualized_volatility": annualized_volatility,
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe_ratio
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def run_moving_average_backtest(
    file_path: str,
    short_window: int = 3,
    long_window: int = 5,
    initial_value: float = 1.0
) -> dict:
    """
    运行简单均线策略回测。

    策略逻辑：
    - 短期均线 > 长期均线：持仓
    - 短期均线 <= 长期均线：空仓

    注意：
    - 使用 signal.shift(1) 生成 position，避免未来函数。
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        if short_window <= 0 or long_window <= 0:
            return {
                "success": False,
                "error": "均线窗口必须为正整数"
            }

        if short_window >= long_window:
            return {
                "success": False,
                "error": "短期均线窗口必须小于长期均线窗口"
            }

        df = pd.read_csv(file_path)

        required_columns = ["date", "close"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                "success": False,
                "error": f"缺少必要字段：{missing_columns}"
            }

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        if len(df) < long_window + 2:
            return {
                "success": False,
                "error": f"数据量不足，至少需要 {long_window + 2} 条价格数据"
            }

        df["daily_return"] = df["close"].pct_change().fillna(0)

        short_ma_col = f"ma_{short_window}"
        long_ma_col = f"ma_{long_window}"

        df[short_ma_col] = df["close"].rolling(window=short_window).mean()
        df[long_ma_col] = df["close"].rolling(window=long_window).mean()

        # 当短期均线大于长期均线时，生成持仓信号
        df["signal"] = (df[short_ma_col] > df[long_ma_col]).astype(int)

        # 关键：信号延后一天生效，避免未来函数
        df["position"] = df["signal"].shift(1).fillna(0)

        df["strategy_return"] = df["position"] * df["daily_return"]

        df["strategy_value"] = (1 + df["strategy_return"]).cumprod() * initial_value
        df["benchmark_value"] = (1 + df["daily_return"]).cumprod() * initial_value

        strategy_total_return = df["strategy_value"].iloc[-1] / initial_value - 1
        benchmark_total_return = df["benchmark_value"].iloc[-1] / initial_value - 1
        excess_return = strategy_total_return - benchmark_total_return

        strategy_returns = df["strategy_return"]

        annualized_volatility = strategy_returns.std() * math.sqrt(252)
        annualized_return = strategy_returns.mean() * 252

        if annualized_volatility == 0:
            sharpe_ratio = None
        else:
            sharpe_ratio = annualized_return / annualized_volatility

        # 最大回撤
        df["strategy_running_max"] = df["strategy_value"].cummax()
        df["strategy_drawdown"] = df["strategy_value"] / df["strategy_running_max"] - 1
        max_drawdown = df["strategy_drawdown"].min()

        # 交易次数：position 从 0 到 1 或从 1 到 0 都算一次变化
        df["position_change"] = df["position"].diff().abs().fillna(0)
        trade_count = int(df["position_change"].sum())

        holding_days = int((df["position"] == 1).sum())
        total_days = len(df)
        holding_ratio = holding_days / total_days

        latest_signal = "持仓" if int(df["signal"].iloc[-1]) == 1 else "空仓"

        # 最近 5 天记录，方便报告展示
        recent_records = []
        for _, row in df.tail(5).iterrows():
            recent_records.append({
                "date": str(row["date"].date()),
                "close": round(float(row["close"]), 4),
                short_ma_col: None if pd.isna(row[short_ma_col]) else round(float(row[short_ma_col]), 4),
                long_ma_col: None if pd.isna(row[long_ma_col]) else round(float(row[long_ma_col]), 4),
                "signal": int(row["signal"]),
                "position": int(row["position"]),
                "strategy_value": round(float(row["strategy_value"]), 4),
                "benchmark_value": round(float(row["benchmark_value"]), 4)
            })

        return {
            "success": True,
            "strategy_name": f"MA{short_window}-MA{long_window} 均线策略",
            "start_date": str(df["date"].iloc[0].date()),
            "end_date": str(df["date"].iloc[-1].date()),
            "short_window": short_window,
            "long_window": long_window,
            "strategy_total_return": round(float(strategy_total_return), 6),
            "benchmark_total_return": round(float(benchmark_total_return), 6),
            "excess_return": round(float(excess_return), 6),
            "annualized_volatility": round(float(annualized_volatility), 6),
            "max_drawdown": round(float(max_drawdown), 6),
            "sharpe_ratio": round(float(sharpe_ratio), 6) if sharpe_ratio is not None else None,
            "trade_count": trade_count,
            "holding_days": holding_days,
            "total_days": total_days,
            "holding_ratio": round(float(holding_ratio), 6),
            "latest_signal": latest_signal,
            "recent_records": recent_records
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def generate_backtest_report(
    file_path: str,
    output_path: str | None = None,
    short_window: int = 3,
    long_window: int = 5
) -> dict:
    """
    生成均线策略回测 Markdown 报告。
    """
    if output_path is None:
        output_path = str(REPORT_DIR / f"backtest_report_MA{short_window}_MA{long_window}.md")
    
    backtest_result = run_moving_average_backtest(
        file_path=file_path,
        short_window=short_window,
        long_window=long_window
    )

    if not backtest_result.get("success"):
        return {
            "success": False,
            "error": backtest_result.get("error", "回测失败")
        }
    chart_result = generate_backtest_charts(
        file_path=file_path,
        short_window=short_window,
        long_window=long_window
    )

    sharpe_ratio = backtest_result.get("sharpe_ratio")
    sharpe_text = "无法计算" if sharpe_ratio is None else f"{sharpe_ratio:.4f}"

    if backtest_result["strategy_total_return"] > backtest_result["benchmark_total_return"]:
        performance_comment = "策略收益高于买入持有基准，说明该均线规则在当前样本区间内有一定超额表现。"
    else:
        performance_comment = "策略收益低于或接近买入持有基准，说明该均线规则在当前样本区间内优势不明显。"

    if backtest_result["max_drawdown"] < -0.1:
        risk_comment = "策略最大回撤较高，需要进一步关注下行风险和止损机制。"
    else:
        risk_comment = "策略最大回撤相对可控，但当前样本较短，仍需更长周期验证。"

    recent_rows = []
    for item in backtest_result["recent_records"]:
        recent_rows.append(
            f"| {item['date']} "
            f"| {item['close']} "
            f"| {item[f'ma_{short_window}']} "
            f"| {item[f'ma_{long_window}']} "
            f"| {item['signal']} "
            f"| {item['position']} "
            f"| {item['strategy_value']} "
            f"| {item['benchmark_value']} |"
        )

    recent_table = "\n".join(recent_rows)

    chart_section = ""

    if chart_result.get("success"):
        nav_chart_path = f"../charts/backtest_nav_MA{short_window}_MA{long_window}.png"
        drawdown_chart_path = f"../charts/backtest_drawdown_MA{short_window}_MA{long_window}.png"

        chart_section = f"""
---

## 5. 回测图表

### 5.1 策略净值 vs 买入持有净值

![策略净值曲线]({nav_chart_path})

### 5.2 策略回撤曲线

![策略回撤曲线]({drawdown_chart_path})
"""
    else:
        chart_section = f"""
---

## 5. 回测图表

图表生成失败：{chart_result.get("error")}
"""

    report_content = f"""# 均线策略回测报告

## 1. 策略说明

本报告基于 **{backtest_result["strategy_name"]}** 进行简单历史回测。

策略规则：

- 短期均线 > 长期均线：生成持仓信号；
- 短期均线 <= 长期均线：生成空仓信号；
- 为避免未来函数，信号在下一交易日生效。

---

## 2. 回测区间

- 开始日期：{backtest_result["start_date"]}
- 结束日期：{backtest_result["end_date"]}
- 短期均线窗口：{backtest_result["short_window"]}
- 长期均线窗口：{backtest_result["long_window"]}

---

## 3. 核心回测指标

| 指标 | 数值 |
|---|---:|
| 策略区间收益率 | {format_percent(backtest_result["strategy_total_return"])} |
| 买入持有收益率 | {format_percent(backtest_result["benchmark_total_return"])} |
| 超额收益 | {format_percent(backtest_result["excess_return"])} |
| 年化波动率 | {format_percent(backtest_result["annualized_volatility"])} |
| 最大回撤 | {format_percent(backtest_result["max_drawdown"])} |
| 夏普比率 | {sharpe_text} |
| 交易次数 | {backtest_result["trade_count"]} |
| 持仓天数 | {backtest_result["holding_days"]} / {backtest_result["total_days"]} |
| 持仓比例 | {format_percent(backtest_result["holding_ratio"])} |
| 最新信号 | {backtest_result["latest_signal"]} |

---

## 4. 最近 5 天信号明细

| 日期 | 收盘价 | MA{short_window} | MA{long_window} | 信号 | 实际持仓 | 策略净值 | 基准净值 |
|---|---:|---:|---:|---:|---:|---:|---:|
{recent_table}

{chart_section}
---

## 6. 初步结论

{performance_comment}

{risk_comment}

---

## 7. 局限性说明

1. 当前策略只是简单均线规则，不代表真实投资建议；
2. 当前回测未考虑交易手续费、滑点、冲击成本；
3. 当前样本数据较短，指标稳定性有限；
4. 后续可以加入更多参数组合、基准指数和风险控制规则；
5. 实际策略研究需要进行样本外测试和更严格的风险评估。
"""

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return {
            "success": True,
            "message": f"回测报告已生成：{output_path}",
            "output_path": output_path,
            "chart_result": chart_result,
            "summary": {
                "strategy_name": backtest_result["strategy_name"],
                "strategy_total_return": backtest_result["strategy_total_return"],
                "benchmark_total_return": backtest_result["benchmark_total_return"],
                "excess_return": backtest_result["excess_return"],
                "max_drawdown": backtest_result["max_drawdown"],
                "sharpe_ratio": backtest_result["sharpe_ratio"],
                "latest_signal": backtest_result["latest_signal"]
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
def optimize_moving_average_parameters(
    file_path: str,
    short_windows=None,
    long_windows=None,
    sort_by: str = "sharpe_ratio"
) -> dict:
    """
    批量扫描不同均线参数组合，并找出表现较好的参数。

    默认扫描：
    short_windows = [3, 5, 7]
    long_windows = [10, 15, 20]

    sort_by 支持：
    - sharpe_ratio
    - strategy_total_return
    - excess_return
    - max_drawdown
    """
    if short_windows is None:
        short_windows = [3, 5, 7]

    if long_windows is None:
        long_windows = [10, 15, 20]

    valid_sort_fields = [
        "sharpe_ratio",
        "strategy_total_return",
        "excess_return",
        "max_drawdown"
    ]

    if sort_by not in valid_sort_fields:
        return {
            "success": False,
            "error": f"不支持的排序字段：{sort_by}，可选值：{valid_sort_fields}"
        }

    results = []
    failed_results = []

    for short_window in short_windows:
        for long_window in long_windows:
            if short_window >= long_window:
                continue

            backtest_result = run_moving_average_backtest(
                file_path=file_path,
                short_window=short_window,
                long_window=long_window
            )

            if not backtest_result.get("success"):
                failed_results.append({
                    "short_window": short_window,
                    "long_window": long_window,
                    "error": backtest_result.get("error")
                })
                continue

            results.append({
                "strategy_name": backtest_result["strategy_name"],
                "short_window": short_window,
                "long_window": long_window,
                "strategy_total_return": backtest_result["strategy_total_return"],
                "benchmark_total_return": backtest_result["benchmark_total_return"],
                "excess_return": backtest_result["excess_return"],
                "annualized_volatility": backtest_result["annualized_volatility"],
                "max_drawdown": backtest_result["max_drawdown"],
                "sharpe_ratio": backtest_result["sharpe_ratio"],
                "trade_count": backtest_result["trade_count"],
                "holding_ratio": backtest_result["holding_ratio"],
                "latest_signal": backtest_result["latest_signal"]
            })

    if not results:
        return {
            "success": False,
            "error": "没有任何参数组合成功完成回测",
            "failed_results": failed_results
        }

    def sort_key(item: dict):
        value = item.get(sort_by)

        if value is None:
            return float("-inf")

        return value

    # max_drawdown 是负数，越接近 0 越好，所以也可以直接 reverse=True
    sorted_results = sorted(
        results,
        key=sort_key,
        reverse=True
    )

    best_result = sorted_results[0]

    return {
        "success": True,
        "sort_by": sort_by,
        "total_combinations": len(results),
        "failed_combinations": failed_results,
        "best_result": best_result,
        "all_results": sorted_results
    }

def generate_parameter_scan_report(
    file_path: str,
    output_path: str | None = None,
    sort_by: str = "sharpe_ratio"
) -> dict:
    """
    生成均线策略参数扫描 Markdown 报告。
    """
    if output_path is None:
        output_path = str(REPORT_DIR / f"parameter_scan_report_{sort_by}.md")


    scan_result = optimize_moving_average_parameters(
        file_path=file_path,
        sort_by=sort_by
    )

    if not scan_result.get("success"):
        return {
            "success": False,
            "error": scan_result.get("error", "参数扫描失败")
        }
    
    chart_result=generate_parameter_scan_chart(
        file_path=file_path,
        sort_by=sort_by
    )

    best_result = scan_result["best_result"]
    all_results = scan_result["all_results"]

    sort_by_name_mapping = {
        "sharpe_ratio": "夏普比率",
        "strategy_total_return": "策略收益率",
        "excess_return": "超额收益",
        "max_drawdown": "最大回撤"
    }

    sort_by_name = sort_by_name_mapping.get(sort_by, sort_by)

    table_rows = []
    for item in all_results:
        sharpe_ratio = item.get("sharpe_ratio")
        sharpe_text = "无法计算" if sharpe_ratio is None else f"{sharpe_ratio:.4f}"

        table_rows.append(
            f"| {item['strategy_name']} "
            f"| {format_percent(item['strategy_total_return'])} "
            f"| {format_percent(item['benchmark_total_return'])} "
            f"| {format_percent(item['excess_return'])} "
            f"| {format_percent(item['annualized_volatility'])} "
            f"| {format_percent(item['max_drawdown'])} "
            f"| {sharpe_text} "
            f"| {item['trade_count']} "
            f"| {format_percent(item['holding_ratio'])} "
            f"| {item['latest_signal']} |"
        )

    table_content = "\n".join(table_rows)

    best_sharpe = best_result.get("sharpe_ratio")
    best_sharpe_text = "无法计算" if best_sharpe is None else f"{best_sharpe:.4f}"

    if best_result["strategy_total_return"] > best_result["benchmark_total_return"]:
        performance_comment = "最佳参数组合在当前样本区间内跑赢买入持有基准。"
    else:
        performance_comment = "最佳参数组合在当前样本区间内仍未跑赢买入持有基准，说明当前样本可能更适合简单持有，或均线策略存在滞后。"

    if best_result["max_drawdown"] < -0.1:
        risk_comment = "最佳参数组合的最大回撤仍然偏高，需要进一步加入风控规则。"
    else:
        risk_comment = "最佳参数组合的最大回撤相对可控，但仍需更长周期数据验证稳定性。"
    
    chart_section = ""

    if chart_result.get("success"):
        chart_path = f"../charts/parameter_scan_{sort_by}.png"

        chart_section = f"""
---

## 参数扫描图表

![参数扫描图表]({chart_path})
"""
    else:
        chart_section = f"""
---

## 参数扫描图表

图表生成失败：{chart_result.get("error")}
"""
    report_content = f"""# 均线策略参数扫描报告

## 1. 扫描目标

本报告对多组均线参数进行批量回测，比较不同参数组合在当前样本区间内的表现。

默认扫描范围：

- 短期均线窗口：3、5、7
- 长期均线窗口：10、15、20

排序指标：**{sort_by_name}**

---

## 2. 最佳参数组合

当前按 **{sort_by_name}** 排序后，表现最好的参数组合为：

- 策略名称：**{best_result["strategy_name"]}**
- 短期均线窗口：{best_result["short_window"]}
- 长期均线窗口：{best_result["long_window"]}
- 策略收益率：{format_percent(best_result["strategy_total_return"])}
- 买入持有收益率：{format_percent(best_result["benchmark_total_return"])}
- 超额收益：{format_percent(best_result["excess_return"])}
- 年化波动率：{format_percent(best_result["annualized_volatility"])}
- 最大回撤：{format_percent(best_result["max_drawdown"])}
- 夏普比率：{best_sharpe_text}
- 最新信号：{best_result["latest_signal"]}

---

## 3. 参数扫描明细

| 策略 | 策略收益率 | 买入持有收益率 | 超额收益 | 年化波动率 | 最大回撤 | 夏普比率 | 交易次数 | 持仓比例 | 最新信号 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
{table_content}

{chart_section}
---

## 4. 初步结论

{performance_comment}

{risk_comment}

需要注意的是，参数扫描只能说明某些参数在当前样本区间内表现较好，不能直接证明其未来有效。真实策略研究中还需要进行样本外测试、滚动窗口验证，并加入交易成本、滑点、止损和风险约束。

---

## 5. 后续优化方向

1. 增加更多历史数据，避免样本过短；
2. 增加样本外测试，降低过拟合风险；
3. 加入手续费、滑点和冲击成本；
4. 增加基准指数对比；
5. 支持更多策略参数和风险控制规则；
6. 让 Agent 自动比较参数组合并生成策略优化建议。
"""

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return {
            "success": True,
            "message": f"参数扫描报告已生成：{output_path}",
            "output_path": output_path,
            "summary": {
                "sort_by": sort_by,
                "total_combinations": scan_result["total_combinations"],
                "best_result": best_result
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
def generate_strategy_research_summary(
    file_path: str,
    output_path: str | None = None,
    sort_by: str = "sharpe_ratio"
) -> dict:
    """
    生成策略研究总结报告。

    综合包含：
    - 标的基础风险收益指标
    - 默认 MA3-MA5 回测结果
    - 参数扫描最佳结果
    - 策略表现判断
    - 风险提示和后续优化建议
    """
    if output_path is None:
        output_path = str(REPORT_DIR / f"strategy_research_summary_{sort_by}.md")
    

    metrics_result = calculate_stock_metrics(file_path)
    if not metrics_result.get("success"):
        return {
            "success": False,
            "error": f"基础金融指标计算失败：{metrics_result.get('error')}"
        }

    default_backtest_result = run_moving_average_backtest(
        file_path=file_path,
        short_window=3,
        long_window=5
    )
    if not default_backtest_result.get("success"):
        return {
            "success": False,
            "error": f"默认均线策略回测失败：{default_backtest_result.get('error')}"
        }

    scan_result = optimize_moving_average_parameters(
        file_path=file_path,
        sort_by=sort_by
    )
    if not scan_result.get("success"):
        return {
            "success": False,
            "error": f"参数扫描失败：{scan_result.get('error')}"
        }

    best_result = scan_result["best_result"]
    best_short_window= best_result["short_window"]
    best_long_window = best_result["long_window"]

    chart_result = generate_backtest_charts(
        file_path=file_path,
        short_window=best_short_window,
        long_window=best_long_window
    )

    chart_section=""

    if chart_result.get("success"):
        nav_chart_path = f"../charts/backtest_nav_MA{best_short_window}_MA{best_long_window}.png"
        drawdown_chart_path = f"../charts/backtest_drawdown_MA{best_short_window}_MA{best_long_window}.png"

        chart_section = f"""
---
## 6. 策略图表

### 6.1 最佳策略净值 vs 买入持有净值

![最佳策略净值曲线]({nav_chart_path})

### 6.2 最佳策略回撤曲线

![最佳策略回撤曲线]({drawdown_chart_path})
"""
    else:
        chart_section = f"""
---

## 6. 策略图表

图表生成失败：{chart_result.get("error")}
"""
        
    sort_by_name_mapping = {
        "sharpe_ratio": "夏普比率",
        "strategy_total_return": "策略收益率",
        "excess_return": "超额收益",
        "max_drawdown": "最大回撤"
    }
    sort_by_name = sort_by_name_mapping.get(sort_by, sort_by)

    metrics_sharpe = metrics_result.get("sharpe_ratio")
    metrics_sharpe_text = "无法计算" if metrics_sharpe is None else f"{metrics_sharpe:.4f}"

    default_sharpe = default_backtest_result.get("sharpe_ratio")
    default_sharpe_text = "无法计算" if default_sharpe is None else f"{default_sharpe:.4f}"

    best_sharpe = best_result.get("sharpe_ratio")
    best_sharpe_text = "无法计算" if best_sharpe is None else f"{best_sharpe:.4f}"

    # 标的本身表现判断
    if metrics_result["total_return"] > 0:
        asset_comment = "标的在当前样本区间内整体上涨，买入持有获得正收益。"
    elif metrics_result["total_return"] < 0:
        asset_comment = "标的在当前样本区间内整体下跌，买入持有出现亏损。"
    else:
        asset_comment = "标的在当前样本区间内整体收益基本持平。"

    # 默认策略表现判断
    if default_backtest_result["strategy_total_return"] > default_backtest_result["benchmark_total_return"]:
        default_strategy_comment = "默认 MA3-MA5 策略跑赢买入持有基准。"
    else:
        default_strategy_comment = "默认 MA3-MA5 策略未跑赢买入持有基准，可能存在信号滞后或趋势行情下空仓损失。"

    # 最佳参数表现判断
    if best_result["strategy_total_return"] > best_result["benchmark_total_return"]:
        best_strategy_comment = "参数扫描得到的最佳组合跑赢买入持有基准。"
    else:
        best_strategy_comment = "参数扫描得到的最佳组合仍未跑赢买入持有基准，说明当前样本中均线策略整体优势有限。"

    # 综合建议
    if best_result["excess_return"] > 0:
        final_suggestion = (
            "当前样本中存在一定均线策略优化空间，但仍需要通过样本外测试、"
            "交易成本约束和更长周期验证策略稳定性。"
        )
    else:
        final_suggestion = (
            "当前样本中均线策略整体未能产生正超额收益，建议不要直接使用当前参数，"
            "后续应扩大样本区间、增加震荡和下跌行情数据，并引入风控或过滤条件。"
        )

    report_content = f"""# 策略研究总结报告

## 1. 研究目标

本报告基于股票/策略价格数据，对标的基础风险收益特征、默认均线策略表现以及多组均线参数扫描结果进行综合分析。

本报告主要回答以下问题：

1. 标的本身在样本区间内表现如何；
2. 默认 MA3-MA5 均线策略是否有效；
3. 多组参数扫描后，哪组参数表现相对最好；
4. 当前策略是否具备进一步研究价值；
5. 后续应该如何优化。

---

## 2. 数据区间

- 开始日期：{metrics_result["start_date"]}
- 结束日期：{metrics_result["end_date"]}
- 起始价格：{metrics_result["start_close"]}
- 结束价格：{metrics_result["end_close"]}

---

## 3. 标的基础风险收益指标

| 指标 | 数值 |
|---|---:|
| 区间收益率 | {format_percent(metrics_result["total_return"])} |
| 年化波动率 | {format_percent(metrics_result["annualized_volatility"])} |
| 最大回撤 | {format_percent(metrics_result["max_drawdown"])} |
| 夏普比率 | {metrics_sharpe_text} |

初步判断：

{asset_comment}

---

## 4. 默认 MA3-MA5 策略表现

| 指标 | 数值 |
|---|---:|
| 策略收益率 | {format_percent(default_backtest_result["strategy_total_return"])} |
| 买入持有收益率 | {format_percent(default_backtest_result["benchmark_total_return"])} |
| 超额收益 | {format_percent(default_backtest_result["excess_return"])} |
| 年化波动率 | {format_percent(default_backtest_result["annualized_volatility"])} |
| 最大回撤 | {format_percent(default_backtest_result["max_drawdown"])} |
| 夏普比率 | {default_sharpe_text} |
| 交易次数 | {default_backtest_result["trade_count"]} |
| 持仓比例 | {format_percent(default_backtest_result["holding_ratio"])} |
| 最新信号 | {default_backtest_result["latest_signal"]} |

初步判断：

{default_strategy_comment}

---

## 5. 参数扫描最佳组合

本次参数扫描按 **{sort_by_name}** 排序，共测试 **{scan_result["total_combinations"]}** 组参数。

最佳参数组合：

| 指标 | 数值 |
|---|---:|
| 策略名称 | {best_result["strategy_name"]} |
| 短期均线窗口 | {best_result["short_window"]} |
| 长期均线窗口 | {best_result["long_window"]} |
| 策略收益率 | {format_percent(best_result["strategy_total_return"])} |
| 买入持有收益率 | {format_percent(best_result["benchmark_total_return"])} |
| 超额收益 | {format_percent(best_result["excess_return"])} |
| 年化波动率 | {format_percent(best_result["annualized_volatility"])} |
| 最大回撤 | {format_percent(best_result["max_drawdown"])} |
| 夏普比率 | {best_sharpe_text} |
| 交易次数 | {best_result["trade_count"]} |
| 持仓比例 | {format_percent(best_result["holding_ratio"])} |
| 最新信号 | {best_result["latest_signal"]} |

初步判断：

{best_strategy_comment}

---

## 6. 综合结论

{final_suggestion}

需要特别注意：

- 当前回测未考虑手续费、滑点和冲击成本；
- 当前样本长度较短，夏普比率和年化波动率可能不稳定；
- 参数扫描存在样本内过拟合风险；
- 当前结果仅用于策略研究流程验证，不构成任何投资建议。

---

## 7. 后续优化方向

1. 接入更长周期行情数据；
2. 增加样本外测试；
3. 进行滚动窗口参数验证；
4. 加入交易成本和滑点假设；
5. 增加止损、止盈和仓位控制；
6. 对比基准指数和行业指数；
7. 让 Agent 自动生成策略优化建议和实验记录。

{chart_section}
"""

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return {
            "success": True,
            "message": f"策略研究总结报告已生成：{output_path}",
            "output_path": output_path,
            "chart_result": chart_result,
            "summary": {
                "sort_by": sort_by,
                "asset_total_return": metrics_result["total_return"],
                "default_strategy_return": default_backtest_result["strategy_total_return"],
                "default_excess_return": default_backtest_result["excess_return"],
                "best_strategy_name": best_result["strategy_name"],
                "best_strategy_return": best_result["strategy_total_return"],
                "best_excess_return": best_result["excess_return"],
                "best_max_drawdown": best_result["max_drawdown"],
                "best_sharpe_ratio": best_result["sharpe_ratio"],
                "final_suggestion": final_suggestion
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def generate_backtest_charts(
    file_path: str,
    output_dir: str | None = None,
    short_window: int = 3,
    long_window: int = 5
) -> dict:
    """
    生成均线策略回测图表。

    输出：
    - 策略净值 vs 买入持有净值曲线
    - 策略回撤曲线
    """
    ensure_output_dirs()

    if output_dir is None:
        output_dir = str(CHART_DIR)

    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在：{file_path}"
        }

    try:
        if short_window <= 0 or long_window <= 0:
            return {
                "success": False,
                "error": "均线窗口必须为正整数"
            }

        if short_window >= long_window:
            return {
                "success": False,
                "error": "短期均线窗口必须小于长期均线窗口"
            }

        df = pd.read_csv(file_path)

        required_columns = ["date", "close"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                "success": False,
                "error": f"缺少必要字段：{missing_columns}"
            }

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        if len(df) < long_window + 2:
            return {
                "success": False,
                "error": f"数据量不足，至少需要 {long_window + 2} 条价格数据"
            }

        df["daily_return"] = df["close"].pct_change().fillna(0)

        short_ma_col = f"ma_{short_window}"
        long_ma_col = f"ma_{long_window}"

        df[short_ma_col] = df["close"].rolling(window=short_window).mean()
        df[long_ma_col] = df["close"].rolling(window=long_window).mean()

        # 生成信号：短期均线 > 长期均线时持仓
        df["signal"] = (df[short_ma_col] > df[long_ma_col]).astype(int)

        # 信号延后一日生效，避免未来函数
        df["position"] = df["signal"].shift(1).fillna(0)

        df["strategy_return"] = df["position"] * df["daily_return"]

        df["strategy_value"] = (1 + df["strategy_return"]).cumprod()
        df["benchmark_value"] = (1 + df["daily_return"]).cumprod()

        df["strategy_running_max"] = df["strategy_value"].cummax()
        df["strategy_drawdown"] = df["strategy_value"] / df["strategy_running_max"] - 1

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        nav_chart_path = output_path / f"backtest_nav_MA{short_window}_MA{long_window}.png"
        drawdown_chart_path = output_path / f"backtest_drawdown_MA{short_window}_MA{long_window}.png"

        # 图 1：策略净值 vs 买入持有净值
        plt.figure(figsize=(10, 5))
        plt.plot(df["date"], df["strategy_value"], label="Strategy NAV")
        plt.plot(df["date"], df["benchmark_value"], label="Buy and Hold")
        plt.title(f"MA{short_window}-MA{long_window} Strategy NAV vs Benchmark")
        plt.xlabel("Date")
        plt.ylabel("Net Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(nav_chart_path, dpi=150)
        plt.close()

        # 图 2：策略回撤曲线
        plt.figure(figsize=(10, 5))
        plt.plot(df["date"], df["strategy_drawdown"], label="Strategy Drawdown")
        plt.title(f"MA{short_window}-MA{long_window} Strategy Drawdown")
        plt.xlabel("Date")
        plt.ylabel("Drawdown")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(drawdown_chart_path, dpi=150)
        plt.close()

        return {
            "success": True,
            "message": "回测图表已生成",
            "nav_chart_path": str(nav_chart_path),
            "drawdown_chart_path": str(drawdown_chart_path),
            "short_window": short_window,
            "long_window": long_window
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
def generate_parameter_scan_chart(
    file_path: str,
    output_dir: str | None = None,
    sort_by: str = "sharpe_ratio"
) -> dict:
    """
    生成均线参数扫描结果对比图。

    当前版本先生成一张柱状图：
    - 不同 MA 参数组合在指定排序指标上的表现对比
    """
    ensure_output_dirs()

    if output_dir is None:
        output_dir = str(CHART_DIR)

    try:
        scan_result = optimize_moving_average_parameters(
            file_path=file_path,
            sort_by=sort_by
        )

        if not scan_result.get("success"):
            return {
                "success": False,
                "error": scan_result.get("error", "参数扫描失败")
            }

        results = (
            scan_result.get("results")
            or scan_result.get("all_results")
            or scan_result.get("top_results")
        )

        if not results:
            return {
                "success": False,
                "error": "参数扫描结果为空，无法生成图表"
            }

        chart_data = []

        for item in results:
            short_window = item.get("short_window")
            long_window = item.get("long_window")
            metric_value = item.get(sort_by)

            if short_window is None or long_window is None:
                continue

            if metric_value is None:
                continue

            chart_data.append({
                "label": f"MA{short_window}-MA{long_window}",
                "value": metric_value
            })

        if not chart_data:
            return {
                "success": False,
                "error": f"没有可用于绘图的 {sort_by} 数据"
            }

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        chart_path = output_path / f"parameter_scan_{sort_by}.png"

        labels = [item["label"] for item in chart_data]
        values = [item["value"] for item in chart_data]

        metric_name_map = {
            "sharpe_ratio": "Sharpe Ratio",
            "strategy_total_return": "Strategy Total Return",
            "excess_return": "Excess Return",
            "max_drawdown": "Max Drawdown"
        }

        metric_name = metric_name_map.get(sort_by, sort_by)

        plt.figure(figsize=(10, 5))
        plt.bar(labels, values)
        plt.title(f"Parameter Scan Comparison by {metric_name}")
        plt.xlabel("MA Parameter")
        plt.ylabel(metric_name)
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y")
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150)
        plt.close()

        return {
            "success": True,
            "message": "参数扫描图表已生成",
            "chart_path": str(chart_path),
            "sort_by": sort_by,
            "total_combinations": len(chart_data)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }