from pathlib import Path

from finance_tools import (
    calculate_stock_metrics,
    generate_stock_metrics_report,
    read_stock_price_data,
)


FILE_PATH = "data/stock_price.csv"


def test_read_stock_price_data():
    result = read_stock_price_data(FILE_PATH)

    assert result["success"] is True
    assert result["rows"] > 0
    assert "date" in result["columns"]
    assert "close" in result["columns"]


def test_calculate_stock_metrics():
    result = calculate_stock_metrics(FILE_PATH)

    assert result["success"] is True
    assert "total_return" in result
    assert "annualized_volatility" in result
    assert "max_drawdown" in result
    assert "sharpe_ratio" in result


def test_generate_stock_metrics_report(tmp_path):
    output_path = tmp_path / "stock_metrics_report.md"

    result = generate_stock_metrics_report(
        file_path=FILE_PATH,
        output_path=str(output_path),
    )

    assert result["success"] is True
    assert Path(result["output_path"]).exists()
