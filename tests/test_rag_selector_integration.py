import pytest

pytest.importorskip("openai")

from llm_tool_selector import select_tool


FILE_PATH = "data/stock_price_strategy.csv"


def test_selector_can_attach_rag_chunks_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = select_tool(
        user_input="如果用户问最大回撤，sort_by 应该是什么？",
        file_path=FILE_PATH,
        mode="real",
        use_rag=True,
        rag_top_k=3,
    )

    assert result["selector_mode"] == "real"
    assert result["use_rag"] is True
    assert len(result["retrieved_chunks"]) > 0
    assert result["tool_name"] is None
