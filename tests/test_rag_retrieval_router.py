import pytest

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
    with pytest.raises(ValueError, match="Unsupported retrieval mode"):
        retrieve_chunks(
            query="测试问题",
            mode="vector",
        )
