from finance_tools import (
    read_stock_price_data,
    calculate_stock_metrics,
    generate_stock_metrics_report
)


file_path = "data/stock_price.csv"

print("读取股票价格数据：")
read_result = read_stock_price_data(file_path)
print(read_result)

print("\n计算金融指标：")
metrics_result = calculate_stock_metrics(file_path)
print(metrics_result)

print("\n生成金融指标报告：")
report_result = generate_stock_metrics_report(
    file_path,
    "data/stock_metrics_report.md"
)
print(report_result)