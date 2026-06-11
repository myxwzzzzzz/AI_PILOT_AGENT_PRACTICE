from pathlib import Path

from finance_tools import generate_backtest_charts


FILE_PATH = "data/stock_price_strategy.csv"


def test_generate_backtest_charts(tmp_path):
    result = generate_backtest_charts(
        file_path=FILE_PATH,
        output_dir=str(tmp_path),
        short_window=5,
        long_window=10,
    )

    assert result["success"] is True
    assert Path(result["nav_chart_path"]).exists()
    assert Path(result["drawdown_chart_path"]).exists()
