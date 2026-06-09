import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finance_tools import generate_parameter_scan_chart


file_path = "data/stock_price_strategy.csv"

print("生成参数扫描图表：")
result = generate_parameter_scan_chart(
    file_path=file_path,
    sort_by="sharpe_ratio"
)
print(result)