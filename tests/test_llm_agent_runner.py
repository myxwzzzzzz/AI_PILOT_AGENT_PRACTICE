import pytest

pytest.importorskip("openai")

from llm_agent_runner import looks_like_knowledge_question, run_llm_agent_task


FILE_PATH = "data/stock_price_strategy.csv"


def test_looks_like_knowledge_question():
    assert looks_like_knowledge_question("最大回撤是什么意思？") is True
    assert looks_like_knowledge_question("生成 MA5-MA10 回测报告") is False


def test_run_llm_agent_task_with_mock_selector():
    result = run_llm_agent_task(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        selector_mode="mock",
    )

    assert result["success"] is True
    assert result["selected_tool"] == "generate_backtest_report"
    assert result["trace"]["selector_mode"] == "mock"


def test_run_llm_agent_task_falls_back_to_mock_for_bad_selector_mode():
    result = run_llm_agent_task(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        selector_mode="bad_mode",
    )

    assert result["success"] is True
    assert result["trace"]["fallback_used"] is True
    assert any("fallback_selector=mock" in step for step in result["trace"]["fallback_steps"])
