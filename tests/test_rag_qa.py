import pytest

pytest.importorskip("openai")

from llm_agent_runner import run_llm_agent_task
from response_formatter import format_response


FILE_PATH = "data/stock_price_strategy.csv"


def test_rag_qa_path_uses_local_fallback_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = run_llm_agent_task(
        user_input="MA5-MA10 策略适合震荡行情吗？",
        file_path=FILE_PATH,
        selector_mode="real",
        fallback_to_mock=True,
        fallback_to_rule=True,
        use_rag=True,
        rag_top_k=3,
    )

    formatted = format_response(result)

    assert result["success"] is True
    assert result["answer_type"] == "rag_qa"
    assert result["trace"]["router_type"] == "rag_qa"
    assert "MA5-MA10" in formatted or "均线" in formatted


def test_rag_mode_still_allows_tool_call(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = run_llm_agent_task(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        selector_mode="mock",
        fallback_to_mock=True,
        fallback_to_rule=True,
        use_rag=True,
        rag_top_k=3,
    )

    assert result["success"] is True
    assert result["selected_tool"] == "generate_backtest_report"
