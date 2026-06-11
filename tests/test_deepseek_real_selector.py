import os

import pytest

pytest.importorskip("openai")

from llm_tool_selector import select_tool


pytestmark = pytest.mark.integration

FILE_PATH = "data/stock_price_strategy.csv"


@pytest.mark.skipif(
    os.getenv("RUN_REAL_LLM_TESTS") != "1" or not os.getenv("DEEPSEEK_API_KEY"),
    reason="Set RUN_REAL_LLM_TESTS=1 and DEEPSEEK_API_KEY to run real DeepSeek integration tests.",
)
def test_deepseek_real_selector_integration():
    result = select_tool(
        user_input="生成 MA5-MA10 回测报告",
        file_path=FILE_PATH,
        mode="real",
    )

    assert isinstance(result, dict)
    assert "tool_name" in result
    assert "arguments" in result
    assert result["selector_mode"] == "real"
