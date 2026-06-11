import pytest

pytest.importorskip("openai")

from llm_tool_selector import select_tool


FILE_PATH = "data/stock_price_strategy.csv"


def test_select_tool_mock_mode():
    result = select_tool(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        mode="mock",
    )

    assert result["tool_name"] == "generate_backtest_report"
    assert result["arguments"] == {"short_window": 5, "long_window": 10}
    assert result["selector_mode"] == "mock"
    assert result["current_file_info"]["file_type"] == "stock_price"


def test_select_tool_real_mode_without_api_key_fails_gracefully(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = select_tool(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        mode="real",
    )

    assert result["tool_name"] is None
    assert result["selector_mode"] == "real"
    assert "DEEPSEEK_API_KEY" in result["reason"]


def test_select_tool_unsupported_mode():
    result = select_tool(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        mode="bad_mode",
    )

    assert result["tool_name"] is None
    assert "不支持" in result["reason"]
