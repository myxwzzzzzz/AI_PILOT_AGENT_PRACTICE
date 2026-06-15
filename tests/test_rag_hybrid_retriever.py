from pathlib import Path

import pytest

from rag_embedding_indexer import build_embedding_index
from rag_hybrid_retriever import retrieve_hybrid_chunks


def create_test_documents(document_dir: Path) -> None:
    document_dir.mkdir(parents=True, exist_ok=True)
    (document_dir / "ma_notes.md").write_text(
        "MA5-MA10 均线策略用于观察短期均线和长期均线的交叉。"
        "趋势行情中，均线策略可能捕捉上涨或下跌趋势。",
        encoding="utf-8",
    )
    (document_dir / "risk_notes.md").write_text(
        "最大回撤用于衡量策略净值从高点到低点的最大下跌幅度。"
        "夏普比率用于衡量单位风险下的收益表现。",
        encoding="utf-8",
    )


def test_retrieve_hybrid_chunks_fuses_keyword_and_embedding_results(tmp_path, monkeypatch):
    document_dir = tmp_path / "documents"
    index_path = tmp_path / "rag_index.json"
    create_test_documents(document_dir)

    build_embedding_index(
        document_dir=document_dir,
        index_path=index_path,
        chunk_size=80,
        overlap=0,
        embedding_dim=32,
    )

    # Make keyword retrieval read the same temporary documents as the embedding
    # index so the test does not depend on the repository-level documents/ data.
    monkeypatch.setattr("rag_retriever.build_document_chunks", lambda: [
        {
            "source": str(document_dir / "ma_notes.md"),
            "chunk_id": "ma_notes.md::chunk_0",
            "chunk_index": 0,
            "text": "MA5-MA10 均线策略用于观察短期均线和长期均线的交叉。",
        },
        {
            "source": str(document_dir / "risk_notes.md"),
            "chunk_id": "risk_notes.md::chunk_0",
            "chunk_index": 0,
            "text": "最大回撤用于衡量策略净值从高点到低点的最大下跌幅度。",
        },
    ])

    chunks = retrieve_hybrid_chunks(
        query="MA5-MA10 均线策略",
        top_k=2,
        min_score=1,
        embedding_index_path=index_path,
    )

    assert len(chunks) > 0
    assert chunks[0]["retrieval_mode"] == "hybrid"
    assert "keyword_weight" in chunks[0]
    assert "embedding_weight" in chunks[0]
    assert "retrieval_sources" in chunks[0]
    assert any(
        "keyword" in chunk["retrieval_sources"]
        for chunk in chunks
    )
    assert any(
        "embedding" in chunk["retrieval_sources"]
        for chunk in chunks
    )


def test_retrieve_hybrid_chunks_falls_back_to_keyword_when_index_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("rag_retriever.build_document_chunks", lambda: [
        {
            "source": "documents/ma_notes.md",
            "chunk_id": "ma_notes.md::chunk_0",
            "chunk_index": 0,
            "text": "MA5-MA10 均线策略用于观察短期均线和长期均线的交叉。",
        },
    ])

    chunks = retrieve_hybrid_chunks(
        query="MA5-MA10 均线策略",
        top_k=2,
        min_score=1,
        embedding_index_path=tmp_path / "missing_index.json",
    )

    assert len(chunks) == 1
    assert chunks[0]["retrieval_mode"] == "hybrid"
    assert chunks[0]["retrieval_sources"] == ["keyword"]
    assert chunks[0]["embedding_status"] == "missing_index_fallback_keyword_only"


def test_retrieve_hybrid_chunks_rejects_invalid_weights():
    with pytest.raises(ValueError, match="weights must be non-negative"):
        retrieve_hybrid_chunks(
            query="测试",
            keyword_weight=-1,
            embedding_weight=1,
        )

    with pytest.raises(ValueError, match="at least one"):
        retrieve_hybrid_chunks(
            query="测试",
            keyword_weight=0,
            embedding_weight=0,
        )
