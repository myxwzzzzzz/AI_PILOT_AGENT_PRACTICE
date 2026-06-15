"""
RAG retrieval router.

This module provides a unified retrieval entrypoint.

Current supported retrieval modes:
1. keyword: local keyword-based retrieval from rag_retriever.py
2. embedding: local embedding-index retrieval from rag_embedding_retriever.py
3. hybrid: keyword + embedding fusion from rag_hybrid_retriever.py

Future retrieval modes:
1. vector_db

The goal is to keep rag_qa.py and llm_agent_runner.py independent from
specific retrieval implementation details.
"""

from typing import Any

import config
from rag_embedding_retriever import retrieve_embedding_chunks
from rag_hybrid_retriever import retrieve_hybrid_chunks
from rag_retriever import retrieve_relevant_chunks


def retrieve_chunks(
    query: str,
    top_k: int = 3,
    min_score: int = 1,
    mode: str | None = None,
) -> list[dict[str, Any]]:
    """
    Unified RAG retrieval entrypoint.

    Parameters
    ----------
    query:
        User question.
    top_k:
        Maximum number of chunks to return.
    min_score:
        Minimum score threshold for keyword retrieval.
    mode:
        Retrieval strategy. If omitted, config.DEFAULT_RETRIEVAL_MODE is used.
        Supported values: "keyword", "embedding", "hybrid".

    Returns
    -------
    list[dict]
        Retrieved document chunks.
    """
    retrieval_mode = mode or config.DEFAULT_RETRIEVAL_MODE

    if retrieval_mode == "keyword":
        return retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

    if retrieval_mode == "embedding":
        return retrieve_embedding_chunks(
            query=query,
            top_k=top_k,
            min_score=float(min_score),
        )

    if retrieval_mode == "hybrid":
        return retrieve_hybrid_chunks(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

    raise ValueError(
        f"Unsupported retrieval mode: {retrieval_mode}. "
        "Currently supported modes: keyword, embedding, hybrid"
    )