"""
Hybrid RAG retriever.

This module combines keyword retrieval and embedding retrieval results.

The goal is not to replace keyword retrieval immediately. Instead, hybrid mode
lets the project experiment with multi-signal retrieval while keeping the
existing keyword path as the stable default.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rag_embedding_retriever import retrieve_embedding_chunks
from rag_retriever import retrieve_relevant_chunks


DEFAULT_KEYWORD_WEIGHT = 0.5
DEFAULT_EMBEDDING_WEIGHT = 0.5


def _normalize_scores(
    chunks: list[dict[str, Any]],
    score_key: str = "score",
) -> dict[tuple[str, str], float]:
    """
    Normalize a list of scored chunks to the 0~1 range.

    Keyword scores and embedding cosine scores are not on the same scale. This
    helper normalizes each retrieval source independently before fusion.
    """
    if not chunks:
        return {}

    raw_scores: dict[tuple[str, str], float] = {}

    for chunk in chunks:
        chunk_key = _chunk_key(chunk)
        score = float(chunk.get(score_key, 0.0))
        raw_scores[chunk_key] = max(score, 0.0)

    max_score = max(raw_scores.values(), default=0.0)

    if max_score <= 0:
        return {chunk_key: 0.0 for chunk_key in raw_scores}

    return {
        chunk_key: score / max_score
        for chunk_key, score in raw_scores.items()
    }


def _chunk_key(chunk: dict[str, Any]) -> tuple[str, str]:
    """
    Build a stable key for deduplicating chunks returned by different retrievers.
    """
    return (
        str(chunk.get("source", "unknown")),
        str(chunk.get("chunk_id", "unknown")),
    )


def _validate_weights(keyword_weight: float, embedding_weight: float) -> None:
    """
    Validate hybrid fusion weights.
    """
    if keyword_weight < 0 or embedding_weight < 0:
        raise ValueError("hybrid retrieval weights must be non-negative")

    if keyword_weight + embedding_weight <= 0:
        raise ValueError("at least one hybrid retrieval weight must be positive")


def retrieve_hybrid_chunks(
    query: str,
    top_k: int = 3,
    min_score: int = 1,
    keyword_weight: float = DEFAULT_KEYWORD_WEIGHT,
    embedding_weight: float = DEFAULT_EMBEDDING_WEIGHT,
    embedding_index_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve chunks using keyword + embedding fusion.

    Parameters
    ----------
    query:
        User question.
    top_k:
        Maximum number of fused chunks to return.
    min_score:
        Minimum score threshold for keyword retrieval. Embedding retrieval uses
        a cosine threshold of 0.0 in this prototype.
    keyword_weight:
        Weight applied to normalized keyword scores.
    embedding_weight:
        Weight applied to normalized embedding scores.
    embedding_index_path:
        Optional custom embedding index path for tests or experiments.

    Returns
    -------
    list[dict]
        Fused, deduplicated, ranked chunks.
    """
    if top_k <= 0:
        return []

    _validate_weights(keyword_weight, embedding_weight)

    keyword_chunks = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
        min_score=min_score,
    )

    embedding_chunks: list[dict[str, Any]] = []
    embedding_status = "available"

    if embedding_weight > 0:
        try:
            embedding_chunks = retrieve_embedding_chunks(
                query=query,
                top_k=top_k,
                min_score=0.0,
                index_path=embedding_index_path,
            )
        except FileNotFoundError:
            # Hybrid retrieval should remain usable even before a local
            # embedding index has been built. In that case it degrades to the
            # stable keyword path and records the fallback status in metadata.
            embedding_status = "missing_index_fallback_keyword_only"
            embedding_chunks = []

    normalized_keyword_scores = _normalize_scores(keyword_chunks)
    normalized_embedding_scores = _normalize_scores(embedding_chunks)

    merged: dict[tuple[str, str], dict[str, Any]] = {}

    for chunk in keyword_chunks:
        chunk_key = _chunk_key(chunk)
        normalized_score = normalized_keyword_scores.get(chunk_key, 0.0)
        merged[chunk_key] = {
            "source": chunk.get("source", "unknown"),
            "chunk_id": chunk.get("chunk_id", "unknown"),
            "chunk_index": chunk.get("chunk_index"),
            "text": chunk.get("text", ""),
            "keyword_score": chunk.get("score", 0),
            "embedding_score": None,
            "retrieval_sources": ["keyword"],
            "retrieval_mode": "hybrid",
            "embedding_status": embedding_status,
        }
        merged[chunk_key]["score"] = keyword_weight * normalized_score

    for chunk in embedding_chunks:
        chunk_key = _chunk_key(chunk)
        normalized_score = normalized_embedding_scores.get(chunk_key, 0.0)

        if chunk_key not in merged:
            merged[chunk_key] = {
                "source": chunk.get("source", "unknown"),
                "chunk_id": chunk.get("chunk_id", "unknown"),
                "chunk_index": chunk.get("chunk_index"),
                "text": chunk.get("text", ""),
                "keyword_score": None,
                "embedding_score": chunk.get("score", 0.0),
                "retrieval_sources": ["embedding"],
                "retrieval_mode": "hybrid",
                "embedding_provider": chunk.get("embedding_provider"),
                "embedding_status": embedding_status,
                "score": 0.0,
            }
        else:
            merged[chunk_key]["embedding_score"] = chunk.get("score", 0.0)
            merged[chunk_key]["retrieval_sources"].append("embedding")
            merged[chunk_key]["embedding_provider"] = chunk.get("embedding_provider")

        merged[chunk_key]["score"] += embedding_weight * normalized_score

    fused_chunks = list(merged.values())

    for chunk in fused_chunks:
        chunk["score"] = round(float(chunk.get("score", 0.0)), 6)
        chunk["keyword_weight"] = keyword_weight
        chunk["embedding_weight"] = embedding_weight

    fused_chunks.sort(key=lambda item: item["score"], reverse=True)

    return fused_chunks[:top_k]


if __name__ == "__main__":
    results = retrieve_hybrid_chunks("MA5-MA10 策略适合震荡行情吗？")

    for result in results:
        print(
            f"[{result['score']:.4f}] "
            f"{result['source']}#{result['chunk_id']} "
            f"sources={result['retrieval_sources']}: "
            f"{result['text'][:80]}"
        )
