"""
Embedding-based RAG retriever.

This module reads the local embedding index built by rag_embedding_indexer.py
and retrieves the most similar document chunks for a user query.

The first implementation uses the same deterministic hash-based embedding
provider as the indexer. It is intentionally local and dependency-free, so it
can be tested without API keys, network access, or vector databases.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import config
from rag_embedding_indexer import (
    SUPPORTED_EMBEDDING_PROVIDERS,
    create_hash_embedding,
    load_embedding_index,
)


SUPPORTED_RETRIEVAL_PROVIDERS = SUPPORTED_EMBEDDING_PROVIDERS


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """
    Compute cosine similarity for two numeric vectors.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding vector dimensions do not match: "
            f"{len(vector_a)} != {len(vector_b)}"
        )

    if not vector_a:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def create_query_embedding(
    query: str,
    embedding_provider: str,
    embedding_dim: int,
) -> list[float]:
    """
    Create a query embedding using the same provider as the saved index.
    """
    if embedding_provider == "hash":
        return create_hash_embedding(text=query, dim=embedding_dim)

    raise ValueError(
        f"Unsupported embedding provider: {embedding_provider}. "
        f"Supported providers: {sorted(SUPPORTED_RETRIEVAL_PROVIDERS)}"
    )


def retrieve_embedding_chunks(
    query: str,
    top_k: int = 3,
    min_score: float = 0.0,
    index_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve top_k chunks from a local embedding index.

    Parameters
    ----------
    query:
        User question.
    top_k:
        Maximum number of chunks to return.
    min_score:
        Minimum cosine similarity threshold.
    index_path:
        Optional custom path for tests or experiments. If omitted,
        config.RAG_INDEX_FILE is used.
    """
    if top_k <= 0:
        return []

    effective_index_path = index_path or config.RAG_INDEX_FILE
    index = load_embedding_index(effective_index_path)

    embedding_provider = index.get(
        "embedding_provider",
        config.DEFAULT_EMBEDDING_PROVIDER,
    )
    embedding_dim = int(index.get("embedding_dim", config.DEFAULT_EMBEDDING_DIM))

    if embedding_provider not in SUPPORTED_RETRIEVAL_PROVIDERS:
        raise ValueError(
            f"Unsupported embedding provider: {embedding_provider}. "
            f"Supported providers: {sorted(SUPPORTED_RETRIEVAL_PROVIDERS)}"
        )

    query_embedding = create_query_embedding(
        query=query,
        embedding_provider=embedding_provider,
        embedding_dim=embedding_dim,
    )

    scored_chunks: list[dict[str, Any]] = []

    for chunk in index.get("chunks", []):
        chunk_embedding = chunk.get("embedding")

        if not isinstance(chunk_embedding, list):
            continue

        score = cosine_similarity(query_embedding, chunk_embedding)

        if score < min_score:
            continue

        scored_chunks.append({
            "source": chunk.get("source", "unknown"),
            "chunk_id": chunk.get("chunk_id", "unknown"),
            "text": chunk.get("text", ""),
            "score": round(score, 6),
            "retrieval_mode": "embedding",
            "embedding_provider": embedding_provider,
        })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    return scored_chunks[:top_k]


if __name__ == "__main__":
    results = retrieve_embedding_chunks("MA5-MA10 策略适合震荡行情吗？")

    for result in results:
        print(
            f"[{result['score']:.4f}] "
            f"{result['source']}#{result['chunk_id']}: "
            f"{result['text'][:80]}"
        )
