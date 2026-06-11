from pathlib import Path

from finance_tools import generate_backtest_report, run_moving_average_backtest


FILE_PATH = "data/stock_price_strategy.csv"


def test_run_moving_average_backtest():
    result = run_moving_average_backtest(
        file_path=FILE_PATH,
        short_window=3,
        long_window=5,
    )

    assert result["success"] is True
    assert result["short_window"] == 3
    assert result["long_window"] == 5
    assert "strategy_total_return" in result
    assert "max_drawdown" in result


def test_generate_backtest_report(tmp_path):
    output_path = tmp_path / "backtest_report.md"

    result = generate_backtest_report(
        file_path=FILE_PATH,
        output_path=str(output_path),
        short_window=3,
        long_window=5,
    )

    assert result["success"] is True
    assert Path(result["output_path"]).exists()
