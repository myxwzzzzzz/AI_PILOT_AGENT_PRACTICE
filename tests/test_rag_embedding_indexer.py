import math

import pytest

import config
from rag_embedding_indexer import (
    build_embedding_index,
    create_hash_embedding,
    load_embedding_index,
    tokenize_for_hash_embedding,
)


def test_tokenize_for_hash_embedding_supports_chinese_and_english():
    tokens = tokenize_for_hash_embedding("MA5-MA10 策略 drawdown")

    assert "ma5" in tokens
    assert "ma10" in tokens
    assert "策" in tokens
    assert "略" in tokens
    assert "drawdown" in tokens


def test_create_hash_embedding_is_deterministic():
    first = create_hash_embedding("最大回撤是什么意思？", dim=16)
    second = create_hash_embedding("最大回撤是什么意思？", dim=16)

    assert first == second
    assert len(first) == 16


def test_create_hash_embedding_is_l2_normalized_for_non_empty_text():
    embedding = create_hash_embedding("MA5-MA10 策略适合趋势行情", dim=32)
    norm = math.sqrt(sum(value * value for value in embedding))

    assert len(embedding) == 32
    assert norm == pytest.approx(1.0, abs=1e-6)


def test_create_hash_embedding_rejects_invalid_dim():
    with pytest.raises(ValueError):
        create_hash_embedding("text", dim=0)


def test_build_embedding_index_writes_json(tmp_path):
    document_dir = tmp_path / "documents"
    document_dir.mkdir()
    (document_dir / "notes.md").write_text(
        "# MA Strategy\n\nMA5-MA10 策略使用短期均线和长期均线交叉生成信号。\n"
        "最大回撤用于衡量策略历史最糟糕的下跌幅度。",
        encoding="utf-8",
    )

    index_path = tmp_path / "rag_index" / "rag_index.json"

    index = build_embedding_index(
        document_dir=document_dir,
        index_path=index_path,
        chunk_size=80,
        overlap=10,
        embedding_dim=16,
    )

    assert index_path.exists()
    assert index["schema_version"] == 1
    assert index["embedding_provider"] == config.DEFAULT_EMBEDDING_PROVIDER
    assert index["embedding_dim"] == 16
    assert index["chunk_count"] == len(index["chunks"])
    assert index["chunk_count"] > 0

    first_chunk = index["chunks"][0]
    assert "chunk_id" in first_chunk
    assert "source" in first_chunk
    assert "text" in first_chunk
    assert "embedding" in first_chunk
    assert len(first_chunk["embedding"]) == 16

    loaded_index = load_embedding_index(index_path)
    assert loaded_index["chunk_count"] == index["chunk_count"]


def test_build_embedding_index_rejects_unknown_provider(tmp_path):
    with pytest.raises(ValueError):
        build_embedding_index(
            document_dir=tmp_path,
            index_path=tmp_path / "rag_index.json",
            embedding_provider="unknown",
        )
