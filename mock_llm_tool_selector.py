from parameter_parser import extract_ma_windows, extract_scan_sort_by


def mock_select_tool(user_input: str) -> dict:
    """
    模拟 LLM 根据用户自然语言选择工具并生成参数。

    注意：
    - 当前仍然是规则实现；
    - 但输出格式模仿真实 LLM Tool Calling；
    - 后续接真实大模型时，只需要替换这一层。
    """
    text = user_input.strip()

    # 1. 回测图表：要放在回测报告/普通回测前面
    if any(keyword in text for keyword in ["回测图表", "净值曲线", "回撤曲线", "策略图表"]):
        ma_params = extract_ma_windows(text)

        return {
            "tool_name": "generate_backtest_charts",
            "arguments": {
                "short_window": ma_params["short_window"],
                "long_window": ma_params["long_window"],
            },
            "reason": "用户想生成回测相关图表，因此选择 generate_backtest_charts。"
        }

    # 2. 回测报告
    if any(keyword in text for keyword in ["回测报告", "策略报告"]):
        ma_params = extract_ma_windows(text)

        return {
            "tool_name": "generate_backtest_report",
            "arguments": {
                "short_window": ma_params["short_window"],
                "long_window": ma_params["long_window"],
            },
            "reason": "用户想生成均线策略回测报告，因此选择 generate_backtest_report。"
        }

    # 3. 普通回测
    if any(keyword in text for keyword in ["回测", "均线策略"]):
        ma_params = extract_ma_windows(text)

        return {
            "tool_name": "run_moving_average_backtest",
            "arguments": {
                "short_window": ma_params["short_window"],
                "long_window": ma_params["long_window"],
            },
            "reason": "用户想运行均线策略回测，因此选择 run_moving_average_backtest。"
        }

    # 4. 参数扫描图表：要放在参数扫描报告/普通扫描前面
    if any(keyword in text for keyword in ["参数扫描图表", "扫描图表", "参数对比图"]):
        sort_params = extract_scan_sort_by(text)

        return {
            "tool_name": "generate_parameter_scan_chart",
            "arguments": {
                "sort_by": sort_params["sort_by"],
            },
            "reason": "用户想生成参数扫描图表，因此选择 generate_parameter_scan_chart。"
        }

    # 5. 参数扫描报告
    if any(keyword in text for keyword in ["参数扫描报告", "扫描报告"]):
        sort_params = extract_scan_sort_by(text)

        return {
            "tool_name": "generate_parameter_scan_report",
            "arguments": {
                "sort_by": sort_params["sort_by"],
            },
            "reason": "用户想生成参数扫描报告，因此选择 generate_parameter_scan_report。"
        }

    # 6. 普通参数扫描
    if any(keyword in text for keyword in ["参数扫描", "扫描均线参数", "优化均线"]):
        sort_params = extract_scan_sort_by(text)

        return {
            "tool_name": "optimize_moving_average_parameters",
            "arguments": {
                "sort_by": sort_params["sort_by"],
            },
            "reason": "用户想进行均线参数扫描，因此选择 optimize_moving_average_parameters。"
        }

    # 7. 策略研究总结
    if any(keyword in text for keyword in ["策略研究总结", "策略研究报告", "综合策略报告", "策略总结"]):
        sort_params = extract_scan_sort_by(text)

        return {
            "tool_name": "generate_strategy_research_summary",
            "arguments": {
                "sort_by": sort_params["sort_by"],
            },
            "reason": "用户想生成综合策略研究总结报告，因此选择 generate_strategy_research_summary。"
        }

    # 8. 金融指标报告
    if any(keyword in text for keyword in ["金融指标报告", "风险收益报告"]):
        return {
            "tool_name": "generate_stock_metrics_report",
            "arguments": {},
            "reason": "用户想生成金融指标报告，因此选择 generate_stock_metrics_report。"
        }

    # 9. 金融指标分析
    if any(keyword in text for keyword in ["风险收益", "金融指标", "最大回撤", "夏普"]):
        return {
            "tool_name": "calculate_stock_metrics",
            "arguments": {},
            "reason": "用户想分析金融风险收益指标，因此选择 calculate_stock_metrics。"
        }

    # 10. 渠道分析报告
    if any(keyword in text for keyword in ["渠道报告", "渠道分析报告"]):
        return {
            "tool_name": "generate_channel_analysis_report",
            "arguments": {},
            "reason": "用户想生成渠道分析报告，因此选择 generate_channel_analysis_report。"
        }

    # 11. 渠道转化分析
    if any(keyword in text for keyword in ["渠道转化", "转化率", "渠道分析"]):
        return {
            "tool_name": "analyze_channel_conversion",
            "arguments": {},
            "reason": "用户想分析渠道转化率，因此选择 analyze_channel_conversion。"
        }

    # 12. CSV 概览
    if any(keyword in text for keyword in ["数据概览", "统计信息", "缺失值"]):
        return {
            "tool_name": "summarize_csv",
            "arguments": {},
            "reason": "用户想查看数据统计概览，因此选择 summarize_csv。"
        }

    # 13. 读取文件
    if any(keyword in text for keyword in ["读取", "预览", "看一下文件"]):
        return {
            "tool_name": "read_csv_file",
            "arguments": {},
            "reason": "用户想读取文件预览，因此选择 read_csv_file。"
        }

    return {
        "tool_name": None,
        "arguments": {},
        "reason": "没有找到合适工具。"
    }