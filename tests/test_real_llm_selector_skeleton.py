import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from real_llm_tool_selector import (
    build_tool_selection_prompt,
    parse_llm_tool_selection_response,
    real_select_tool,
)


user_input = "帮我生成 MA5-MA10 回测报告"

current_file_info = {
    "file_path": "data/stock_price_strategy.csv",
    "file_type": "stock_price",
    "file_type_name": "股票价格数据",
    "columns": ["date", "close"]
}


print("测试 1：生成 LLM Tool Selection Prompt")
prompt = build_tool_selection_prompt(
    user_input=user_input,
    current_file_info=current_file_info
)
print(prompt[:1200])
print("\nPrompt 总长度：", len(prompt))


print("\n测试 2：解析合法 LLM JSON 输出")
mock_response = json.dumps({
    "tool_name": "generate_backtest_report",
    "arguments": {
        "short_window": 5,
        "long_window": 10
    },
    "reason": "用户想生成 MA5-MA10 均线策略回测报告。"
}, ensure_ascii=False)

parsed = parse_llm_tool_selection_response(mock_response)
print(parsed)


print("\n测试 3：解析非法 LLM 输出")
bad_response = "我觉得应该调用 generate_backtest_report"
parsed = parse_llm_tool_selection_response(bad_response)
print(parsed)


print("\n测试 4：调用 real_select_tool 占位入口")
result = real_select_tool(
    user_input=user_input,
    current_file_info=current_file_info
)
print({
    "tool_name": result.get("tool_name"),
    "arguments": result.get("arguments"),
    "reason": result.get("reason"),
    "has_debug_prompt": "debug_prompt" in result
})