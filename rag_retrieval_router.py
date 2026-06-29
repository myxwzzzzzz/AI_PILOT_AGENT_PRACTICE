"""
RAG retrieval router.

This module provides a unified retrieval entrypoint.

Current supported retrieval mode:
1. keyword: local keyword-based retrieval from rag_retriever.py

Skill-aware retrieval:
When skill_name is provided, retrieval first narrows candidate documents to the
documents registered under that skill. If no skill document chunk is found, it
can fall back to global retrieval.

Lesson 80 used result filtering after global retrieval.
Lesson 81 upgrades keyword retrieval to pre-filter candidate documents before
chunk scoring, which is the first real step toward retrieval acceleration.
"""

from __future__ import annotations

from typing import Any, Optional

from rag_retriever import retrieve_relevant_chunks
from skill_aware_rag import (
    annotate_chunks_with_skill_scope,
    build_skill_source_filter,
    get_skill_document_names,
)


DEFAULT_RETRIEVAL_MODE = "keyword"


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
    source_filter: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Retrieve keyword chunks and normalize metadata."""

    chunks = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
        min_score=min_score,
        source_filter=source_filter,
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
        Optional matched Skill name. When provided, RAG first narrows retrieval
        to documents registered under that Skill.
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

        skill_document_names = build_skill_source_filter(skill_name)

        if skill_document_names:
            skill_chunks = _retrieve_keyword_chunks(
                query=query,
                top_k=top_k,
                min_score=min_score,
                source_filter=skill_document_names,
            )

            if skill_chunks:
                return annotate_chunks_with_skill_scope(
                    skill_chunks,
                    skill_name=skill_name,
                    skill_document_names=skill_document_names,
                    retrieval_scope="skill_documents_prefiltered",
                )

            if not fallback_to_global:
                return []

        if not fallback_to_global:
            return []

        global_fallback_chunks = _retrieve_keyword_chunks(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        return annotate_chunks_with_skill_scope(
            global_fallback_chunks,
            skill_name=skill_name,
            skill_document_names=get_skill_document_names(skill_name),
            retrieval_scope="global_fallback",
        )

    raise ValueError(
        f"Unsupported retrieval mode: {mode}. "
        "Currently supported modes: keyword"
    )
