import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_health_check import (
    check_deepseek_connection,
    format_llm_health_check_result,
)


result = check_deepseek_connection()
print(format_llm_health_check_result(result))