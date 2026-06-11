from llm_router import route_llm_tool_call
from mock_llm_tool_selector import mock_select_tool


FILE_PATH = "data/stock_price_strategy.csv"


def test_mock_selector_selects_backtest_report_tool():
    llm_tool_call = mock_select_tool("生成 MA5-MA10 回测报告")

    assert llm_tool_call["tool_name"] == "generate_backtest_report"
    assert llm_tool_call["arguments"] == {"short_window": 5, "long_window": 10}

    result = route_llm_tool_call(
        llm_tool_call=llm_tool_call,
        file_path=FILE_PATH,
    )

    assert result["success"] is True


def test_mock_selector_returns_no_tool_for_chat():
    llm_tool_call = mock_select_tool("随便聊聊天")

    assert llm_tool_call.get("tool_name") is None
