"""
RAG retrieval router.

This module provides a unified retrieval entrypoint.

Current supported retrieval mode:
1. keyword: local keyword-based retrieval from rag_retriever.py

Future retrieval modes:
1. embedding
2. vector_db
3. hybrid

The goal is to keep rag_qa.py and llm_agent_runner.py independent from
specific retrieval implementation details.
"""

from typing import Any

import config
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
        Currently only "keyword" is supported.

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

    raise ValueError(
        f"Unsupported retrieval mode: {retrieval_mode}. "
        "Currently supported modes: keyword"
    )