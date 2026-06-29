import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag_retrieval_router import retrieve_chunks


def test_retrieve_chunks_keyword_mode():
    chunks = retrieve_chunks(
        query="MA5-MA10 策略适合震荡行情吗？",
        top_k=3,
        min_score=1,
        mode="keyword",
    )

    assert isinstance(chunks, list)
    assert len(chunks) > 0

    first_chunk = chunks[0]

    assert "source" in first_chunk
    assert "chunk_id" in first_chunk
    assert "text" in first_chunk
    assert "score" in first_chunk


def test_retrieve_chunks_unsupported_mode():
    try:
        retrieve_chunks(
            query="测试问题",
            mode="vector",
        )
    except ValueError as error:
        assert "Unsupported retrieval mode" in str(error)
    else:
        raise AssertionError("Expected ValueError for unsupported retrieval mode")


def test_retrieve_chunks_with_skill_name_prioritizes_skill_documents():
    chunks = retrieve_chunks(
        query="最大回撤是什么意思？",
        top_k=3,
        min_score=1,
        mode="keyword",
        skill_name="stock_metrics_skill",
    )

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(chunk.get("skill_aware_rag") is True for chunk in chunks)
    assert all(chunk.get("rag_skill_name") == "stock_metrics_skill" for chunk in chunks)
    assert chunks[0].get("rag_retrieval_scope") in {"skill_documents", "global_fallback"}


def test_retrieve_chunks_with_skill_name_can_disable_global_fallback():
    chunks = retrieve_chunks(
        query="一个故意很难匹配到本地知识库的随机问题xyz",
        top_k=3,
        min_score=999,
        mode="keyword",
        skill_name="stock_metrics_skill",
        fallback_to_global=False,
    )

    assert chunks == []
