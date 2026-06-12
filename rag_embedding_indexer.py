"""
Build a minimal local embedding index for RAG documents.

This module is the first implementation step after the embedding RAG design.
It intentionally uses a deterministic local hash-based embedding provider, so
it does not require API keys, network access, model downloads, or vector DBs.

The generated index is meant to be a runtime artifact and should not be
committed to Git by default.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import config
from rag_document_loader import build_document_chunks


INDEX_SCHEMA_VERSION = 1
SUPPORTED_EMBEDDING_PROVIDERS = {"hash"}
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


def tokenize_for_hash_embedding(text: str) -> list[str]:
    """
    Tokenize text for the local hash-based embedding prototype.

    English letters and numbers are grouped into word-like tokens. Chinese
    characters are kept as individual tokens so short Chinese questions and
    document chunks can still produce stable non-empty vectors.
    """
    normalized_text = text.lower().strip()

    if not normalized_text:
        return []

    tokens = _TOKEN_PATTERN.findall(normalized_text)

    if tokens:
        return tokens

    return [char for char in normalized_text if not char.isspace()]


def create_hash_embedding(
    text: str,
    dim: int = config.DEFAULT_EMBEDDING_DIM,
) -> list[float]:
    """
    Create a deterministic local embedding vector.

    This is not a semantic embedding model. It is a stable, dependency-free
    placeholder that gives the project a testable index format before a real
    embedding provider is introduced.
    """
    if dim <= 0:
        raise ValueError("embedding dim must be greater than 0")

    vector = [0.0 for _ in range(dim)]
    tokens = tokenize_for_hash_embedding(text)

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], byteorder="big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [round(value / norm, 8) for value in vector]


def build_embedding_index(
    document_dir: str | Path = config.DOCUMENT_DIR,
    index_path: str | Path = config.RAG_INDEX_FILE,
    chunk_size: int = 500,
    overlap: int = 80,
    embedding_provider: str = config.DEFAULT_EMBEDDING_PROVIDER,
    embedding_dim: int = config.DEFAULT_EMBEDDING_DIM,
) -> dict[str, Any]:
    """
    Build and save a local embedding index from documents/ chunks.

    The first supported provider is "hash". Later lessons can add real
    embedding providers without changing the index schema consumers.
    """
    if embedding_provider not in SUPPORTED_EMBEDDING_PROVIDERS:
        raise ValueError(
            f"Unsupported embedding provider: {embedding_provider}. "
            f"Supported providers: {sorted(SUPPORTED_EMBEDDING_PROVIDERS)}"
        )

    chunks = build_document_chunks(
        document_dir=document_dir,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    indexed_chunks = []

    for chunk in chunks:
        embedding = create_hash_embedding(
            text=chunk["text"],
            dim=embedding_dim,
        )
        indexed_chunks.append({
            **chunk,
            "embedding": embedding,
        })

    index = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "embedding_provider": embedding_provider,
        "embedding_dim": embedding_dim,
        "document_dir": str(Path(document_dir)),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunk_count": len(indexed_chunks),
        "chunks": indexed_chunks,
    }

    save_embedding_index(index=index, index_path=index_path)

    return index


def save_embedding_index(index: dict[str, Any], index_path: str | Path) -> Path:
    """
    Save an embedding index as UTF-8 JSON.
    """
    path = Path(index_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def load_embedding_index(
    index_path: str | Path = config.RAG_INDEX_FILE,
) -> dict[str, Any]:
    """
    Load a saved embedding index JSON file.
    """
    path = Path(index_path)

    if not path.exists():
        raise FileNotFoundError(f"RAG embedding index not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    built_index = build_embedding_index()
    print(
        "Built RAG embedding index: "
        f"{built_index['chunk_count']} chunks -> {config.RAG_INDEX_FILE}"
    )
