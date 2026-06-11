import json

import pytest

pytest.importorskip("openai")

from real_llm_tool_selector import (
    build_tool_selection_prompt,
    parse_llm_tool_selection_response,
    real_select_tool,
)


CURRENT_FILE_INFO = {
    "file_path": "data/stock_price_strategy.csv",
    "file_type": "stock_price",
    "file_type_name": "股票价格数据",
    "columns": ["date", "close"],
}


def test_build_tool_selection_prompt():
    prompt = build_tool_selection_prompt(
        user_input="帮我生成 MA5-MA10 回测报告",
        current_file_info=CURRENT_FILE_INFO,
    )

    assert "MA5-MA10" in prompt
    assert "generate_backtest_report" in prompt
    assert "stock_price_strategy.csv" in prompt


def test_parse_llm_tool_selection_response_valid_json():
    mock_response = json.dumps(
        {
            "tool_name": "generate_backtest_report",
            "arguments": {"short_window": 5, "long_window": 10},
            "reason": "用户想生成 MA5-MA10 均线策略回测报告。",
        },
        ensure_ascii=False,
    )

    parsed = parse_llm_tool_selection_response(mock_response)

    assert parsed["tool_name"] == "generate_backtest_report"
    assert parsed["arguments"] == {"short_window": 5, "long_window": 10}


def test_parse_llm_tool_selection_response_invalid_json():
    parsed = parse_llm_tool_selection_response("我觉得应该调用 generate_backtest_report")

    assert parsed["tool_name"] is None
    assert parsed["arguments"] == {}


def test_real_select_tool_without_api_key_fails_gracefully(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = real_select_tool(
        user_input="帮我生成 MA5-MA10 回测报告",
        current_file_info=CURRENT_FILE_INFO,
    )

    assert result["tool_name"] is None
    assert "DEEPSEEK_API_KEY" in result["reason"]
