from finance_tools import (
    optimize_moving_average_parameters,
    generate_parameter_scan_report
)


file_path = "data/stock_price_strategy.csv"

print("运行均线参数扫描：")
scan_result = optimize_moving_average_parameters(
    file_path=file_path,
    sort_by="sharpe_ratio"
)
print(scan_result)

print("\n生成均线参数扫描报告：")
report_result = generate_parameter_scan_report(
    file_path=file_path,
    output_path="data/parameter_scan_report.md",
    sort_by="sharpe_ratio"
)
print(report_result)