from pathlib import Path

import pytest

from rag_embedding_indexer import build_embedding_index
from rag_embedding_retriever import (
    cosine_similarity,
    retrieve_embedding_chunks,
)


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


def test_cosine_similarity_basic_cases():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)


def test_cosine_similarity_rejects_dimension_mismatch():
    with pytest.raises(ValueError, match="dimensions do not match"):
        cosine_similarity([1.0, 2.0], [1.0])


def test_retrieve_embedding_chunks_returns_ranked_chunks(tmp_path):
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

    chunks = retrieve_embedding_chunks(
        query="MA5-MA10 均线策略",
        top_k=2,
        index_path=index_path,
    )

    assert len(chunks) == 2
    assert chunks[0]["score"] >= chunks[1]["score"]
    assert chunks[0]["retrieval_mode"] == "embedding"
    assert chunks[0]["embedding_provider"] == "hash"
    assert "source" in chunks[0]
    assert "chunk_id" in chunks[0]
    assert "text" in chunks[0]


def test_retrieve_embedding_chunks_applies_min_score(tmp_path):
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

    chunks = retrieve_embedding_chunks(
        query="完全无关的问题",
        top_k=3,
        min_score=1.1,
        index_path=index_path,
    )

    assert chunks == []


def test_retrieve_embedding_chunks_missing_index_has_clear_error(tmp_path):
    missing_index_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError, match="RAG embedding index not found"):
        retrieve_embedding_chunks(
            query="MA 策略",
            index_path=missing_index_path,
        )
