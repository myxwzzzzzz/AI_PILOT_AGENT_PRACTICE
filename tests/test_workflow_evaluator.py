from workflow_evaluator import evaluate_workflow_result


def _workflow_result_with_metrics(*, max_drawdown=-0.08, sharpe=1.2, excess=0.08):
    return {
        "success": True,
        "is_workflow": True,
        "workflow_summary": {
            "sort_by": "sharpe_ratio",
        },
        "step_results": [
            {
                "tool_name": "calculate_stock_metrics",
                "success": True,
                "tool_result": {
                    "success": True,
                    "total_return": 0.12,
                    "max_drawdown": -0.12,
                    "sharpe_ratio": 0.8,
                },
            },
            {
                "tool_name": "optimize_moving_average_parameters",
                "success": True,
                "tool_result": {
                    "success": True,
                    "sort_by": "sharpe_ratio",
                    "total_combinations": 9,
                    "best_result": {
                        "strategy_name": "MA5-MA10",
                        "strategy_total_return": 0.18,
                        "excess_return": excess,
                        "max_drawdown": max_drawdown,
                        "sharpe_ratio": sharpe,
                    },
                },
            },
        ],
    }


def test_evaluate_workflow_result_returns_positive_judgement():
    judgement = evaluate_workflow_result(
        _workflow_result_with_metrics(max_drawdown=-0.08, sharpe=1.2, excess=0.08)
    )

    assert judgement["success"] is True
    assert judgement["evaluation_status"] == "completed"
    assert judgement["overall_label"] == "具备继续研究价值"
    assert judgement["risk_level"] == "low"
    assert judgement["quality_level"] == "good"
    assert judgement["excess_return_level"] == "positive"
    assert judgement["metrics"]["best_strategy_name"] == "MA5-MA10"
    assert judgement["warnings"]
    assert judgement["suggestions"]


def test_evaluate_workflow_result_flags_high_drawdown_and_negative_excess():
    judgement = evaluate_workflow_result(
        _workflow_result_with_metrics(max_drawdown=-0.25, sharpe=0.2, excess=-0.03)
    )

    assert judgement["overall_label"] == "需要谨慎"
    assert judgement["risk_level"] == "high"
    assert judgement["quality_level"] == "poor"
    assert judgement["excess_return_level"] == "negative"
    assert any("最大回撤" in item for item in judgement["findings"])
    assert any("不宜过度外推" in item for item in judgement["warnings"])


def test_evaluate_workflow_result_skips_non_workflow_result():
    judgement = evaluate_workflow_result({"is_workflow": False})

    assert judgement["success"] is False
    assert judgement["evaluation_status"] == "skipped"
