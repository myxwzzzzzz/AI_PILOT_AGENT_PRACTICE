"""
Workflow final summary generator.

This module adds an optional LLM-powered natural-language summary layer on top
of workflow execution results. It is intentionally safe by default:
- If DeepSeek is unavailable, it falls back to a local rule-based summary.
- It does not execute tools.
- It only reads completed workflow result metadata, judgement, and generated files.
"""

from __future__ import annotations

import os
import time
from typing import Any


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"


def _safe_text(value: Any, default: str = "未提供") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _format_bullets(items: list[Any], limit: int = 5) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {_safe_text(item)}" for item in items[:limit])


def _get_user_input(workflow_result: dict[str, Any]) -> str:
    plan = workflow_result.get("plan") or {}
    trace = plan.get("trace") or {}
    return trace.get("user_input") or "未记录"


def build_workflow_llm_summary_prompt(workflow_result: dict[str, Any]) -> str:
    """
    Build a compact prompt for DeepSeek to summarize one workflow execution.

    The prompt only provides structured workflow metadata and asks for a concise
    Chinese summary. It does not ask the LLM to call tools or invent metrics.
    """
    summary = workflow_result.get("workflow_summary") or {}
    judgement = workflow_result.get("workflow_judgement") or {}
    generated_files = workflow_result.get("generated_files") or []

    step_lines: list[str] = []
    for step in workflow_result.get("step_results", []) or []:
        status = "成功" if step.get("success") else "失败"
        step_lines.append(
            f"- 第{step.get('step_index')}步：{status}，"
            f"工具={step.get('tool_name')}，说明={step.get('description')}"
        )

    prompt = f"""
你是一个 AI Pilot Agent 的 workflow 结果总结助手。

请根据下面的 workflow 执行信息，生成一段简洁、客观、中文的最终总结。

严格要求：
1. 只能基于给定的 workflow 结果、规则判断和生成文件总结；
2. 不要编造没有出现的具体收益数字；
3. 不要调用工具；
4. 不要输出 JSON；
5. 输出结构建议包含：任务完成情况、核心判断、风险提示、建议查看的文件。

用户请求：{_get_user_input(workflow_result)}
Workflow 名称：{workflow_result.get('workflow_display_name') or workflow_result.get('workflow_name')}
执行状态：{'成功' if workflow_result.get('success') else '失败'}
排序指标：{summary.get('sort_by_name') or summary.get('sort_by') or '未指定'}
计划步骤数：{summary.get('planned_step_count')}
成功步骤数：{summary.get('successful_step_count')}
失败步骤数：{summary.get('failed_step_count')}

规则判断：
- 综合判断：{judgement.get('overall_label', '未生成')}
- 风险等级：{judgement.get('risk_level', 'unknown')}
- 策略质量：{judgement.get('quality_level', 'unknown')}
- 超额收益判断：{judgement.get('excess_return_level', 'unknown')}

主要发现：
{_format_bullets(judgement.get('findings', []))}

风险提示：
{_format_bullets(judgement.get('warnings', []))}

后续建议：
{_format_bullets(judgement.get('suggestions', []))}

执行步骤：
{chr(10).join(step_lines) if step_lines else '- 无'}

生成文件：
{_format_bullets(generated_files, limit=8)}

请生成最终中文总结。
"""
    return prompt.strip()


def generate_local_workflow_summary(workflow_result: dict[str, Any]) -> str:
    """
    Generate a deterministic local summary for workflow results.

    This is the fallback summary used when LLM is unavailable. It keeps the
    project runnable without API key or network access.
    """
    summary = workflow_result.get("workflow_summary") or {}
    judgement = workflow_result.get("workflow_judgement") or {}
    generated_files = workflow_result.get("generated_files") or []

    status_text = "成功" if workflow_result.get("success") else "失败"
    workflow_name = workflow_result.get("workflow_display_name") or workflow_result.get("workflow_name") or "Workflow"
    sort_by = summary.get("sort_by_name") or summary.get("sort_by") or "未指定"

    lines = [
        f"本次 {workflow_name} 执行状态为{status_text}。",
        (
            f"系统计划执行 {summary.get('planned_step_count', 0)} 步，"
            f"实际执行 {summary.get('executed_step_count', 0)} 步，"
            f"成功 {summary.get('successful_step_count', 0)} 步，"
            f"失败 {summary.get('failed_step_count', 0)} 步。"
        ),
        f"本次排序指标为：{sort_by}。",
    ]

    if judgement.get("success"):
        lines.append(
            "规则判断结果："
            f"{judgement.get('overall_label')}；"
            f"风险等级为 {judgement.get('risk_level')}；"
            f"策略质量为 {judgement.get('quality_level')}；"
            f"超额收益判断为 {judgement.get('excess_return_level')}。"
        )
        warnings = judgement.get("warnings") or []
        if warnings:
            lines.append(f"主要风险提示：{warnings[0]}")
        suggestions = judgement.get("suggestions") or []
        if suggestions:
            lines.append(f"后续建议：{suggestions[0]}")
    else:
        lines.append("当前未生成完整规则判断，建议先检查 workflow 执行步骤和输出文件。")

    if generated_files:
        lines.append(f"本次共生成 {len(generated_files)} 个文件，建议优先查看 workflow 总结报告和策略研究总结报告。")
    else:
        lines.append("本次没有记录到生成文件。")

    return "\n".join(lines)


def generate_workflow_final_summary(
    workflow_result: dict[str, Any],
    *,
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    Generate final natural-language summary for a workflow result.

    DeepSeek is optional. If API key, SDK, network, or model call fails, this
    function returns a local fallback summary instead of failing the workflow.
    """
    if not workflow_result.get("is_workflow"):
        return {
            "success": False,
            "summary_source": "skipped",
            "summary_text": "当前结果不是 workflow 结果，未生成总结。",
        }

    local_summary = generate_local_workflow_summary(workflow_result)

    if not use_llm:
        return {
            "success": True,
            "summary_source": "local",
            "provider": "local_rules",
            "model": None,
            "summary_text": local_summary,
        }

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {
            "success": True,
            "summary_source": "local_fallback",
            "provider": "local_rules",
            "model": None,
            "fallback_reason": "未检测到 DEEPSEEK_API_KEY，使用本地规则总结。",
            "summary_text": local_summary,
        }

    start_time = time.perf_counter()
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL,
            timeout=30.0,
        )
        prompt = build_workflow_llm_summary_prompt(workflow_result)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严谨的 workflow 执行结果总结助手。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=800,
        )
        summary_text = response.choices[0].message.content.strip()
        return {
            "success": True,
            "summary_source": "llm",
            "provider": "deepseek",
            "model": DEEPSEEK_MODEL,
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
            "summary_text": summary_text,
        }
    except Exception as exc:  # pragma: no cover - defensive fallback
        return {
            "success": True,
            "summary_source": "local_fallback",
            "provider": "local_rules",
            "model": None,
            "fallback_reason": f"调用 DeepSeek 生成 workflow 总结失败：{exc}",
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
            "summary_text": local_summary,
        }
