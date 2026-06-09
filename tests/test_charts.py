import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finance_tools import generate_backtest_charts


file_path = "data/stock_price_strategy.csv"

print("生成回测图表：")
result = generate_backtest_charts(
    file_path=file_path,
    short_window=5,
    long_window=10
)
print(result)