"""
Rule-based workflow planner prototype.

This module is the first small step from single-step Tool Calling toward
multi-step Agent Workflow.

Current scope:
- Only plan workflows; do not execute tools.
- Only support the first workflow: stock_strategy_research.
- Keep planning deterministic and testable before adding LLM planning.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from file_inspector import detect_file_type
from parameter_parser import extract_scan_sort_by
from tool_registry import get_tool_by_name


STOCK_STRATEGY_WORKFLOW_NAME = "stock_strategy_research"

WORKFLOW_TRIGGER_KEYWORDS = [
    "完整",
    "全面",
    "综合",
    "整体",
    "全流程",
    "从头到尾",
    "一整套",
    "系统分析",
]

STOCK_STRATEGY_KEYWORDS = [
    "股票",
    "策略",
    "均线",
    "回测",
    "参数扫描",
    "风险收益",
    "策略研究",
    "研究报告",
]


STOCK_STRATEGY_WORKFLOW_STEPS = [
    {
        "step_id": "read_stock_data",
        "tool_name": "read_stock_price_data",
        "description": "读取股票价格数据，确认日期区间、价格字段和数据规模。",
        "arguments": {},
        "output_key": "stock_data_overview",
    },
    {
        "step_id": "calculate_risk_return_metrics",
        "tool_name": "calculate_stock_metrics",
        "description": "计算基础风险收益指标，包括收益率、波动率、最大回撤和夏普比率。",
        "arguments": {},
        "output_key": "risk_return_metrics",
    },
    {
        "step_id": "generate_metrics_report",
        "tool_name": "generate_stock_metrics_report",
        "description": "生成金融风险收益指标 Markdown 报告。",
        "arguments": {},
        "output_key": "metrics_report",
    },
    {
        "step_id": "scan_ma_parameters",
        "tool_name": "optimize_moving_average_parameters",
        "description": "扫描多组均线参数，比较策略收益、超额收益、最大回撤和夏普比率。",
        "arguments": {},
        "output_key": "parameter_scan_result",
    },
    {
        "step_id": "generate_parameter_scan_report",
        "tool_name": "generate_parameter_scan_report",
        "description": "生成均线参数扫描对比报告。",
        "arguments": {},
        "output_key": "parameter_scan_report",
    },
    {
        "step_id": "generate_parameter_scan_chart",
        "tool_name": "generate_parameter_scan_chart",
        "description": "生成均线参数扫描图表，帮助比较不同参数组合。",
        "arguments": {},
        "output_key": "parameter_scan_chart",
    },
    {
        "step_id": "generate_strategy_summary",
        "tool_name": "generate_strategy_research_summary",
        "description": "综合基础指标、参数扫描和策略表现，生成策略研究总结报告。",
        "arguments": {},
        "output_key": "strategy_research_summary",
    },
]


SUPPORTED_WORKFLOWS = [
    {
        "name": STOCK_STRATEGY_WORKFLOW_NAME,
        "display_name": "股票策略研究工作流",
        "description": "面向股票价格数据的一整套风险收益分析、均线参数扫描和策略研究总结流程。",
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "steps": STOCK_STRATEGY_WORKFLOW_STEPS,
    }
]


def list_supported_workflows() -> list[dict[str, Any]]:
    """
    返回当前支持的 workflow 摘要。
    """
    summaries = []

    for workflow in SUPPORTED_WORKFLOWS:
        summaries.append(
            {
                "name": workflow["name"],
                "display_name": workflow["display_name"],
                "description": workflow["description"],
                "required_file_type_name": workflow["required_file_type_name"],
                "step_count": len(workflow["steps"]),
            }
        )

    return summaries


def get_supported_workflow(workflow_name: str | None) -> dict[str, Any] | None:
    """Return a supported workflow definition by internal workflow name."""

    if not workflow_name:
        return None

    for workflow in SUPPORTED_WORKFLOWS:
        if workflow["name"] == workflow_name:
            return workflow

    return None


def is_workflow_request(user_input: str) -> bool:
    """
    判断用户输入是否像一个多步 workflow 请求。

    设计上刻意偏保守：
    - 必须同时命中“完整/综合/全流程”等 workflow 意图词；
    - 也要命中股票策略相关领域词。

    这样可以避免把“生成策略研究总结报告”这类已有单工具任务误判为 workflow。
    """
    normalized_input = user_input.strip()

    has_workflow_trigger = any(keyword in normalized_input for keyword in WORKFLOW_TRIGGER_KEYWORDS)
    has_stock_strategy_context = any(keyword in normalized_input for keyword in STOCK_STRATEGY_KEYWORDS)

    return has_workflow_trigger and has_stock_strategy_context


def _build_file_type_error(
    workflow: dict[str, Any],
    file_path: str,
    file_info: dict[str, Any],
    trace: dict[str, Any],
) -> dict[str, Any]:
    """
    构造 workflow 文件类型不匹配结果。
    """
    current_file_type_name = file_info.get("file_type_name", "未知类型数据")
    required_file_type_name = workflow.get("required_file_type_name", "指定类型数据")

    trace["file_type_check"] = "failed"
    trace["planning_status"] = "blocked_by_file_type_check"

    return {
        "success": False,
        "is_workflow": True,
        "workflow_name": workflow["name"],
        "workflow_display_name": workflow["display_name"],
        "error": (
            f"当前 workflow 需要使用【{required_file_type_name}】，"
            f"但当前文件 {file_path} 被识别为【{current_file_type_name}】。"
        ),
        "suggestion": "请先切换到股票价格数据，例如：切换文件 data/stock_price_strategy.csv",
        "steps": [],
        "trace": trace,
    }


def _attach_tool_metadata(step: dict[str, Any]) -> dict[str, Any]:
    """
    为 workflow step 补充 Tool Registry 中的工具元信息。
    """
    enriched_step = deepcopy(step)
    tool = get_tool_by_name(step["tool_name"])

    if tool is None:
        enriched_step["tool_exists"] = False
        enriched_step["tool_description"] = None
        enriched_step["required_file_type"] = None
        enriched_step["required_file_type_name"] = None
        return enriched_step

    enriched_step["tool_exists"] = True
    enriched_step["tool_description"] = tool.get("description")
    enriched_step["required_file_type"] = tool.get("required_file_type")
    enriched_step["required_file_type_name"] = tool.get("required_file_type_name")

    return enriched_step


def build_stock_strategy_workflow_steps(user_input: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    根据用户输入生成股票策略研究 workflow 的步骤列表。

    当前只解析参数扫描排序指标 sort_by。
    后续可以继续扩展为解析 MA 默认参数、报告类型、图表类型等。
    """
    sort_parse_result = extract_scan_sort_by(user_input)
    sort_by = sort_parse_result.get("sort_by", "sharpe_ratio")

    steps = []

    for step in STOCK_STRATEGY_WORKFLOW_STEPS:
        enriched_step = _attach_tool_metadata(step)

        if enriched_step["tool_name"] in {
            "optimize_moving_average_parameters",
            "generate_parameter_scan_report",
            "generate_parameter_scan_chart",
            "generate_strategy_research_summary",
        }:
            enriched_step["arguments"] = {
                **enriched_step.get("arguments", {}),
                "sort_by": sort_by,
            }

        steps.append(enriched_step)

    metadata = {
        "sort_by": sort_by,
        "sort_by_name": sort_parse_result.get("sort_by_name"),
        "sort_by_source": sort_parse_result.get("source"),
    }

    return steps, metadata


def plan_workflow(
    user_input: str,
    file_path: str,
    *,
    workflow_name: str | None = None,
) -> dict[str, Any]:
    """
    为用户输入生成 workflow 计划。

    注意：本函数只负责规划，不执行任何工具。

    workflow_name 用于 Skill-aware Workflow Dispatch：当上层 Skill
    Dispatcher 已经明确选择某个 workflow 时，planner 可以绕过原来的
    文本启发式判断，但仍保留文件类型校验和步骤生成。
    """
    file_info = detect_file_type(file_path)

    trace = {
        "planner_type": "rule_based_workflow_planner",
        "user_input": user_input,
        "current_file_path": file_path,
        "current_file_type": file_info.get("file_type"),
        "current_file_type_name": file_info.get("file_type_name"),
        "requested_workflow_name": workflow_name,
        "planning_trigger": "skill_dispatch" if workflow_name else "heuristic",
        "matched_workflow": None,
        "planning_status": "not_started",
    }

    if not file_info.get("success"):
        trace["planning_status"] = "failed_file_inspection"
        return {
            "success": False,
            "is_workflow": False,
            "workflow_name": None,
            "reason": "文件类型识别失败，无法规划 workflow。",
            "error": file_info.get("error"),
            "steps": [],
            "trace": trace,
        }

    workflow = get_supported_workflow(workflow_name) if workflow_name else None

    if workflow_name and workflow is None:
        trace["planning_status"] = "unsupported_workflow"
        return {
            "success": False,
            "is_workflow": False,
            "workflow_name": workflow_name,
            "reason": "Skill Dispatcher 指定了 workflow，但当前 planner 尚不支持。",
            "error": f"Unsupported workflow: {workflow_name}",
            "steps": [],
            "trace": trace,
        }

    if workflow is None:
        if not is_workflow_request(user_input):
            trace["planning_status"] = "not_workflow_request"
            return {
                "success": True,
                "is_workflow": False,
                "workflow_name": None,
                "reason": "当前输入不像多步 workflow 请求，建议继续走单步 router 或 LLM Tool Calling。",
                "steps": [],
                "trace": trace,
            }

        workflow = SUPPORTED_WORKFLOWS[0]

    trace["matched_workflow"] = workflow["name"]

    if file_info.get("file_type") != workflow["required_file_type"]:
        return _build_file_type_error(
            workflow=workflow,
            file_path=file_path,
            file_info=file_info,
            trace=trace,
        )

    steps, planning_metadata = build_stock_strategy_workflow_steps(user_input)

    trace["file_type_check"] = "passed"
    trace["planning_status"] = "success"
    trace["step_count"] = len(steps)
    trace["planning_metadata"] = planning_metadata

    return {
        "success": True,
        "is_workflow": True,
        "workflow_name": workflow["name"],
        "workflow_display_name": workflow["display_name"],
        "description": workflow["description"],
        "reason": (
            "Skill Dispatcher 已指定 workflow，因此生成股票策略研究 workflow 计划。"
            if workflow_name
            else "用户输入命中了完整/综合分析类意图，并且当前文件是股票价格数据，因此生成股票策略研究 workflow 计划。"
        ),
        "steps": steps,
        "planning_metadata": planning_metadata,
        "trace": trace,
    }


def format_workflow_plan(plan: dict[str, Any]) -> str:
    """
    将 workflow plan 格式化为适合 CLI 展示的文本。
    """
    if not plan.get("success"):
        suggestion = plan.get("suggestion")
        message = f"Workflow 规划失败：{plan.get('error', '未知错误')}"
        if suggestion:
            message += f"\n建议：{suggestion}"
        return message

    if not plan.get("is_workflow"):
        return plan.get("reason", "当前输入不需要 workflow。")

    lines = [
        f"已生成 Workflow 计划：{plan.get('workflow_display_name')}",
        "",
        plan.get("description", ""),
        "",
        "计划步骤：",
    ]

    for index, step in enumerate(plan.get("steps", []), start=1):
        arguments = step.get("arguments", {})
        if arguments:
            argument_text = ", ".join(f"{key}={value}" for key, value in arguments.items())
        else:
            argument_text = "无"

        lines.append(
            f"{index}. {step.get('description')}\n"
            f"   - tool: {step.get('tool_name')}\n"
            f"   - arguments: {argument_text}"
        )

    lines.append("")
    lines.append("说明：当前版本只生成计划，不自动执行这些步骤。")

    return "\n".join(lines)


if __name__ == "__main__":
    demo_plan = plan_workflow(
        user_input="帮我完整分析这份股票数据，并生成策略研究报告",
        file_path="data/stock_price_strategy.csv",
    )
    print(format_workflow_plan(demo_plan))
