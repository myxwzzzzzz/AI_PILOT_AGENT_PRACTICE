from pathlib import Path

from config import DOCUMENT_DIR


SUPPORTED_DOCUMENT_EXTENSIONS = [".md", ".txt"]


def load_text_file(file_path: str | Path) -> str:
    """
    读取单个文本文件。

    当前支持 Markdown 和 txt。
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文档不存在：{path}")

    return path.read_text(encoding="utf-8")


def list_document_files(document_dir: str | Path = DOCUMENT_DIR) -> list[Path]:
    """
    列出 documents 目录下支持的文档文件。
    """
    document_dir = Path(document_dir)

    if not document_dir.exists():
        return []

    files = []

    for path in document_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_DOCUMENT_EXTENSIONS:
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
) -> list[dict]:
    """
    读取 documents 目录下所有文档，并切分成 chunk。

    返回结构示例：
    {
        "chunk_id": "ma_strategy_notes.md::chunk_0",
        "source": "documents/ma_strategy_notes.md",
        "chunk_index": 0,
        "text": "..."
    }
    """
    document_files = list_document_files(document_dir)

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