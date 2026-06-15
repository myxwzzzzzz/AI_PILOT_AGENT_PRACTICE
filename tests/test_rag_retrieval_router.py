import pytest

import config
from rag_retrieval_router import retrieve_chunks


def test_retrieve_chunks_uses_config_default_mode():
    chunks = retrieve_chunks(
        query="MA5-MA10 策略适合震荡行情吗？",
        top_k=3,
        min_score=1,
    )

    assert config.DEFAULT_RETRIEVAL_MODE == "keyword"
    assert isinstance(chunks, list)
    assert len(chunks) > 0


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


def test_retrieve_chunks_embedding_mode(monkeypatch, tmp_path):
    from rag_embedding_indexer import build_embedding_index

    document_dir = tmp_path / "documents"
    index_path = tmp_path / "rag_index.json"
    document_dir.mkdir(parents=True, exist_ok=True)
    (document_dir / "ma_notes.md").write_text(
        "MA5-MA10 均线策略用于观察短期均线和长期均线的交叉。",
        encoding="utf-8",
    )

    build_embedding_index(
        document_dir=document_dir,
        index_path=index_path,
        chunk_size=80,
        overlap=0,
        embedding_dim=32,
    )
    monkeypatch.setattr(config, "RAG_INDEX_FILE", index_path)

    chunks = retrieve_chunks(
        query="MA5-MA10 均线策略",
        top_k=1,
        min_score=0,
        mode="embedding",
    )

    assert len(chunks) == 1
    assert chunks[0]["retrieval_mode"] == "embedding"
    assert chunks[0]["embedding_provider"] == "hash"


def test_retrieve_chunks_hybrid_mode(monkeypatch, tmp_path):
    from rag_embedding_indexer import build_embedding_index

    document_dir = tmp_path / "documents"
    index_path = tmp_path / "rag_index.json"
    document_dir.mkdir(parents=True, exist_ok=True)
    (document_dir / "ma_notes.md").write_text(
        "MA5-MA10 均线策略用于观察短期均线和长期均线的交叉。",
        encoding="utf-8",
    )

    build_embedding_index(
        document_dir=document_dir,
        index_path=index_path,
        chunk_size=80,
        overlap=0,
        embedding_dim=32,
    )

    monkeypatch.setattr(config, "RAG_INDEX_FILE", index_path)
    monkeypatch.setattr("rag_retriever.build_document_chunks", lambda: [
        {
            "source": str(document_dir / "ma_notes.md"),
            "chunk_id": "ma_notes.md::chunk_0",
            "chunk_index": 0,
            "text": "MA5-MA10 均线策略用于观察短期均线和长期均线的交叉。",
        },
    ])

    chunks = retrieve_chunks(
        query="MA5-MA10 均线策略",
        top_k=2,
        min_score=1,
        mode="hybrid",
    )

    assert len(chunks) > 0
    assert chunks[0]["retrieval_mode"] == "hybrid"
    assert "retrieval_sources" in chunks[0]


def test_retrieve_chunks_unsupported_mode():
    with pytest.raises(ValueError, match="Unsupported retrieval mode"):
        retrieve_chunks(
            query="测试问题",
            mode="vector",
        )
