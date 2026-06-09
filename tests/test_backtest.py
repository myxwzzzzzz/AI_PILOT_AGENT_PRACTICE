import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finance_tools import (
    run_moving_average_backtest,
    generate_backtest_report
)


file_path = "data/stock_price_strategy.csv"

print("运行均线策略回测：")
backtest_result = run_moving_average_backtest(
    file_path=file_path,
    short_window=3,
    long_window=5
)
print(backtest_result)

print("\n生成均线策略回测报告：")
report_result = generate_backtest_report(
    file_path=file_path,
    short_window=3,
    long_window=5
)
print(report_result)