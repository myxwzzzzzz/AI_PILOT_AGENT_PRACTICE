"""
Workflow summary report generator.

This module turns a workflow execution result into a standalone Markdown
summary report. The report is different from single-tool reports: it describes
what the whole multi-step workflow did, which files it produced, and which
outputs users should inspect first.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import REPORT_DIR, ensure_output_dirs


SORT_BY_DISPLAY_NAMES = {
    "sharpe_ratio": "夏普比率",
    "strategy_total_return": "策略收益率",
    "excess_return": "超额收益",
    "max_drawdown": "最大回撤",
}


def _safe_text(value: Any, default: str = "未提供") -> str:
    """
    Convert a value to display text for Markdown reports.
    """
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _get_user_input(workflow_result: dict[str, Any]) -> str:
    """
    Extract the original user input from the workflow plan trace when possible.
    """
    plan = workflow_result.get("plan") or {}
    trace = plan.get("trace") or {}
    return trace.get("user_input") or "未记录"


def _get_sort_by_text(summary: dict[str, Any]) -> str:
    """
    Format the workflow sorting metric.
    """
    sort_by = summary.get("sort_by")
    if not sort_by:
        return "未指定"

    sort_by_name = summary.get("sort_by_name") or SORT_BY_DISPLAY_NAMES.get(sort_by, sort_by)
    return f"{sort_by_name}（{sort_by}）"


def _format_step_table(step_results: list[dict[str, Any]]) -> str:
    """
    Format workflow step results as a Markdown table.
    """
    if not step_results:
        return "暂无已执行步骤。"

    rows = [
        "| 序号 | 状态 | 步骤 | 工具 | 参数 | 输出文件 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for step in step_results:
        status = "成功" if step.get("success") else "失败"
        arguments = step.get("arguments") or {}
        if arguments:
            argument_text = ", ".join(f"{key}={value}" for key, value in arguments.items())
        else:
            argument_text = "无"

        output_paths = step.get("output_paths") or []
        if output_paths:
            output_text = "<br>".join(output_paths)
        else:
            output_text = "无"

        rows.append(
            "| "
            f"{step.get('step_index', '')} | "
            f"{status} | "
            f"{_safe_text(step.get('description'))} | "
            f"{_safe_text(step.get('tool_name'))} | "
            f"{argument_text} | "
            f"{output_text} |"
        )

    return "\n".join(rows)


def _format_generated_files(generated_files: list[str]) -> str:
    """
    Format generated file paths as a Markdown bullet list.
    """
    if not generated_files:
        return "- 暂无生成文件。"

    return "\n".join(f"- `{path}`" for path in generated_files)


def _build_review_order(generated_files: list[str]) -> str:
    """
    Build a simple suggested review order based on generated file names.
    """
    if not generated_files:
        return "暂无可查看文件。"

    priority_keywords = [
        ("strategy_research_summary", "优先查看策略研究总结报告，快速了解整体结论。"),
        ("workflow_summary_report", "查看 Workflow 总结报告，确认本次任务执行范围和生成文件。"),
        ("parameter_scan_report", "查看参数扫描报告，比较不同均线参数组合。"),
        ("parameter_scan_", "查看参数扫描图表，直观看到不同参数组合表现。"),
        ("stock_metrics_report", "查看基础风险收益指标报告，理解数据整体风险收益特征。"),
    ]

    suggestions: list[str] = []
    used_files: set[str] = set()

    for keyword, suggestion in priority_keywords:
        for path in generated_files:
            if keyword in path and path not in used_files:
                suggestions.append(f"- {suggestion}文件：`{path}`")
                used_files.add(path)
                break

    for path in generated_files:
        if path not in used_files:
            suggestions.append(f"- 其他产物：`{path}`")

    return "\n".join(suggestions)


def build_workflow_summary_markdown(
    workflow_result: dict[str, Any],
    *,
    file_path: str,
) -> str:
    """
    Build Markdown content for one workflow execution result.
    """
    summary = workflow_result.get("workflow_summary") or {}
    generated_files = workflow_result.get("generated_files") or summary.get("generated_files") or []
    step_results = workflow_result.get("step_results") or []

    status_text = "成功" if workflow_result.get("success") else "失败"
    user_input = _get_user_input(workflow_result)
    sort_by_text = _get_sort_by_text(summary)

    failed_reason = workflow_result.get("error") or "无"

    return f"""# Workflow 总结报告：{_safe_text(workflow_result.get('workflow_display_name') or workflow_result.get('workflow_name'))}

## 1. 本次任务

- 用户请求：{_safe_text(user_input)}
- 数据文件：`{file_path}`
- Workflow：`{_safe_text(workflow_result.get('workflow_name'))}`
- 执行状态：{status_text}
- 排序指标：{sort_by_text}

---

## 2. 执行概览

- 计划步骤数：{summary.get('planned_step_count', len(step_results))}
- 实际执行步骤数：{summary.get('executed_step_count', len(step_results))}
- 成功步骤数：{summary.get('successful_step_count', 0)}
- 失败步骤数：{summary.get('failed_step_count', 0)}
- 生成文件数：{len(generated_files)}
- 总耗时：{summary.get('elapsed_seconds', 0)} 秒

---

## 3. 执行步骤明细

{_format_step_table(step_results)}

---

## 4. 本次生成文件

{_format_generated_files(generated_files)}

---

## 5. 建议查看顺序

{_build_review_order(generated_files)}

---

## 6. 失败信息

{failed_reason}

---

## 7. 说明

本报告是 Workflow 层的汇总报告。它不会替代单个工具生成的专业报告，而是用于说明本次多步任务执行了哪些步骤、生成了哪些文件，以及用户应该按什么顺序查看这些结果。
"""


def generate_workflow_summary_report(
    workflow_result: dict[str, Any],
    *,
    file_path: str,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """
    Generate a Markdown summary report for a workflow execution.
    """
    ensure_output_dirs()

    summary = workflow_result.get("workflow_summary") or {}
    sort_by = summary.get("sort_by") or "default"

    if output_dir is None:
        output_dir = REPORT_DIR

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_path = output_path / f"workflow_summary_report_{sort_by}.md"
    content = build_workflow_summary_markdown(workflow_result, file_path=file_path)
    report_path.write_text(content, encoding="utf-8")

    return {
        "success": True,
        "message": "Workflow 总结报告已生成",
        "output_path": report_path.as_posix(),
        "sort_by": sort_by,
    }
