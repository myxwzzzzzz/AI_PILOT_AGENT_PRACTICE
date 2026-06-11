from pathlib import Path

from finance_tools import generate_strategy_research_summary


FILE_PATH = "data/stock_price_strategy.csv"


def test_generate_strategy_research_summary(tmp_path):
    output_path = tmp_path / "strategy_research_summary.md"

    result = generate_strategy_research_summary(
        file_path=FILE_PATH,
        output_path=str(output_path),
        sort_by="sharpe_ratio",
    )

    assert result["success"] is True
    assert Path(result["output_path"]).exists()
