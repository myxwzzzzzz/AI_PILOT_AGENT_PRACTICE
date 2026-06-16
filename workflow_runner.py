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

from typing import Any

from llm_router import route_llm_tool_call
from workflow_planner import format_workflow_plan, plan_workflow


TERMINAL_SUCCESS_STATUS = "success"
TERMINAL_FAILED_STATUS = "failed"
PLANNING_FAILED_STATUS = "planning_failed"
NOT_WORKFLOW_STATUS = "not_workflow"


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
    }


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

    return summary


def _build_step_result(
    *,
    step_index: int,
    step: dict[str, Any],
    execution_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize one step execution result.
    """
    tool_result = execution_result.get("tool_result")
    success = bool(execution_result.get("success"))

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
        "error": execution_result.get("error") or (tool_result or {}).get("error"),
        "trace": execution_result.get("trace", {}),
    }

    return step_result


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
    trace = _build_initial_trace(plan, file_path)
    trace["stop_on_failure"] = stop_on_failure

    if not plan.get("success"):
        trace["execution_status"] = PLANNING_FAILED_STATUS
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
            "trace": trace,
        }

    if not plan.get("is_workflow"):
        trace["execution_status"] = NOT_WORKFLOW_STATUS
        return {
            "success": False,
            "is_workflow": False,
            "workflow_name": None,
            "workflow_display_name": None,
            "workflow_status": NOT_WORKFLOW_STATUS,
            "error": plan.get("reason", "当前输入不是 workflow 请求。"),
            "step_results": [],
            "outputs": {},
            "trace": trace,
        }

    steps = plan.get("steps", [])
    step_results: list[dict[str, Any]] = []
    outputs: dict[str, Any] = {}

    trace["execution_status"] = "running"

    for index, step in enumerate(steps, start=1):
        tool_name = step.get("tool_name")
        arguments = step.get("arguments", {}) or {}

        execution_result = route_llm_tool_call(
            llm_tool_call={
                "tool_name": tool_name,
                "arguments": arguments,
            },
            file_path=file_path,
        )

        step_result = _build_step_result(
            step_index=index,
            step=step,
            execution_result=execution_result,
        )
        step_results.append(step_result)

        output_key = step.get("output_key")
        if output_key and step_result["success"]:
            outputs[output_key] = _summarize_tool_result(step_result.get("tool_result"))

        if not step_result["success"] and stop_on_failure:
            trace["execution_status"] = TERMINAL_FAILED_STATUS
            trace["completed_steps"] = len([item for item in step_results if item.get("success")])
            trace["failed_step_id"] = step_result.get("step_id")
            trace["failed_tool_name"] = step_result.get("tool_name")

            return {
                "success": False,
                "is_workflow": True,
                "workflow_name": plan.get("workflow_name"),
                "workflow_display_name": plan.get("workflow_display_name"),
                "workflow_status": TERMINAL_FAILED_STATUS,
                "error": step_result.get("error") or f"步骤 {step_result.get('step_id')} 执行失败。",
                "failed_step": step_result,
                "step_results": step_results,
                "outputs": outputs,
                "trace": trace,
            }

    failed_steps = [step_result for step_result in step_results if not step_result.get("success")]

    if failed_steps:
        trace["execution_status"] = TERMINAL_FAILED_STATUS
        trace["completed_steps"] = len([item for item in step_results if item.get("success")])
        trace["failed_step_count"] = len(failed_steps)

        return {
            "success": False,
            "is_workflow": True,
            "workflow_name": plan.get("workflow_name"),
            "workflow_display_name": plan.get("workflow_display_name"),
            "workflow_status": TERMINAL_FAILED_STATUS,
            "error": "Workflow 执行完成，但存在失败步骤。",
            "failed_steps": failed_steps,
            "step_results": step_results,
            "outputs": outputs,
            "trace": trace,
        }

    trace["execution_status"] = TERMINAL_SUCCESS_STATUS
    trace["completed_steps"] = len(step_results)
    trace["failed_step_count"] = 0

    return {
        "success": True,
        "is_workflow": True,
        "workflow_name": plan.get("workflow_name"),
        "workflow_display_name": plan.get("workflow_display_name"),
        "workflow_status": TERMINAL_SUCCESS_STATUS,
        "step_results": step_results,
        "outputs": outputs,
        "trace": trace,
    }


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

    lines = [
        f"Workflow 执行结果：{result.get('workflow_display_name') or result.get('workflow_name')}",
        f"状态：{'成功' if result.get('success') else '失败'}",
        "",
        "执行步骤：",
    ]

    for step_result in result.get("step_results", []):
        status_text = "成功" if step_result.get("success") else "失败"
        line = (
            f"{step_result.get('step_index')}. [{status_text}] "
            f"{step_result.get('description')} "
            f"(tool: {step_result.get('tool_name')})"
        )
        if step_result.get("error"):
            line += f"\n   错误：{step_result.get('error')}"
        lines.append(line)

    if result.get("outputs"):
        lines.append("")
        lines.append("关键输出：")
        for output_key, output_value in result["outputs"].items():
            if output_value.get("output_path"):
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
