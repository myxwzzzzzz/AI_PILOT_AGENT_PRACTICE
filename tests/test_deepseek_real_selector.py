import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_tool_selector import select_tool


file_path = "data/stock_price_strategy.csv"

test_inputs = [
    "生成 MA5-MA10 回测报告",
    "按收益率生成参数扫描图表",
    "随便聊聊天"
]

for user_input in test_inputs:
    print("=" * 80)
    print("用户输入：", user_input)

    result = select_tool(
        user_input=user_input,
        file_path=file_path,
        mode="real"
    )

    print("真实 LLM 选择结果：")
    print(result)