from llm_router import route_llm_tool_call


FILE_PATH = "data/stock_price_strategy.csv"


def test_route_llm_tool_call_backtest_report():
    result = route_llm_tool_call(
        llm_tool_call={
            "tool_name": "generate_backtest_report",
            "arguments": {"short_window": 5, "long_window": 10},
        },
        file_path=FILE_PATH,
    )

    assert result["success"] is True
    assert result["selected_tool"] == "generate_backtest_report"


def test_route_llm_tool_call_parameter_scan_chart():
    result = route_llm_tool_call(
        llm_tool_call={
            "tool_name": "generate_parameter_scan_chart",
            "arguments": {"sort_by": "strategy_total_return"},
        },
        file_path=FILE_PATH,
    )

    assert result["success"] is True
    assert result["selected_tool"] == "generate_parameter_scan_chart"


def test_route_llm_tool_call_rejects_invalid_arguments():
    result = route_llm_tool_call(
        llm_tool_call={
            "tool_name": "generate_backtest_report",
            "arguments": {"short_window": 20, "long_window": 5},
        },
        file_path=FILE_PATH,
    )

    assert result["success"] is False


def test_route_llm_tool_call_rejects_unknown_tool():
    result = route_llm_tool_call(
        llm_tool_call={"tool_name": "unknown_tool", "arguments": {}},
        file_path=FILE_PATH,
    )

    assert result["success"] is False
