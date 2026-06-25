"""
Workflow runner prototype.

This module is the second step from single-step Tool Calling toward
multi-step Agent Workflow.

Current scope:
- Execute an already planned workflow step by step.
- Reuse llm_router.route_llm_tool_call for tool validation and safe execution.
- Stop on the first failed step by default.
- Keep execution deterministic and testable before adding LLM replanning.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any

from llm_router import route_llm_tool_call
from workflow_planner import format_workflow_plan, plan_workflow
from workflow_summary_report import generate_workflow_summary_report


TERMINAL_SUCCESS_STATUS = "success"
TERMINAL_FAILED_STATUS = "failed"
PLANNING_FAILED_STATUS = "planning_failed"
NOT_WORKFLOW_STATUS = "not_workflow"


OUTPUT_PATH_KEYS = [
    "output_path",
    "report_path",
    "chart_path",
    "nav_chart_path",
    "drawdown_chart_path",
]


def _build_initial_trace(plan: dict[str, Any], file_path: str) -> dict[str, Any]:
    """
    Build the top-level workflow execution trace.
    """
    return {
        "runner_type": "rule_based_workflow_runner",
        "workflow_name": plan.get("workflow_name"),
        "workflow_display_name": plan.get("workflow_display_name"),
        "current_file_path": file_path,
        "planned_step_count": len(plan.get("steps", [])),
        "execution_status": "not_started",
        "stop_on_failure": True,
        "step_traces": [],
        "generated_files": [],
    }


def _extract_output_paths(tool_result: dict[str, Any] | None) -> list[str]:
    """
    Extract generated file paths from a tool result.

    Existing tools do not all use exactly the same field name. Reports usually
    use output_path, charts may use chart_path, and backtest charts may return
    nav_chart_path / drawdown_chart_path. The workflow layer normalizes those
    fields so users can see all generated files in one place.
    """
    if not isinstance(tool_result, dict):
        return []

    paths: list[str] = []

    for key in OUTPUT_PATH_KEYS:
        value = tool_result.get(key)
        if isinstance(value, str) and value:
            paths.append(value)

    for key, value in tool_result.items():
        if not key.endswith("_path"):
            continue
        if isinstance(value, str) and value and value not in paths:
            paths.append(value)

    return paths


def _summarize_tool_result(tool_result: dict[str, Any] | None) -> dict[str, Any]:
    """
    Keep compact output metadata for workflow-level result aggregation.

    Full tool outputs are still preserved in each step_result. The workflow-level
    outputs mapping stores the most useful fields so the final result remains
    readable in CLI output and trace views.
    """
    if not isinstance(tool_result, dict):
        return {}

    summary: dict[str, Any] = {
        "success": tool_result.get("success"),
    }

    for key in ["message", "output_path", "summary", "error"]:
        if key in tool_result:
            summary[key] = tool_result[key]

    output_paths = _extract_output_paths(tool_result)
    if output_paths:
        summary["output_paths"] = output_paths
        summary["primary_output_path"] = output_paths[0]

    for key in ["sort_by", "short_window", "long_window", "total_combinations"]:
        if key in tool_result:
            summary[key] = tool_result[key]

    return summary


def _build_step_trace(step_result: dict[str, Any], elapsed_seconds: float) -> dict[str, Any]:
    """
    Build a compact trace record for one workflow step.
    """
    return {
        "step_index": step_result.get("step_index"),
        "step_id": step_result.get("step_id"),
        "tool_name": step_result.get("tool_name"),
        "arguments": step_result.get("arguments", {}),
        "execution_status": step_result.get("execution_status"),
        "success": step_result.get("success"),
        "elapsed_seconds": round(elapsed_seconds, 4),
        "output_key": step_result.get("output_key"),
        "output_paths": step_result.get("output_paths", []),
        "error": step_result.get("error"),
    }


def _build_step_result(
    *,
    step_index: int,
    step: dict[str, Any],
    execution_result: dict[str, Any],
    elapsed_seconds: float = 0.0,
) -> dict[str, Any]:
    """
    Normalize one step execution result.
    """
    tool_result = execution_result.get("tool_result")
    success = bool(execution_result.get("success"))
    output_paths = _extract_output_paths(tool_result)

    step_result = {
        "step_index": step_index,
        "step_id": step.get("step_id"),
        "description": step.get("description"),
        "tool_name": step.get("tool_name"),
        "arguments": step.get("arguments", {}),
        "output_key": step.get("output_key"),
        "success": success,
        "execution_status": "success" if success else "failed",
        "tool_result": tool_result,
        "output_paths": output_paths,
        "elapsed_seconds": round(elapsed_seconds, 4),
        "error": execution_result.get("error") or (tool_result or {}).get("error"),
        "trace": execution_result.get("trace", {}),
    }

    return step_result


def _build_workflow_summary(
    *,
    plan: dict[str, Any],
    step_results: list[dict[str, Any]],
    generated_files: list[str],
    workflow_status: str,
    elapsed_seconds: float,
) -> dict[str, Any]:
    """
    Build high-level workflow summary metadata.
    """
    successful_steps = [step for step in step_results if step.get("success")]
    failed_steps = [step for step in step_results if not step.get("success")]

    planning_metadata = plan.get("planning_metadata", {}) or {}

    return {
        "workflow_name": plan.get("workflow_name"),
        "workflow_display_name": plan.get("workflow_display_name"),
        "workflow_status": workflow_status,
        "planned_step_count": len(plan.get("steps", [])),
        "executed_step_count": len(step_results),
        "successful_step_count": len(successful_steps),
        "failed_step_count": len(failed_steps),
        "generated_file_count": len(generated_files),
        "generated_files": generated_files,
        "sort_by": planning_metadata.get("sort_by"),
        "sort_by_name": planning_metadata.get("sort_by_name"),
        "elapsed_seconds": round(elapsed_seconds, 4),
    }




def _attach_workflow_summary_report(result: dict[str, Any], file_path: str) -> dict[str, Any]:
    """
    Generate and attach a workflow-level Markdown summary report.

    The summary report is a workflow-level artifact, different from the
    underlying tool reports. If report generation fails, the workflow execution
    result is still returned; the summary report error is recorded in trace.
    """
    if not result.get("is_workflow") or not result.get("step_results"):
        return result

    try:
        report_result = generate_workflow_summary_report(
            workflow_result=result,
            file_path=file_path,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        result.setdefault("trace", {})["workflow_summary_report"] = {
            "success": False,
            "error": str(exc),
        }
        return result

    result.setdefault("outputs", {})["workflow_summary_report"] = {
        "success": report_result.get("success"),
        "message": report_result.get("message"),
        "output_path": report_result.get("output_path"),
    }

    output_path = report_result.get("output_path")
    if output_path:
        generated_files = result.setdefault("generated_files", [])
        if output_path not in generated_files:
            generated_files.append(output_path)

        summary = result.setdefault("workflow_summary", {})
        summary["generated_files"] = generated_files
        summary["generated_file_count"] = len(generated_files)

        trace = result.setdefault("trace", {})
        trace["generated_files"] = generated_files
        trace["workflow_summary_report"] = {
            "success": report_result.get("success"),
            "output_path": output_path,
        }

    return result

def run_workflow_plan(
    plan: dict[str, Any],
    file_path: str,
    *,
    stop_on_failure: bool = True,
) -> dict[str, Any]:
    """
    Execute a workflow plan step by step.

    Parameters
    ----------
    plan:
        A workflow plan produced by workflow_planner.plan_workflow().
    file_path:
        Current data file path.
    stop_on_failure:
        If True, stop at the first failed step. The first prototype keeps this
        default because it is easier to explain, test, and debug.
    """
    workflow_start = perf_counter()
    trace = _build_initial_trace(plan, file_path)
    trace["stop_on_failure"] = stop_on_failure

    if not plan.get("success"):
        trace["execution_status"] = PLANNING_FAILED_STATUS
        trace["elapsed_seconds"] = round(perf_counter() - workflow_start, 4)
        return {
            "success": False,
            "is_workflow": plan.get("is_workflow", False),
            "workflow_name": plan.get("workflow_name"),
            "workflow_display_name": plan.get("workflow_display_name"),
            "workflow_status": PLANNING_FAILED_STATUS,
            "error": plan.get("error", "Workflow 规划失败，无法执行。"),
            "suggestion": plan.get("suggestion"),
            "step_results": [],
            "outputs": {},
            "generated_files": [],
            "workflow_summary": _build_workflow_summary(
                plan=plan,
                step_results=[],
                generated_files=[],
                workflow_status=PLANNING_FAILED_STATUS,
                elapsed_seconds=trace["elapsed_seconds"],
            ),
            "trace": trace,
        }

    if not plan.get("is_workflow"):
        trace["execution_status"] = NOT_WORKFLOW_STATUS
        trace["elapsed_seconds"] = round(perf_counter() - workflow_start, 4)
        return {
            "success": False,
            "is_workflow": False,
            "workflow_name": None,
            "workflow_display_name": None,
            "workflow_status": NOT_WORKFLOW_STATUS,
            "error": plan.get("reason", "当前输入不是 workflow 请求。"),
            "step_results": [],
            "outputs": {},
            "generated_files": [],
            "workflow_summary": _build_workflow_summary(
                plan=plan,
                step_results=[],
                generated_files=[],
                workflow_status=NOT_WORKFLOW_STATUS,
                elapsed_seconds=trace["elapsed_seconds"],
            ),
            "trace": trace,
        }

    steps = plan.get("steps", [])
    step_results: list[dict[str, Any]] = []
    outputs: dict[str, Any] = {}
    generated_files: list[str] = []

    trace["execution_status"] = "running"

    for index, step in enumerate(steps, start=1):
        tool_name = step.get("tool_name")
        arguments = step.get("arguments", {}) or {}

        step_start = perf_counter()
        execution_result = route_llm_tool_call(
            llm_tool_call={
                "tool_name": tool_name,
                "arguments": arguments,
            },
            file_path=file_path,
        )
        elapsed_seconds = perf_counter() - step_start

        step_result = _build_step_result(
            step_index=index,
            step=step,
            execution_result=execution_result,
            elapsed_seconds=elapsed_seconds,
        )
        step_results.append(step_result)

        for output_path in step_result.get("output_paths", []):
            if output_path not in generated_files:
                generated_files.append(output_path)

        output_key = step.get("output_key")
        if output_key and step_result["success"]:
            outputs[output_key] = _summarize_tool_result(step_result.get("tool_result"))

        trace["step_traces"].append(_build_step_trace(step_result, elapsed_seconds))
        trace["generated_files"] = generated_files

        if not step_result["success"] and stop_on_failure:
            trace["execution_status"] = TERMINAL_FAILED_STATUS
            trace["completed_steps"] = len([item for item in step_results if item.get("success")])
            trace["failed_step_id"] = step_result.get("step_id")
            trace["failed_tool_name"] = step_result.get("tool_name")
            trace["failed_step_count"] = len([item for item in step_results if not item.get("success")])
            trace["elapsed_seconds"] = round(perf_counter() - workflow_start, 4)

            result = {
                "success": False,
                "is_workflow": True,
                "workflow_name": plan.get("workflow_name"),
                "workflow_display_name": plan.get("workflow_display_name"),
                "workflow_status": TERMINAL_FAILED_STATUS,
                "error": step_result.get("error") or f"步骤 {step_result.get('step_id')} 执行失败。",
                "failed_step": step_result,
                "step_results": step_results,
                "outputs": outputs,
                "generated_files": generated_files,
                "workflow_summary": _build_workflow_summary(
                    plan=plan,
                    step_results=step_results,
                    generated_files=generated_files,
                    workflow_status=TERMINAL_FAILED_STATUS,
                    elapsed_seconds=trace["elapsed_seconds"],
                ),
                "trace": trace,
            }
            return _attach_workflow_summary_report(result, file_path)

    failed_steps = [step_result for step_result in step_results if not step_result.get("success")]

    if failed_steps:
        trace["execution_status"] = TERMINAL_FAILED_STATUS
        trace["completed_steps"] = len([item for item in step_results if item.get("success")])
        trace["failed_step_count"] = len(failed_steps)
        trace["elapsed_seconds"] = round(perf_counter() - workflow_start, 4)

        result = {
            "success": False,
            "is_workflow": True,
            "workflow_name": plan.get("workflow_name"),
            "workflow_display_name": plan.get("workflow_display_name"),
            "workflow_status": TERMINAL_FAILED_STATUS,
            "error": "Workflow 执行完成，但存在失败步骤。",
            "failed_steps": failed_steps,
            "step_results": step_results,
            "outputs": outputs,
            "generated_files": generated_files,
            "workflow_summary": _build_workflow_summary(
                plan=plan,
                step_results=step_results,
                generated_files=generated_files,
                workflow_status=TERMINAL_FAILED_STATUS,
                elapsed_seconds=trace["elapsed_seconds"],
            ),
            "trace": trace,
        }
        return _attach_workflow_summary_report(result, file_path)

    trace["execution_status"] = TERMINAL_SUCCESS_STATUS
    trace["completed_steps"] = len(step_results)
    trace["failed_step_count"] = 0
    trace["elapsed_seconds"] = round(perf_counter() - workflow_start, 4)

    result = {
        "success": True,
        "is_workflow": True,
        "workflow_name": plan.get("workflow_name"),
        "workflow_display_name": plan.get("workflow_display_name"),
        "workflow_status": TERMINAL_SUCCESS_STATUS,
        "step_results": step_results,
        "outputs": outputs,
        "generated_files": generated_files,
        "workflow_summary": _build_workflow_summary(
            plan=plan,
            step_results=step_results,
            generated_files=generated_files,
            workflow_status=TERMINAL_SUCCESS_STATUS,
            elapsed_seconds=trace["elapsed_seconds"],
        ),
        "trace": trace,
    }
    return _attach_workflow_summary_report(result, file_path)


def run_workflow(
    user_input: str,
    file_path: str,
    *,
    stop_on_failure: bool = True,
) -> dict[str, Any]:
    """
    Plan and execute a workflow request.

    This helper keeps planner and runner connected, but still separates their
    responsibilities internally.
    """
    plan = plan_workflow(user_input=user_input, file_path=file_path)

    if not plan.get("success") or not plan.get("is_workflow"):
        result = run_workflow_plan(
            plan=plan,
            file_path=file_path,
            stop_on_failure=stop_on_failure,
        )
        result["plan"] = plan
        return result

    result = run_workflow_plan(
        plan=plan,
        file_path=file_path,
        stop_on_failure=stop_on_failure,
    )
    result["plan"] = plan
    return result


def _format_arguments(arguments: dict[str, Any] | None) -> str:
    """
    Format step arguments for human-readable workflow output.
    """
    if not arguments:
        return "无"

    return ", ".join(
        f"{key}={value}"
        for key, value in arguments.items()
    )


def format_workflow_result(result: dict[str, Any]) -> str:
    """
    Format workflow execution result for CLI-style display.
    """
    if not result.get("is_workflow"):
        plan = result.get("plan")
        if isinstance(plan, dict):
            return format_workflow_plan(plan)
        return result.get("error", "当前输入不是 workflow 请求。")

    if result.get("workflow_status") == PLANNING_FAILED_STATUS:
        message = f"Workflow 无法执行：{result.get('error', '规划失败')}"
        if result.get("suggestion"):
            message += f"\n建议：{result['suggestion']}"
        return message

    summary = result.get("workflow_summary", {}) or {}

    lines = [
        f"Workflow 执行结果：{result.get('workflow_display_name') or result.get('workflow_name')}",
        f"状态：{'成功' if result.get('success') else '失败'}",
    ]

    sort_by = summary.get("sort_by")
    if sort_by:
        sort_by_name = summary.get("sort_by_name") or sort_by
        lines.append(f"排序指标：{sort_by_name} ({sort_by})")

    lines.extend([
        (
            "步骤概览："
            f"计划 {summary.get('planned_step_count', len(result.get('step_results', [])))} 步，"
            f"执行 {summary.get('executed_step_count', len(result.get('step_results', [])))} 步，"
            f"成功 {summary.get('successful_step_count', 0)} 步，"
            f"失败 {summary.get('failed_step_count', 0)} 步"
        ),
        f"生成文件数：{summary.get('generated_file_count', len(result.get('generated_files', [])))}",
        f"总耗时：{summary.get('elapsed_seconds', result.get('trace', {}).get('elapsed_seconds', 0))} 秒",
        "",
        "执行步骤：",
    ])

    for step_result in result.get("step_results", []):
        status_text = "成功" if step_result.get("success") else "失败"
        line = (
            f"{step_result.get('step_index')}. [{status_text}] "
            f"{step_result.get('description')} "
            f"(tool: {step_result.get('tool_name')})"
        )
        lines.append(line)
        lines.append(f"   参数：{_format_arguments(step_result.get('arguments'))}")
        lines.append(f"   耗时：{step_result.get('elapsed_seconds', 0)} 秒")

        if step_result.get("output_paths"):
            lines.append("   输出文件：")
            for output_path in step_result["output_paths"]:
                lines.append(f"   - {output_path}")

        if step_result.get("error"):
            lines.append(f"   错误：{step_result.get('error')}")

    generated_files = result.get("generated_files") or summary.get("generated_files") or []
    if generated_files:
        lines.append("")
        lines.append("本次 Workflow 生成文件：")
        for output_path in generated_files:
            lines.append(f"- {output_path}")

    if result.get("outputs"):
        lines.append("")
        lines.append("关键输出：")
        for output_key, output_value in result["outputs"].items():
            output_paths = output_value.get("output_paths") or []
            if output_paths:
                lines.append(f"- {output_key}: {output_paths[0]}")
            elif output_value.get("output_path"):
                lines.append(f"- {output_key}: {output_value['output_path']}")
            elif output_value.get("message"):
                lines.append(f"- {output_key}: {output_value['message']}")
            else:
                lines.append(f"- {output_key}: success={output_value.get('success')}")

    if not result.get("success") and result.get("error"):
        lines.append("")
        lines.append(f"失败原因：{result.get('error')}")

    return "\n".join(lines)


if __name__ == "__main__":
    demo_result = run_workflow(
        user_input="帮我完整分析这份股票数据，并生成策略研究报告",
        file_path="data/stock_price_strategy.csv",
    )
    print(format_workflow_result(demo_result))
