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