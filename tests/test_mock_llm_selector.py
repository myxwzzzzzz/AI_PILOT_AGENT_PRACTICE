import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from mock_llm_tool_selector import mock_select_tool
from llm_router import route_llm_tool_call


file_path = "data/stock_price_strategy.csv"

test_inputs = [
    "生成 MA5-MA10 回测报告",
    "生成 MA5-MA10 回测图表",
    "按收益率生成参数扫描图表",
    "按最大回撤生成参数扫描报告",
    "生成策略研究总结报告",
    "分析风险收益",
    "随便聊聊天"
]

for user_input in test_inputs:
    print("=" * 80)
    print("用户输入：", user_input)

    llm_tool_call = mock_select_tool(user_input)

    print("Mock LLM Tool Call：")
    print(llm_tool_call)

    if llm_tool_call.get("tool_name") is None:
        print("没有选择工具，跳过执行。")
        continue

    result = route_llm_tool_call(
        llm_tool_call=llm_tool_call,
        file_path=file_path
    )

    print("执行结果：")
    print(result)