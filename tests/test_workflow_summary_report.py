from pathlib import Path

from workflow_summary_report import (
    build_workflow_summary_markdown,
    generate_workflow_summary_report,
)


STOCK_FILE_PATH = "data/stock_price_strategy.csv"


def _sample_workflow_result():
    return {
        "success": True,
        "is_workflow": True,
        "workflow_name": "stock_strategy_research",
        "workflow_display_name": "股票策略研究工作流",
        "plan": {
            "trace": {
                "user_input": "完整分析股票数据，并按夏普比率生成策略研究报告",
            }
        },
        "workflow_summary": {
            "workflow_status": "success",
            "planned_step_count": 2,
            "executed_step_count": 2,
            "successful_step_count": 2,
            "failed_step_count": 0,
            "generated_file_count": 2,
            "generated_files": [
                "data/output/reports/stock_metrics_report.md",
                "data/output/reports/strategy_research_summary_sharpe_ratio.md",
            ],
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
            "elapsed_seconds": 0.25,
        },
        "generated_files": [
            "data/output/reports/stock_metrics_report.md",
            "data/output/reports/strategy_research_summary_sharpe_ratio.md",
        ],
        "step_results": [
            {
                "step_index": 1,
                "success": True,
                "description": "生成基础指标报告",
                "tool_name": "generate_stock_metrics_report",
                "arguments": {},
                "output_paths": ["data/output/reports/stock_metrics_report.md"],
            },
            {
                "step_index": 2,
                "success": True,
                "description": "生成策略总结报告",
                "tool_name": "generate_strategy_research_summary",
                "arguments": {"sort_by": "sharpe_ratio"},
                "output_paths": ["data/output/reports/strategy_research_summary_sharpe_ratio.md"],
            },
        ],
    }


def test_build_workflow_summary_markdown_contains_task_and_outputs():
    markdown = build_workflow_summary_markdown(
        _sample_workflow_result(),
        file_path=STOCK_FILE_PATH,
    )

    assert "# Workflow 总结报告" in markdown
    assert "完整分析股票数据" in markdown
    assert "夏普比率（sharpe_ratio）" in markdown
    assert "生成基础指标报告" in markdown
    assert "strategy_research_summary_sharpe_ratio.md" in markdown
    assert "建议查看顺序" in markdown


def test_generate_workflow_summary_report_writes_markdown(tmp_path):
    result = generate_workflow_summary_report(
        _sample_workflow_result(),
        file_path=STOCK_FILE_PATH,
        output_dir=tmp_path,
    )

    assert result["success"] is True
    assert result["output_path"].endswith("workflow_summary_report_sharpe_ratio.md")

    report_path = Path(result["output_path"])
    assert report_path.exists()

    content = report_path.read_text(encoding="utf-8")
    assert "Workflow 总结报告" in content
    assert "本次生成文件" in content
    assert "strategy_research_summary_sharpe_ratio.md" in content


def test_build_workflow_summary_markdown_handles_failed_workflow():
    workflow_result = _sample_workflow_result()
    workflow_result["success"] = False
    workflow_result["error"] = "第二步执行失败"
    workflow_result["workflow_summary"]["failed_step_count"] = 1

    markdown = build_workflow_summary_markdown(
        workflow_result,
        file_path=STOCK_FILE_PATH,
    )

    assert "执行状态：失败" in markdown
    assert "第二步执行失败" in markdown
