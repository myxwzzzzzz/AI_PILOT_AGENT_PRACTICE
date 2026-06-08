from finance_tools import generate_strategy_research_summary


file_path = "data/stock_price_strategy.csv"

print("生成策略研究总结报告：")
result = generate_strategy_research_summary(
    file_path=file_path,
    output_path="data/strategy_research_summary.md",
    sort_by="sharpe_ratio"
)
print(result)