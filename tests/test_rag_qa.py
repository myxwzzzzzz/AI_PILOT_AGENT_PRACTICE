import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_agent_runner import run_llm_agent_task
from response_formatter import format_response


file_path = "data/stock_price_strategy.csv"

test_inputs = [
    "MA5-MA10 策略适合震荡行情吗？",
    "如果用户问最大回撤，sort_by 应该是什么？",
    "生成 MA5-MA10 回测报告",
]


for user_input in test_inputs:
    print("=" * 80)
    print("用户输入：", user_input)

    result = run_llm_agent_task(
        user_input=user_input,
        file_path=file_path,
        selector_mode="real",
        fallback_to_mock=True,
        fallback_to_rule=True,
        use_rag=True,
        rag_top_k=3,
    )

    print("原始结果：")
    print({
        "success": result.get("success"),
        "answer_type": result.get("answer_type"),
        "selected_tool": result.get("selected_tool"),
        "trace_router_type": result.get("trace", {}).get("router_type"),
    })

    print("\n格式化回复：")
    print(format_response(result))