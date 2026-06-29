"""
Skill-aware RAG helpers.

This module connects the Skill abstraction to RAG retrieval.

Before this layer, RAG searched all documents in the same way.
With skill-aware RAG, a matched skill can narrow or prioritize the document
scope. For example:
- stock_strategy_research_skill -> ma_strategy_notes.md, risk_metrics_notes.md
- rag_qa_skill -> all RAG knowledge documents registered in that skill

The implementation is intentionally conservative:
- It never executes tools.
- It only filters/annotates retrieved document chunks.
- If a skill has no documents or no chunk matches the skill documents, callers
  can fall back to global retrieval.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from skill_registry import get_skill


def normalize_document_name(document: str | Path) -> str:
    """Return only the file name of a document path."""

    return Path(str(document)).name


def get_skill_document_names(skill_name: Optional[str]) -> list[str]:
    """Return normalized document names configured for a skill."""

    if not skill_name:
        return []

    skill = get_skill(skill_name)
    if not skill:
        return []

    document_names: list[str] = []
    seen = set()

    for document in skill.get("documents", []) or []:
        name = normalize_document_name(document)
        if name and name not in seen:
            document_names.append(name)
            seen.add(name)

    return document_names


def chunk_matches_skill_documents(
    chunk: dict[str, Any],
    skill_document_names: list[str],
) -> bool:
    """Check whether a retrieved chunk belongs to one of the skill documents."""

    if not skill_document_names:
        return False

    source_name = normalize_document_name(chunk.get("source", ""))
    return source_name in set(skill_document_names)


def annotate_chunks_with_skill_scope(
    chunks: list[dict[str, Any]],
    *,
    skill_name: Optional[str],
    skill_document_names: Optional[list[str]] = None,
    retrieval_scope: str,
) -> list[dict[str, Any]]:
    """Attach skill-aware RAG metadata to chunks without mutating input chunks."""

    document_names = skill_document_names
    if document_names is None:
        document_names = get_skill_document_names(skill_name)

    annotated: list[dict[str, Any]] = []

    for chunk in chunks:
        skill_document_match = chunk_matches_skill_documents(
            chunk=chunk,
            skill_document_names=document_names,
        )

        annotated.append(
            {
                **chunk,
                "skill_aware_rag": bool(skill_name),
                "rag_skill_name": skill_name,
                "rag_skill_documents": document_names,
                "rag_retrieval_scope": retrieval_scope,
                "skill_document_match": skill_document_match,
            }
        )

    return annotated


def filter_chunks_for_skill(
    chunks: list[dict[str, Any]],
    *,
    skill_name: Optional[str],
    top_k: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Filter retrieved chunks to documents registered by a skill."""

    document_names = get_skill_document_names(skill_name)

    if not skill_name or not document_names:
        return []

    matched_chunks = [
        chunk
        for chunk in chunks
        if chunk_matches_skill_documents(
            chunk=chunk,
            skill_document_names=document_names,
        )
    ]

    if top_k is not None:
        matched_chunks = matched_chunks[:top_k]

    return annotate_chunks_with_skill_scope(
        matched_chunks,
        skill_name=skill_name,
        skill_document_names=document_names,
        retrieval_scope="skill_documents",
    )


def build_skill_aware_retrieval_metadata(skill_name: Optional[str]) -> dict[str, Any]:
    """Build compact metadata for trace/debug use."""

    document_names = get_skill_document_names(skill_name)

    return {
        "skill_aware_rag": bool(skill_name),
        "rag_skill_name": skill_name,
        "rag_skill_documents": document_names,
        "has_skill_documents": bool(document_names),
    }
