import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_tool_selector import select_tool


file_path = "data/stock_price_strategy.csv"

test_inputs = [
    "MA5-MA10 策略适合震荡行情吗？",
    "如果用户问最大回撤，sort_by 应该是什么？",
    "生成 MA5-MA10 回测报告",
]


for user_input in test_inputs:
    print("=" * 80)
    print("用户输入：", user_input)

    result = select_tool(
        user_input=user_input,
        file_path=file_path,
        mode="real",
        use_rag=True,
        rag_top_k=3,
    )

    print("Selector 输出：")
    print({
        "tool_name": result.get("tool_name"),
        "arguments": result.get("arguments"),
        "reason": result.get("reason"),
        "selector_mode": result.get("selector_mode"),
        "use_rag": result.get("use_rag"),
        "retrieved_chunk_count": len(result.get("retrieved_chunks", [])),
        "retrieved_chunk_ids": [
            chunk.get("chunk_id")
            for chunk in result.get("retrieved_chunks", [])
        ],
    })