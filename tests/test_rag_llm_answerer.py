import pytest

pytest.importorskip("openai")

from rag_qa import answer_with_retrieved_context
from rag_retriever import retrieve_relevant_chunks


def test_answer_with_retrieved_context_local_fallback():
    user_input = "MA5-MA10 策略适合震荡行情吗？"
    chunks = retrieve_relevant_chunks(query=user_input, top_k=3, min_score=1)

    result = answer_with_retrieved_context(
        user_input=user_input,
        retrieved_chunks=chunks,
        use_llm_answer=False,
    )

    assert result["success"] is True
    assert result["answer_type"] == "rag_qa"
    assert result["answer_source"] == "local_rule_fallback"
    assert "震荡" in result["answer"]
