"""
Workflow result evaluator.

This module adds a lightweight conditional judgement layer on top of workflow
execution results. It does not execute tools and does not call an LLM. Instead,
it reads the structured outputs produced by workflow steps and generates simple,
traceable risk / quality / strategy findings.

Current scope:
- Evaluate stock strategy research workflow results.
- Use deterministic rules for max drawdown, Sharpe ratio and excess return.
- Return human-readable findings and suggestions for CLI output / reports.
"""

from __future__ import annotations

from typing import Any


HIGH_RISK_DRAWDOWN = -0.20
MEDIUM_RISK_DRAWDOWN = -0.10
GOOD_SHARPE = 1.0
STRONG_SHARPE = 1.5
WEAK_SHARPE = 0.5
MEANINGFUL_EXCESS_RETURN = 0.05


def _as_float(value: Any) -> float | None:
    """
    Safely convert a metric value to float.
    """
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_percent(value: float | None) -> str:
    """
    Format a decimal metric as percentage text.
    """
    if value is None:
        return "无法计算"
    return f"{value * 100:.2f}%"


def _format_number(value: float | None) -> str:
    """
    Format a numeric metric for judgement text.
    """
    if value is None:
        return "无法计算"
    return f"{value:.4f}"


def _find_step_tool_result(workflow_result: dict[str, Any], tool_name: str) -> dict[str, Any] | None:
    """
    Find the first successful tool result for a workflow step by tool name.
    """
    for step in workflow_result.get("step_results", []) or []:
        if step.get("tool_name") != tool_name:
            continue
        tool_result = step.get("tool_result")
        if isinstance(tool_result, dict) and tool_result.get("success"):
            return tool_result
    return None


def _extract_metrics(workflow_result: dict[str, Any]) -> dict[str, Any]:
    """
    Extract core metrics from workflow step outputs.
    """
    metrics_result = _find_step_tool_result(workflow_result, "calculate_stock_metrics") or {}
    scan_result = _find_step_tool_result(workflow_result, "optimize_moving_average_parameters") or {}
    summary_report_result = _find_step_tool_result(workflow_result, "generate_strategy_research_summary") or {}

    best_result = scan_result.get("best_result") if isinstance(scan_result.get("best_result"), dict) else {}
    summary = summary_report_result.get("summary") if isinstance(summary_report_result.get("summary"), dict) else {}

    return {
        "asset_total_return": _as_float(metrics_result.get("total_return")),
        "asset_max_drawdown": _as_float(metrics_result.get("max_drawdown")),
        "asset_sharpe_ratio": _as_float(metrics_result.get("sharpe_ratio")),
        "best_strategy_name": best_result.get("strategy_name") or summary.get("best_strategy_name"),
        "best_strategy_return": _as_float(best_result.get("strategy_total_return", summary.get("best_strategy_return"))),
        "best_excess_return": _as_float(best_result.get("excess_return", summary.get("best_excess_return"))),
        "best_max_drawdown": _as_float(best_result.get("max_drawdown", summary.get("best_max_drawdown"))),
        "best_sharpe_ratio": _as_float(best_result.get("sharpe_ratio", summary.get("best_sharpe_ratio"))),
        "scan_total_combinations": scan_result.get("total_combinations"),
        "sort_by": scan_result.get("sort_by") or (workflow_result.get("workflow_summary") or {}).get("sort_by"),
    }


def _judge_drawdown(max_drawdown: float | None) -> tuple[str, str]:
    """
    Judge drawdown risk level.
    """
    if max_drawdown is None:
        return "unknown", "最大回撤无法计算，暂时无法判断下行风险。"
    if max_drawdown <= HIGH_RISK_DRAWDOWN:
        return "high", f"最大回撤为 {_format_percent(max_drawdown)}，下行风险较高。"
    if max_drawdown <= MEDIUM_RISK_DRAWDOWN:
        return "medium", f"最大回撤为 {_format_percent(max_drawdown)}，存在一定下行风险。"
    return "low", f"最大回撤为 {_format_percent(max_drawdown)}，样本内回撤相对可控。"


def _judge_sharpe(sharpe_ratio: float | None) -> tuple[str, str]:
    """
    Judge Sharpe ratio quality.
    """
    if sharpe_ratio is None:
        return "unknown", "夏普比率无法计算，暂时无法判断风险调整后收益。"
    if sharpe_ratio >= STRONG_SHARPE:
        return "strong", f"夏普比率为 {_format_number(sharpe_ratio)}，样本内风险调整后表现较强。"
    if sharpe_ratio >= GOOD_SHARPE:
        return "good", f"夏普比率为 {_format_number(sharpe_ratio)}，样本内风险调整后表现较好。"
    if sharpe_ratio >= WEAK_SHARPE:
        return "weak", f"夏普比率为 {_format_number(sharpe_ratio)}，表现一般，需要继续验证。"
    return "poor", f"夏普比率为 {_format_number(sharpe_ratio)}，风险调整后收益偏弱。"


def _judge_excess_return(excess_return: float | None) -> tuple[str, str]:
    """
    Judge whether the best strategy has meaningful excess return.
    """
    if excess_return is None:
        return "unknown", "未能获得最佳策略超额收益，暂时无法判断策略优势。"
    if excess_return > MEANINGFUL_EXCESS_RETURN:
        return "positive", f"最佳策略超额收益为 {_format_percent(excess_return)}，样本内存在较明显优势。"
    if excess_return > 0:
        return "limited", f"最佳策略超额收益为 {_format_percent(excess_return)}，优势存在但幅度有限。"
    return "negative", f"最佳策略超额收益为 {_format_percent(excess_return)}，未跑赢买入持有基准。"


def evaluate_workflow_result(workflow_result: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate a completed workflow result with deterministic conditional rules.

    The evaluator is intentionally lightweight. It only reads structured
    workflow outputs and produces judgement metadata. It does not change the
    workflow success status and does not execute additional tools.
    """
    if not workflow_result.get("is_workflow"):
        return {
            "success": False,
            "evaluation_status": "skipped",
            "reason": "当前结果不是 workflow 结果。",
            "findings": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {},
        }

    metrics = _extract_metrics(workflow_result)

    drawdown_level, drawdown_text = _judge_drawdown(metrics.get("best_max_drawdown"))
    sharpe_level, sharpe_text = _judge_sharpe(metrics.get("best_sharpe_ratio"))
    excess_level, excess_text = _judge_excess_return(metrics.get("best_excess_return"))

    findings = [drawdown_text, sharpe_text, excess_text]
    warnings: list[str] = []
    suggestions: list[str] = []

    if drawdown_level == "high":
        warnings.append("最佳策略样本内最大回撤较高，不建议只看收益率或夏普比率。")
        suggestions.append("后续应增加止损、仓位控制或风险预算规则。")
    elif drawdown_level == "medium":
        suggestions.append("建议在更长时间区间和不同市场环境下复查回撤稳定性。")

    if sharpe_level in {"poor", "weak", "unknown"}:
        warnings.append("策略风险调整后表现不够强，当前结论不宜过度外推。")
        suggestions.append("建议加入样本外测试和滚动窗口验证。")

    if excess_level in {"negative", "limited", "unknown"}:
        warnings.append("最佳参数组合相对买入持有的优势不明显。")
        suggestions.append("建议比较更多策略类型，而不是只依赖均线参数扫描。")
    else:
        suggestions.append("可以将当前最佳参数作为候选方案，但仍需加入交易成本和样本外检验。")

    if not warnings:
        warnings.append("当前样本内结果较好，但仍可能存在过拟合风险。")

    if not suggestions:
        suggestions.append("建议继续补充更长周期数据和交易成本假设。")

    if drawdown_level == "high" or excess_level == "negative":
        overall_label = "需要谨慎"
    elif sharpe_level in {"strong", "good"} and excess_level in {"positive", "limited"}:
        overall_label = "具备继续研究价值"
    else:
        overall_label = "结果一般，建议继续验证"

    return {
        "success": True,
        "evaluation_status": "completed",
        "evaluation_type": "rule_based_workflow_judgement",
        "overall_label": overall_label,
        "risk_level": drawdown_level,
        "quality_level": sharpe_level,
        "excess_return_level": excess_level,
        "metrics": metrics,
        "findings": findings,
        "warnings": warnings,
        "suggestions": suggestions,
        "rules": {
            "high_risk_drawdown": HIGH_RISK_DRAWDOWN,
            "medium_risk_drawdown": MEDIUM_RISK_DRAWDOWN,
            "good_sharpe": GOOD_SHARPE,
            "strong_sharpe": STRONG_SHARPE,
            "meaningful_excess_return": MEANINGFUL_EXCESS_RETURN,
        },
    }
