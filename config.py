from pathlib import Path


DATA_DIR = Path("data")
DOCUMENT_DIR = Path("documents")
OUTPUT_DIR = DATA_DIR / "output"
REPORT_DIR = OUTPUT_DIR / "reports"
CHART_DIR = OUTPUT_DIR / "charts"
LOG_DIR = DATA_DIR / "logs"
RAG_INDEX_DIR = DATA_DIR / "rag_index"
RAG_INDEX_FILE = RAG_INDEX_DIR / "rag_index.json"

# Default retrieval strategy used by the RAG retrieval router.
# Keep this in config.py so upper-level modules do not hardcode
# implementation details such as keyword / embedding / hybrid.
DEFAULT_RETRIEVAL_MODE = "keyword"

# Default embedding settings for the first local embedding index prototype.
# The current provider is deterministic and local, so it does not call any API.
DEFAULT_EMBEDDING_PROVIDER = "hash"
DEFAULT_EMBEDDING_DIM = 64


def ensure_output_dirs() -> None:
    """
    确保输出目录存在。
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)