import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finance_tools import generate_strategy_research_summary


file_path = "data/stock_price_strategy.csv"

print("生成策略研究总结报告：")
result = generate_strategy_research_summary(
    file_path=file_path,
    sort_by="sharpe_ratio"
)
print(result)