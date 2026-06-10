import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_router import route_llm_tool_call


file_path = "data/stock_price_strategy.csv"


print("测试 1：模拟 LLM 调用 MA5-MA10 回测报告")
result = route_llm_tool_call(
    llm_tool_call={
        "tool_name": "generate_backtest_report",
        "arguments": {
            "short_window": 5,
            "long_window": 10
        }
    },
    file_path=file_path
)
print(result)


print("\n测试 2：模拟 LLM 调用按收益率排序的参数扫描图表")
result = route_llm_tool_call(
    llm_tool_call={
        "tool_name": "generate_parameter_scan_chart",
        "arguments": {
            "sort_by": "strategy_total_return"
        }
    },
    file_path=file_path
)
print(result)


print("\n测试 3：模拟 LLM 返回非法参数")
result = route_llm_tool_call(
    llm_tool_call={
        "tool_name": "generate_backtest_report",
        "arguments": {
            "short_window": 20,
            "long_window": 5
        }
    },
    file_path=file_path
)
print(result)


print("\n测试 4：模拟 LLM 选择未知工具")
result = route_llm_tool_call(
    llm_tool_call={
        "tool_name": "unknown_tool",
        "arguments": {}
    },
    file_path=file_path
)
print(result)