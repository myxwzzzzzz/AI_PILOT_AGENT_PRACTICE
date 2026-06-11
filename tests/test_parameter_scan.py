from pathlib import Path

from finance_tools import generate_parameter_scan_report, optimize_moving_average_parameters


FILE_PATH = "data/stock_price_strategy.csv"


def test_optimize_moving_average_parameters():
    result = optimize_moving_average_parameters(
        file_path=FILE_PATH,
        sort_by="sharpe_ratio",
    )

    assert result["success"] is True
    assert result["sort_by"] == "sharpe_ratio"
    assert result["total_combinations"] > 0
    assert "best_result" in result


def test_generate_parameter_scan_report(tmp_path):
    output_path = tmp_path / "parameter_scan_report.md"

    result = generate_parameter_scan_report(
        file_path=FILE_PATH,
        output_path=str(output_path),
        sort_by="sharpe_ratio",
    )

    assert result["success"] is True
    assert Path(result["output_path"]).exists()
