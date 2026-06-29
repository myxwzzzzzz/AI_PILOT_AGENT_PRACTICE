"""
RAG retrieval router.

This module provides a unified retrieval entrypoint.

Current supported retrieval mode:
1. keyword: local keyword-based retrieval from rag_retriever.py

Skill-aware retrieval:
When skill_name is provided, retrieval first over-samples global keyword results,
then prioritizes chunks whose source document is registered under that skill.
If no skill document chunk is found, it can fall back to global retrieval.

The goal is to keep rag_qa.py and llm_agent_runner.py independent from
specific retrieval implementation details.
"""

from __future__ import annotations

from typing import Any, Optional

from rag_retriever import retrieve_relevant_chunks
from skill_aware_rag import (
    annotate_chunks_with_skill_scope,
    filter_chunks_for_skill,
    get_skill_document_names,
)


DEFAULT_RETRIEVAL_MODE = "keyword"
SKILL_AWARE_OVERSAMPLE_FACTOR = 5


def _ensure_retrieval_mode(
    chunks: list[dict[str, Any]],
    mode: str,
) -> list[dict[str, Any]]:
    """Attach retrieval mode when lower-level retrievers do not provide it."""

    return [
        {
            **chunk,
            "retrieval_mode": chunk.get("retrieval_mode", mode),
        }
        for chunk in chunks
    ]


def _retrieve_keyword_chunks(
    query: str,
    top_k: int,
    min_score: int,
) -> list[dict[str, Any]]:
    """Retrieve keyword chunks and normalize metadata."""

    chunks = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
        min_score=min_score,
    )

    return _ensure_retrieval_mode(chunks, "keyword")


def retrieve_chunks(
    query: str,
    top_k: int = 3,
    min_score: int = 1,
    mode: str = DEFAULT_RETRIEVAL_MODE,
    skill_name: Optional[str] = None,
    fallback_to_global: bool = True,
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
        Retrieval strategy. Currently only "keyword" is supported.
    skill_name:
        Optional matched Skill name. When provided, RAG prioritizes documents
        registered under that Skill.
    fallback_to_global:
        If True, return global retrieval results when no skill-specific chunks
        are found.

    Returns
    -------
    list[dict]
        Retrieved document chunks.
    """
    if mode == "keyword":
        if not skill_name:
            return _retrieve_keyword_chunks(
                query=query,
                top_k=top_k,
                min_score=min_score,
            )

        candidate_top_k = max(
            top_k,
            top_k * SKILL_AWARE_OVERSAMPLE_FACTOR,
        )
        candidate_chunks = _retrieve_keyword_chunks(
            query=query,
            top_k=candidate_top_k,
            min_score=min_score,
        )

        skill_chunks = filter_chunks_for_skill(
            candidate_chunks,
            skill_name=skill_name,
            top_k=top_k,
        )

        if skill_chunks:
            return skill_chunks

        if not fallback_to_global:
            return []

        skill_document_names = get_skill_document_names(skill_name)
        global_fallback_chunks = candidate_chunks[:top_k]

        return annotate_chunks_with_skill_scope(
            global_fallback_chunks,
            skill_name=skill_name,
            skill_document_names=skill_document_names,
            retrieval_scope="global_fallback",
        )

    raise ValueError(
        f"Unsupported retrieval mode: {mode}. "
        "Currently supported modes: keyword"
    )
