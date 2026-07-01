"""
Skill Dispatcher

This module is the first small bridge from Skill routing to execution dispatch.

The router answers: "which high-level Skill does this user request match?"
The dispatcher answers: "does this Skill imply a workflow/tool/RAG execution path?"

Lesson 82 scope:
- Only dispatch Skill -> Workflow.
- Do not take over tool dispatch yet.
- Keep the result as metadata so main.py can attach it into trace.
"""

from __future__ import annotations

from typing import Any, Optional

from skill_registry import get_skill
from workflow_planner import STOCK_STRATEGY_WORKFLOW_NAME


SKILL_WORKFLOW_BINDINGS: dict[str, dict[str, str]] = {
    "stock_strategy_research_workflow": {
        "workflow_name": STOCK_STRATEGY_WORKFLOW_NAME,
        "execution_path": "workflow",
    }
}


def _make_dispatch_result(
    *,
    success: bool,
    dispatch_status: str,
    reason: str,
    skill_name: Optional[str] = None,
    skill_display_name: Optional[str] = None,
    selected_execution_path: Optional[str] = None,
    should_run_workflow: bool = False,
    skill_workflow_name: Optional[str] = None,
    workflow_name: Optional[str] = None,
    file_type_compatible: Optional[bool] = None,
) -> dict[str, Any]:
    """Build a normalized skill dispatch result."""

    return {
        "success": success,
        "dispatch_type": "skill_dispatch",
        "dispatch_status": dispatch_status,
        "selected_execution_path": selected_execution_path,
        "should_run_workflow": should_run_workflow,
        "skill_name": skill_name,
        "skill_display_name": skill_display_name,
        "skill_workflow_name": skill_workflow_name,
        "workflow_name": workflow_name,
        "file_type_compatible": file_type_compatible,
        "reason": reason,
    }


def dispatch_skill(
    *,
    user_input: str,
    skill_route: dict[str, Any],
    current_file_type: Optional[str] = None,
) -> dict[str, Any]:
    """
    Decide whether a matched Skill should dispatch to a higher-level executor.

    Current prototype only supports Skill -> Workflow dispatch. It does not call
    tools directly and does not execute the workflow itself.
    """

    del user_input  # Reserved for future intent refinements in later lessons.

    if not isinstance(skill_route, dict) or not skill_route.get("success"):
        return _make_dispatch_result(
            success=False,
            dispatch_status="no_skill_match",
            reason="Skill Router 未命中 Skill，因此不进行 Skill Dispatch。",
            file_type_compatible=None,
        )

    skill_name = skill_route.get("skill_name")
    skill = skill_route.get("skill") or get_skill(skill_name)

    if not skill:
        return _make_dispatch_result(
            success=False,
            dispatch_status="unknown_skill",
            reason="Skill Router 返回的 Skill 未在 Skill Registry 中找到。",
            skill_name=skill_name,
            file_type_compatible=skill_route.get("file_type_compatible"),
        )

    file_type_compatible = skill_route.get("file_type_compatible")
    if file_type_compatible is False:
        return _make_dispatch_result(
            success=False,
            dispatch_status="blocked_by_file_type",
            reason=(
                "命中的 Skill 与当前文件类型不匹配，暂不进入 workflow；"
                "后续仍可由原有 router 给出错误或 fallback。"
            ),
            skill_name=skill.get("name"),
            skill_display_name=skill.get("display_name"),
            file_type_compatible=file_type_compatible,
        )

    workflows = skill.get("workflows", []) or []
    if not workflows:
        return _make_dispatch_result(
            success=False,
            dispatch_status="no_bound_workflow",
            reason="命中的 Skill 尚未绑定 workflow，保持原有 tool / RAG 路由。",
            skill_name=skill.get("name"),
            skill_display_name=skill.get("display_name"),
            file_type_compatible=file_type_compatible,
        )

    for skill_workflow_name in workflows:
        binding = SKILL_WORKFLOW_BINDINGS.get(skill_workflow_name)
        if not binding:
            continue

        return _make_dispatch_result(
            success=True,
            dispatch_status="workflow_selected",
            selected_execution_path=binding["execution_path"],
            should_run_workflow=True,
            skill_name=skill.get("name"),
            skill_display_name=skill.get("display_name"),
            skill_workflow_name=skill_workflow_name,
            workflow_name=binding["workflow_name"],
            file_type_compatible=file_type_compatible,
            reason=(
                f"Skill {skill.get('name')} 绑定了 {skill_workflow_name}，"
                "因此由 Skill Dispatcher 选择 workflow 执行路径。"
            ),
        )

    return _make_dispatch_result(
        success=False,
        dispatch_status="unsupported_workflow_binding",
        reason="命中的 Skill 绑定了 workflow，但当前 dispatcher 尚不支持这些 workflow。",
        skill_name=skill.get("name"),
        skill_display_name=skill.get("display_name"),
        file_type_compatible=file_type_compatible,
    )
