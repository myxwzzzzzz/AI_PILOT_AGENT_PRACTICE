import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_tool_schema import (
    build_all_llm_tool_schemas,
    get_llm_tool_schema_by_name,
)


print("全部 LLM Tool Schema 数量：")
schemas = build_all_llm_tool_schemas()
print(len(schemas))


print("\n查看 generate_backtest_report 的 Tool Schema：")
backtest_report_schema = get_llm_tool_schema_by_name("generate_backtest_report")
print(json.dumps(backtest_report_schema, ensure_ascii=False, indent=2))


print("\n查看 generate_parameter_scan_chart 的 Tool Schema：")
scan_chart_schema = get_llm_tool_schema_by_name("generate_parameter_scan_chart")
print(json.dumps(scan_chart_schema, ensure_ascii=False, indent=2))