
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm_agent_runner import run_llm_agent_task


file_path = "data/stock_price_strategy.csv"


print("测试 1：mock selector 正常执行")
result = run_llm_agent_task(
    user_input="生成 MA5-MA10 回测报告",
    file_path=file_path,
    selector_mode="mock"
)
print(result)


print("\n测试 2：非法 selector mode，自动 fallback 到 mock")
result = run_llm_agent_task(
    user_input="生成 MA5-MA10 回测报告",
    file_path=file_path,
    selector_mode="bad_mode"
)
print(result)


print("\n测试 3：无工具意图，fallback 到规则 router")
result = run_llm_agent_task(
    user_input="随便聊聊天",
    file_path=file_path,
    selector_mode="bad_mode"
)
print(result)