from pathlib import Path


DATA_DIR = Path("data")
DOCUMENT_DIR = Path("documents")
OUTPUT_DIR = DATA_DIR / "output"
REPORT_DIR = OUTPUT_DIR / "reports"
CHART_DIR = OUTPUT_DIR / "charts"
LOG_DIR = DATA_DIR / "logs"


def ensure_output_dirs() -> None:
    """
    确保输出目录存在。
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)