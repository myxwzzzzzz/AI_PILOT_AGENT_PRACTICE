import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_tool_selector import select_tool


file_path = "data/stock_price_strategy.csv"
user_input = "生成 MA5-MA10 回测报告"


print("测试 1：mock selector")
result = select_tool(
    user_input=user_input,
    file_path=file_path,
    mode="mock"
)
print(result)


print("\n测试 2：real selector 占位入口")
result = select_tool(
    user_input=user_input,
    file_path=file_path,
    mode="real"
)
print({
    "tool_name": result.get("tool_name"),
    "arguments": result.get("arguments"),
    "reason": result.get("reason"),
    "selector_mode": result.get("selector_mode"),
    "has_debug_prompt": "debug_prompt" in result,
    "current_file_info": result.get("current_file_info"),
})


print("\n测试 3：非法 selector mode")
result = select_tool(
    user_input=user_input,
    file_path=file_path,
    mode="bad_mode"
)
print(result)