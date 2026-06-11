from pathlib import Path

from finance_tools import generate_parameter_scan_chart


FILE_PATH = "data/stock_price_strategy.csv"


def test_generate_parameter_scan_chart(tmp_path):
    result = generate_parameter_scan_chart(
        file_path=FILE_PATH,
        output_dir=str(tmp_path),
        sort_by="sharpe_ratio",
    )

    assert result["success"] is True
    assert Path(result["chart_path"]).exists()
