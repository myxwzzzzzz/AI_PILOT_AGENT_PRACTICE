def format_percent(value: float) -> str:
    """
    将小数格式化为百分比字符串。
    """
    return f"{value * 100:.2f}%"


def format_response(route_result: dict) -> str:
    """
    将路由器返回的工具结果，格式化为自然语言回答。
    """
    if route_result.get("is_workflow"):
        from workflow_runner import format_workflow_result

        return format_workflow_result(route_result)

    if route_result.get("answer_type") == "rag_qa":
        answer = route_result.get("answer", "")

        sources = route_result.get("retrieved_chunks", [])
        source_lines = []

        for chunk in sources:
            source_lines.append(
                f"- {chunk.get('chunk_id')}（score={chunk.get('score')}，source={chunk.get('source')}）"
            )

        if source_lines:
            return (
                f"{answer}\n\n"
                "参考的本地知识片段：\n"
                + "\n".join(source_lines)
            )

        return answer
    if not route_result.get("success"):
        error = route_result.get("error", "任务执行失败")
        suggestion = route_result.get("suggestion", "")
        if suggestion:
            return f"任务未能执行：{error}\n建议：{suggestion}"
        return f"任务未能执行：{error}"

    selected_tool = route_result.get("selected_tool")
    tool_result = route_result.get("tool_result", {})

    if not tool_result.get("success"):
        return f"工具执行失败：{tool_result.get('error', '未知错误')}"

    if selected_tool == "read_csv_file":
        return format_read_csv_response(tool_result)

    if selected_tool == "summarize_csv":
        return format_summarize_csv_response(tool_result)

    if selected_tool == "analyze_channel_conversion":
        return format_channel_conversion_response(tool_result)

    if selected_tool == "generate_channel_analysis_report":
        return format_report_generation_response(tool_result)
    
    if selected_tool == "read_stock_price_data":
        return format_read_stock_price_response(tool_result)

    if selected_tool == "calculate_stock_metrics":
        return format_stock_metrics_response(tool_result)

    if selected_tool == "generate_stock_metrics_report":
        return format_stock_report_generation_response(tool_result)
    
    if selected_tool == "run_moving_average_backtest":
        return format_backtest_response(tool_result)
    
    if selected_tool == "generate_backtest_charts":
        return format_backtest_charts_response(tool_result)

    if selected_tool == "generate_backtest_report":
        return format_backtest_report_generation_response(tool_result)
    
    if selected_tool == "optimize_moving_average_parameters":
        return format_parameter_scan_response(tool_result)
   
    if selected_tool == "generate_parameter_scan_chart":
        return format_parameter_scan_chart_response(tool_result)

    if selected_tool == "generate_parameter_scan_report":
        return format_parameter_scan_report_generation_response(tool_result)
    
    if selected_tool == "generate_strategy_research_summary":
        return format_strategy_research_summary_response(tool_result)

    return "任务已完成，但暂时没有对应的格式化输出。"


def format_read_csv_response(tool_result: dict) -> str:
    """
    格式化 CSV 读取结果。
    """
    rows = tool_result.get("rows")
    columns = tool_result.get("columns", [])
    preview = tool_result.get("preview", [])

    column_text = "、".join(columns)

    return f"""已成功读取 CSV 文件。

数据共有 **{rows}** 行，包含以下字段：

{column_text}

前几行数据预览：

{preview}
"""


def format_summarize_csv_response(tool_result: dict) -> str:
    """
    格式化 CSV 统计结果。
    """
    shape = tool_result.get("shape")
    columns = tool_result.get("columns", [])
    missing_values = tool_result.get("missing_values", {})

    missing_text_list = []
    for column, count in missing_values.items():
        missing_text_list.append(f"- {column}：{count} 个缺失值")

    missing_text = "\n".join(missing_text_list)

    return f"""已完成数据概览分析。

数据规模：**{shape[0]} 行，{shape[1]} 列**

字段包括：

{", ".join(columns)}

缺失值情况：

{missing_text}
"""


def format_channel_conversion_response(tool_result: dict) -> str:
    """
    格式化渠道转化率分析结果。
    """
    best_signup = tool_result["best_signup_channel"]
    best_payment = tool_result["best_payment_channel"]
    best_signup_to_payment = tool_result["best_signup_to_payment_channel"]

    channel_metrics = tool_result.get("channel_metrics", [])

    rows = []
    for item in channel_metrics:
        rows.append(
            f"- {item['channel']}：注册转化率 {format_percent(item['signup_rate'])}，"
            f"付费转化率 {format_percent(item['payment_rate'])}，"
            f"注册到付费转化率 {format_percent(item['signup_to_payment_rate'])}"
        )

    detail_text = "\n".join(rows)

    same_best_channel = (
        best_signup["channel"] == best_payment["channel"]
        == best_signup_to_payment["channel"]
    )

    if same_best_channel:
        conclusion = (
            f"整体来看，**{best_payment['channel']}** 是当前表现最好的渠道，"
            f"它在注册转化率、付费转化率和注册到付费转化率三个指标上均排名第一。"
        )
    else:
        conclusion = (
            f"不同渠道在不同阶段表现不同：注册转化率最高的是 **{best_signup['channel']}**，"
            f"付费转化率最高的是 **{best_payment['channel']}**，"
            f"注册到付费转化率最高的是 **{best_signup_to_payment['channel']}**。"
        )

    return f"""已完成渠道转化率分析。

{conclusion}

核心指标如下：

- 注册转化率最高渠道：**{best_signup['channel']}**，{format_percent(best_signup['signup_rate'])}
- 付费转化率最高渠道：**{best_payment['channel']}**，{format_percent(best_payment['payment_rate'])}
- 注册到付费转化率最高渠道：**{best_signup_to_payment['channel']}**，{format_percent(best_signup_to_payment['signup_to_payment_rate'])}

各渠道明细：

{detail_text}

初步建议：

1. 优先复盘高转化渠道的用户来源、内容策略和转化路径。
2. 对低转化渠道进一步分析落地页、用户质量和付费链路。
3. 后续可以加入投放成本，进一步计算 ROI。
"""


def format_report_generation_response(tool_result: dict) -> str:

    """
    格式化报告生成结果。
    """
    output_path = tool_result.get("output_path")
    summary = tool_result.get("summary", {})

    best_payment = summary.get("best_payment_channel", {})

    if best_payment:
        return f"""渠道分析报告已生成。

报告路径：

{output_path}

核心结论：

当前付费转化率最高的渠道是 **{best_payment.get('channel')}**，付费转化率为 **{format_percent(best_payment.get('payment_rate'))}**。

你可以打开该 Markdown 文件查看完整分析报告。
"""

    return f"""渠道分析报告已生成。

报告路径：

{output_path}
"""

def format_read_stock_price_response(tool_result: dict) -> str:
    """
    格式化股票价格数据读取结果。
    """
    return f"""已成功读取股票/策略价格数据。

数据共有 **{tool_result.get("rows")}** 行。

数据区间：

- 开始日期：{tool_result.get("start_date")}
- 结束日期：{tool_result.get("end_date")}
- 起始价格：{tool_result.get("start_close")}
- 结束价格：{tool_result.get("end_close")}

字段包括：

{", ".join(tool_result.get("columns", []))}
"""


def format_stock_metrics_response(tool_result: dict) -> str:
    """
    格式化金融指标分析结果。
    """
    total_return = tool_result.get("total_return")
    annualized_volatility = tool_result.get("annualized_volatility")
    max_drawdown = tool_result.get("max_drawdown")
    sharpe_ratio = tool_result.get("sharpe_ratio")

    if total_return > 0:
        return_comment = "该标的在统计区间内取得正收益。"
    elif total_return < 0:
        return_comment = "该标的在统计区间内出现负收益。"
    else:
        return_comment = "该标的在统计区间内收益基本持平。"

    if max_drawdown < -0.1:
        risk_comment = "最大回撤相对较高，需要重点关注下行风险。"
    else:
        risk_comment = "最大回撤相对可控，但仍需要结合更长周期数据判断风险。"

    if sharpe_ratio is None:
        sharpe_text = "无法计算"
    else:
        sharpe_text = f"{sharpe_ratio:.4f}"

    return f"""已完成风险收益指标分析。

数据区间：

- 开始日期：{tool_result.get("start_date")}
- 结束日期：{tool_result.get("end_date")}
- 起始价格：{tool_result.get("start_close")}
- 结束价格：{tool_result.get("end_close")}

核心指标：

- 区间收益率：**{format_percent(total_return)}**
- 年化波动率：**{format_percent(annualized_volatility)}**
- 最大回撤：**{format_percent(max_drawdown)}**
- 夏普比率：**{sharpe_text}**

最佳与最差单日：

- 最佳单日：{tool_result["best_day"]["date"]}，日收益率 {format_percent(tool_result["best_day"]["daily_return"])}
- 最差单日：{tool_result["worst_day"]["date"]}，日收益率 {format_percent(tool_result["worst_day"]["daily_return"])}

初步判断：

{return_comment}

{risk_comment}

注意：当前样本数据较短，年化波动率和夏普比率可能存在较大偏差，真实业务中应使用更长周期数据并结合基准指数进一步评估。
"""


def format_stock_report_generation_response(tool_result: dict) -> str:
    """
    格式化金融指标报告生成结果。
    """
    output_path = tool_result.get("output_path")
    summary = tool_result.get("summary", {})

    total_return = summary.get("total_return")
    max_drawdown = summary.get("max_drawdown")
    sharpe_ratio = summary.get("sharpe_ratio")

    sharpe_text = "无法计算" if sharpe_ratio is None else f"{sharpe_ratio:.4f}"

    return f"""金融指标报告已生成。

报告路径：

{output_path}

核心摘要：

- 区间收益率：**{format_percent(total_return)}**
- 最大回撤：**{format_percent(max_drawdown)}**
- 夏普比率：**{sharpe_text}**

你可以打开该 Markdown 文件查看完整风险收益分析报告。
"""

def format_backtest_response(tool_result: dict) -> str:
    """
    格式化均线策略回测结果。
    """
    sharpe_ratio = tool_result.get("sharpe_ratio")
    sharpe_text = "无法计算" if sharpe_ratio is None else f"{sharpe_ratio:.4f}"

    strategy_return = tool_result.get("strategy_total_return")
    benchmark_return = tool_result.get("benchmark_total_return")
    excess_return = tool_result.get("excess_return")

    if strategy_return > benchmark_return:
        performance_comment = "该策略在当前样本区间内跑赢买入持有基准。"
    else:
        performance_comment = "该策略在当前样本区间内跑输买入持有基准，可能是因为均线信号存在滞后或样本处于较强上涨趋势。"

    return f"""已完成均线策略回测。

策略名称：**{tool_result.get("strategy_name")}**

回测区间：

- 开始日期：{tool_result.get("start_date")}
- 结束日期：{tool_result.get("end_date")}
- 短期均线窗口：{tool_result.get("short_window")}
- 长期均线窗口：{tool_result.get("long_window")}

核心指标：

- 策略区间收益率：**{format_percent(strategy_return)}**
- 买入持有收益率：**{format_percent(benchmark_return)}**
- 超额收益：**{format_percent(excess_return)}**
- 年化波动率：**{format_percent(tool_result.get("annualized_volatility"))}**
- 最大回撤：**{format_percent(tool_result.get("max_drawdown"))}**
- 夏普比率：**{sharpe_text}**
- 交易次数：**{tool_result.get("trade_count")}**
- 持仓比例：**{format_percent(tool_result.get("holding_ratio"))}**
- 最新信号：**{tool_result.get("latest_signal")}**

初步判断：

{performance_comment}

注意：当前回测未考虑交易成本、滑点和冲击成本，且样本周期较短，结果仅用于验证策略流程，不构成投资建议。
"""

def format_backtest_report_generation_response(tool_result: dict) -> str:
    """
    格式化均线策略回测报告生成结果。
    """
    output_path = tool_result.get("output_path")
    summary = tool_result.get("summary", {})

    sharpe_ratio = summary.get("sharpe_ratio")
    sharpe_text = "无法计算" if sharpe_ratio is None else f"{sharpe_ratio:.4f}"

    return f"""均线策略回测报告已生成。

报告路径：

{output_path}

核心摘要：

- 策略名称：**{summary.get("strategy_name")}**
- 策略收益率：**{format_percent(summary.get("strategy_total_return"))}**
- 买入持有收益率：**{format_percent(summary.get("benchmark_total_return"))}**
- 超额收益：**{format_percent(summary.get("excess_return"))}**
- 最大回撤：**{format_percent(summary.get("max_drawdown"))}**
- 夏普比率：**{sharpe_text}**
- 最新信号：**{summary.get("latest_signal")}**

你可以打开该 Markdown 文件查看完整回测报告。
"""

def format_parameter_scan_response(tool_result: dict) -> str:
    """
    格式化均线参数扫描结果。
    """
    best_result = tool_result.get("best_result", {})
    all_results = tool_result.get("all_results", [])
    sort_by = tool_result.get("sort_by")

    sort_by_name_mapping = {
        "sharpe_ratio": "夏普比率",
        "strategy_total_return": "策略收益率",
        "excess_return": "超额收益",
        "max_drawdown": "最大回撤"
    }

    sort_by_name = sort_by_name_mapping.get(sort_by, sort_by)

    best_sharpe = best_result.get("sharpe_ratio")
    best_sharpe_text = "无法计算" if best_sharpe is None else f"{best_sharpe:.4f}"

    top_items = all_results[:3]
    top_lines = []

    for idx, item in enumerate(top_items, start=1):
        sharpe = item.get("sharpe_ratio")
        sharpe_text = "无法计算" if sharpe is None else f"{sharpe:.4f}"

        top_lines.append(
            f"{idx}. **{item['strategy_name']}**："
            f"策略收益率 {format_percent(item['strategy_total_return'])}，"
            f"超额收益 {format_percent(item['excess_return'])}，"
            f"最大回撤 {format_percent(item['max_drawdown'])}，"
            f"夏普比率 {sharpe_text}"
        )

    top_text = "\n".join(top_lines)

    if best_result.get("strategy_total_return", 0) > best_result.get("benchmark_total_return", 0):
        performance_comment = "最佳参数组合在当前样本中跑赢买入持有基准。"
    else:
        performance_comment = "最佳参数组合在当前样本中仍未跑赢买入持有基准，说明当前样本下买入持有表现更强，或均线策略存在滞后。"

    return f"""已完成均线策略参数扫描。

本次共完成 **{tool_result.get("total_combinations")}** 组参数组合回测，排序指标为：**{sort_by_name}**。

最佳参数组合：

- 策略名称：**{best_result.get("strategy_name")}**
- 短期均线窗口：{best_result.get("short_window")}
- 长期均线窗口：{best_result.get("long_window")}
- 策略收益率：**{format_percent(best_result.get("strategy_total_return"))}**
- 买入持有收益率：**{format_percent(best_result.get("benchmark_total_return"))}**
- 超额收益：**{format_percent(best_result.get("excess_return"))}**
- 最大回撤：**{format_percent(best_result.get("max_drawdown"))}**
- 夏普比率：**{best_sharpe_text}**
- 最新信号：**{best_result.get("latest_signal")}**

Top 3 参数组合：

{top_text}

初步判断：

{performance_comment}

注意：参数扫描容易产生样本内过拟合，当前结果只能说明这些参数在当前样本区间内表现较好，不能直接代表未来有效。真实策略研究中需要样本外测试、滚动窗口验证和交易成本约束。
"""

def format_parameter_scan_report_generation_response(tool_result: dict) -> str:

    """
    格式化均线参数扫描报告生成结果。
    """
    output_path = tool_result.get("output_path")
    summary = tool_result.get("summary", {})
    best_result = summary.get("best_result", {})

    sharpe_ratio = best_result.get("sharpe_ratio")
    sharpe_text = "无法计算" if sharpe_ratio is None else f"{sharpe_ratio:.4f}"

    return f"""均线策略参数扫描报告已生成。

报告路径：

{output_path}

核心摘要：

- 排序指标：**{summary.get("sort_by")}**
- 参数组合数量：**{summary.get("total_combinations")}**
- 最佳策略：**{best_result.get("strategy_name")}**
- 策略收益率：**{format_percent(best_result.get("strategy_total_return"))}**
- 买入持有收益率：**{format_percent(best_result.get("benchmark_total_return"))}**
- 超额收益：**{format_percent(best_result.get("excess_return"))}**
- 最大回撤：**{format_percent(best_result.get("max_drawdown"))}**
- 夏普比率：**{sharpe_text}**

你可以打开该 Markdown 文件查看完整参数扫描对比报告。
"""

def format_strategy_research_summary_response(tool_result: dict) -> str:
    """
    格式化策略研究总结报告生成结果。
    """
    output_path = tool_result.get("output_path")
    summary = tool_result.get("summary", {})

    best_sharpe = summary.get("best_sharpe_ratio")
    best_sharpe_text = "无法计算" if best_sharpe is None else f"{best_sharpe:.4f}"

    return f"""策略研究总结报告已生成。

报告路径：

{output_path}

核心摘要：

- 标的买入持有收益率：**{format_percent(summary.get("asset_total_return"))}**
- 默认 MA3-MA5 策略收益率：**{format_percent(summary.get("default_strategy_return"))}**
- 默认策略超额收益：**{format_percent(summary.get("default_excess_return"))}**
- 最佳策略：**{summary.get("best_strategy_name")}**
- 最佳策略收益率：**{format_percent(summary.get("best_strategy_return"))}**
- 最佳策略超额收益：**{format_percent(summary.get("best_excess_return"))}**
- 最佳策略最大回撤：**{format_percent(summary.get("best_max_drawdown"))}**
- 最佳策略夏普比率：**{best_sharpe_text}**

综合建议：

{summary.get("final_suggestion")}

你可以打开该 Markdown 文件查看完整策略研究总结。
"""

def format_backtest_charts_response(tool_result: dict) -> str:
    """
    格式化回测图表生成结果。
    """
    return f"""回测图表已生成。

图表路径：

- 策略净值曲线：{tool_result.get("nav_chart_path")}
- 策略回撤曲线：{tool_result.get("drawdown_chart_path")}

策略参数：

- 短期均线窗口：{tool_result.get("short_window")}
- 长期均线窗口：{tool_result.get("long_window")}

你可以打开图片文件查看策略净值和回撤表现。
"""

def format_parameter_scan_chart_response(tool_result: dict) -> str:
    """
    格式化参数扫描图表生成结果。
    """
    return f"""参数扫描图表已生成。

图表路径：

{tool_result.get("chart_path")}

排序指标：

{tool_result.get("sort_by")}

本次图表包含参数组合数量：

{tool_result.get("total_combinations")}

你可以打开图片文件查看不同均线参数组合的表现对比。
"""