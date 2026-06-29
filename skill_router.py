"""
Skill Router

This module routes a user request to a high-level Skill.

The skill router works above the tool router:
- router.py / llm_router.py select concrete tools.
- skill_router.py selects the broader capability area first.

Current implementation is rule-based and deterministic. It does not call an LLM.
"""

from __future__ import annotations

from typing import Any, Optional

from skill_registry import get_skill, list_skills


KNOWLEDGE_QA_KEYWORDS = [
    "是什么",
    "什么意思",
    "说明什么",
    "适合",
    "为什么",
    "怎么理解",
    "区别",
    "原理",
    "概念",
    "sort_by",
    "应该是什么",
]

CHANNEL_KEYWORDS = [
    "渠道",
    "转化",
    "注册",
    "支付",
    "访问",
    "表现最好",
    "channel",
    "conversion",
]

STOCK_METRICS_KEYWORDS = [
    "风险收益",
    "最大回撤",
    "夏普",
    "波动率",
    "收益率",
    "金融指标",
    "stock metrics",
    "drawdown",
    "sharpe",
]

MA_BACKTEST_KEYWORDS = [
    "ma",
    "均线",
    "回测",
    "短均线",
    "长均线",
    "ma5",
    "ma10",
    "backtest",
]

STOCK_RESEARCH_WORKFLOW_KEYWORDS = [
    "完整分析",
    "综合分析",
    "全流程",
    "策略研究",
    "完整策略",
    "研究报告",
    "完整报告",
    "完整的均线策略研究",
]


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _find_matches(text: str, keywords: list[str]) -> list[str]:
    normalized = _normalize_text(text)
    return [keyword for keyword in keywords if keyword.lower() in normalized]


def _is_file_type_compatible(skill: dict[str, Any], current_file_type: Optional[str]) -> bool:
    required_file_type = skill.get("required_file_type")

    if required_file_type is None:
        return True

    if current_file_type is None:
        return True

    return required_file_type == current_file_type


def _make_route_result(
    *,
    success: bool,
    skill_name: Optional[str],
    confidence: float,
    reason: str,
    matched_keywords: Optional[list[str]] = None,
    current_file_type: Optional[str] = None,
) -> dict[str, Any]:
    skill = get_skill(skill_name) if skill_name else None

    return {
        "success": success,
        "route_type": "skill_route",
        "skill_name": skill_name,
        "skill_display_name": skill.get("display_name") if skill else None,
        "confidence": confidence,
        "reason": reason,
        "matched_keywords": matched_keywords or [],
        "current_file_type": current_file_type,
        "required_file_type": skill.get("required_file_type") if skill else None,
        "file_type_compatible": _is_file_type_compatible(skill, current_file_type) if skill else None,
        "skill": skill,
    }


def route_skill(user_input: str, current_file_type: Optional[str] = None) -> dict[str, Any]:
    """Route user input to a registered skill.

    The router intentionally stays conservative:
    - It returns no match when the intent is unclear.
    - It prioritizes knowledge QA patterns before execution skills.
    - It includes file type compatibility metadata, but does not execute anything.
    """

    normalized = _normalize_text(user_input)

    if not normalized:
        return _make_route_result(
            success=False,
            skill_name=None,
            confidence=0.0,
            reason="用户输入为空，无法判断 Skill。",
            current_file_type=current_file_type,
        )

    knowledge_matches = _find_matches(user_input, KNOWLEDGE_QA_KEYWORDS)
    metrics_matches = _find_matches(user_input, STOCK_METRICS_KEYWORDS)
    ma_matches = _find_matches(user_input, MA_BACKTEST_KEYWORDS)

    # Knowledge QA should win when the user is asking for concepts, definitions,
    # suitability, or tool-usage knowledge rather than asking to execute a tool.
    if knowledge_matches and (metrics_matches or ma_matches or "策略" in normalized or "工具" in normalized):
        return _make_route_result(
            success=True,
            skill_name="rag_qa_skill",
            confidence=0.92,
            reason="用户问题更像知识问答，需要基于本地文档进行解释。",
            matched_keywords=knowledge_matches + metrics_matches + ma_matches,
            current_file_type=current_file_type,
        )

    workflow_matches = _find_matches(user_input, STOCK_RESEARCH_WORKFLOW_KEYWORDS)
    if workflow_matches:
        return _make_route_result(
            success=True,
            skill_name="stock_strategy_research_skill",
            confidence=0.95,
            reason="用户请求完整股票策略研究，适合使用股票策略研究 Skill。",
            matched_keywords=workflow_matches,
            current_file_type=current_file_type,
        )

    channel_matches = _find_matches(user_input, CHANNEL_KEYWORDS)
    if channel_matches:
        return _make_route_result(
            success=True,
            skill_name="channel_analysis_skill",
            confidence=0.9,
            reason="用户请求渠道转化或渠道表现分析，适合使用渠道转化分析 Skill。",
            matched_keywords=channel_matches,
            current_file_type=current_file_type,
        )

    # MA backtest is more specific than general stock metrics, so route it first.
    if ma_matches:
        return _make_route_result(
            success=True,
            skill_name="ma_strategy_backtest_skill",
            confidence=0.88,
            reason="用户请求均线策略回测或图表报告，适合使用均线策略回测 Skill。",
            matched_keywords=ma_matches,
            current_file_type=current_file_type,
        )

    if metrics_matches:
        return _make_route_result(
            success=True,
            skill_name="stock_metrics_skill",
            confidence=0.86,
            reason="用户请求股票风险收益或金融指标分析，适合使用股票风险收益分析 Skill。",
            matched_keywords=metrics_matches,
            current_file_type=current_file_type,
        )

    # Pure knowledge questions without a finance keyword can still go to RAG QA
    # when the user asks in an explanatory form.
    if knowledge_matches:
        return _make_route_result(
            success=True,
            skill_name="rag_qa_skill",
            confidence=0.75,
            reason="用户输入呈现知识问答形式，优先使用 RAG 知识问答 Skill。",
            matched_keywords=knowledge_matches,
            current_file_type=current_file_type,
        )

    return _make_route_result(
        success=False,
        skill_name=None,
        confidence=0.0,
        reason="未匹配到明确 Skill，后续可交给工具路由或 LLM selector 处理。",
        current_file_type=current_file_type,
    )


def format_skill_route(route_result: dict[str, Any]) -> str:
    """Format a skill route result for CLI or trace display."""

    if not route_result.get("success"):
        return f"Skill 路由结果：未命中\n原因：{route_result.get('reason', '')}"

    lines = [
        f"Skill 路由结果：{route_result['skill_display_name']} ({route_result['skill_name']})",
        f"置信度：{route_result['confidence']:.2f}",
        f"原因：{route_result['reason']}",
    ]

    matched_keywords = route_result.get("matched_keywords") or []
    if matched_keywords:
        lines.append(f"命中关键词：{', '.join(matched_keywords)}")

    required_file_type = route_result.get("required_file_type") or "不限"
    current_file_type = route_result.get("current_file_type") or "未知"
    file_type_compatible = route_result.get("file_type_compatible")

    lines.append(f"适用文件类型：{required_file_type}")
    lines.append(f"当前文件类型：{current_file_type}")
    lines.append(f"文件类型是否匹配：{'是' if file_type_compatible else '否'}")

    return "\n".join(lines)


if __name__ == "__main__":
    examples = [
        "完整分析股票数据，并按夏普比率生成策略研究报告",
        "最大回撤是什么意思？",
        "哪个渠道表现最好？",
        "运行 MA5-MA10 回测",
    ]

    for example in examples:
        print("=" * 60)
        print(example)
        print(format_skill_route(route_skill(example, current_file_type="stock_price")))
