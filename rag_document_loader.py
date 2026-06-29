from pathlib import Path
from typing import Optional

from config import DOCUMENT_DIR


SUPPORTED_DOCUMENT_EXTENSIONS = [".md", ".txt"]


def normalize_document_name(document: str | Path) -> str:
    """
    统一文档名，只保留文件名部分。

    这样无论传入的是：
    - risk_metrics_notes.md
    - documents/risk_metrics_notes.md
    - D:/xxx/documents/risk_metrics_notes.md

    都会归一化为：
    - risk_metrics_notes.md
    """
    return Path(str(document)).name


def load_text_file(file_path: str | Path) -> str:
    """
    读取单个文本文件。

    当前支持 Markdown 和 txt。
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文档不存在：{path}")

    return path.read_text(encoding="utf-8")


def list_document_files(
    document_dir: str | Path = DOCUMENT_DIR,
    source_filter: Optional[list[str]] = None,
) -> list[Path]:
    """
    列出 documents 目录下支持的文档文件。

    source_filter:
        可选的文档名过滤列表。传入后，只返回文件名在该列表中的文档。
        这是 Skill-aware RAG 前置过滤的关键：先缩小候选文档，再进入 chunk 构建和打分。
    """
    document_dir = Path(document_dir)

    if not document_dir.exists():
        return []

    normalized_filter = None
    if source_filter is not None:
        normalized_filter = {
            normalize_document_name(source)
            for source in source_filter
            if source
        }

    files = []

    for path in document_dir.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_DOCUMENT_EXTENSIONS:
            continue

        if normalized_filter is not None and path.name not in normalized_filter:
            continue

        files.append(path)

    return sorted(files)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """
    将长文本切分成多个 chunk。

    chunk_size：每个 chunk 的最大字符数
    overlap：相邻 chunk 的重叠字符数，帮助保留上下文
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if overlap < 0:
        raise ValueError("overlap 不能为负数")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def build_document_chunks(
    document_dir: str | Path = DOCUMENT_DIR,
    chunk_size: int = 500,
    overlap: int = 80,
    source_filter: Optional[list[str]] = None,
) -> list[dict]:
    """
    读取 documents 目录下的文档，并切分成 chunk。

    如果 source_filter 不为空，则只加载指定文档。
    这比“先加载所有文档，再过滤 chunk”更靠前，因此更接近真正的 Skill-aware retrieval acceleration。

    返回结构示例：
    {
        "chunk_id": "ma_strategy_notes.md::chunk_0",
        "source": "documents/ma_strategy_notes.md",
        "chunk_index": 0,
        "text": "..."
    }
    """
    document_files = list_document_files(
        document_dir=document_dir,
        source_filter=source_filter,
    )

    all_chunks = []

    for file_path in document_files:
        text = load_text_file(file_path)
        chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{file_path.name}::chunk_{index}",
                "source": str(file_path),
                "chunk_index": index,
                "text": chunk,
            })

    return all_chunks
