"""
Skill Registry

This module defines high-level reusable capabilities for the AI Pilot Agent project.

A skill is not a single tool. It is a capability package that groups related tools,
workflows, documents, examples, and file requirements around a business goal.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional


SKILL_REGISTRY: list[dict[str, Any]] = [
    {
        "name": "channel_analysis_skill",
        "display_name": "渠道转化分析 Skill",
        "description": "用于分析渠道访问、注册、支付转化表现，并生成渠道分析报告。",
        "required_file_type": "channel_data",
        "tools": [
            "read_csv_file",
            "show_columns",
            "check_missing_values",
            "show_basic_statistics",
            "analyze_channel_conversion",
            "find_best_channel",
            "generate_channel_report",
        ],
        "workflows": [],
        "documents": [],
        "example_queries": [
            "分析渠道转化率",
            "哪个渠道表现最好？",
            "生成渠道分析报告",
        ],
    },
    {
        "name": "stock_metrics_skill",
        "display_name": "股票风险收益分析 Skill",
        "description": "用于读取股票价格数据，计算收益率、波动率、最大回撤和夏普比率，并生成指标报告。",
        "required_file_type": "stock_price",
        "tools": [
            "read_stock_price_data",
            "calculate_stock_metrics",
            "generate_stock_metrics_report",
        ],
        "workflows": [],
        "documents": [
            "risk_metrics_notes.md",
        ],
        "example_queries": [
            "分析风险收益",
            "计算最大回撤",
            "生成金融指标报告",
        ],
    },
    {
        "name": "ma_strategy_backtest_skill",
        "display_name": "均线策略回测 Skill",
        "description": "用于执行 MA 短长均线策略回测，并生成回测报告和图表。",
        "required_file_type": "stock_price",
        "tools": [
            "run_moving_average_backtest",
            "generate_backtest_report",
            "generate_backtest_chart",
        ],
        "workflows": [],
        "documents": [
            "ma_strategy_notes.md",
            "risk_metrics_notes.md",
        ],
        "example_queries": [
            "运行 MA5-MA10 回测",
            "生成 MA5-MA10 回测报告",
            "生成 MA5-MA10 回测图表",
        ],
    },
    {
        "name": "stock_strategy_research_skill",
        "display_name": "股票策略研究 Skill",
        "description": "用于对股票价格数据执行完整风险收益分析、均线参数扫描、图表生成和策略研究总结。",
        "required_file_type": "stock_price",
        "tools": [
            "read_stock_price_data",
            "calculate_stock_metrics",
            "generate_stock_metrics_report",
            "optimize_moving_average_parameters",
            "generate_parameter_scan_report",
            "generate_parameter_scan_chart",
            "generate_strategy_research_summary",
        ],
        "workflows": [
            "stock_strategy_research_workflow",
        ],
        "documents": [
            "ma_strategy_notes.md",
            "risk_metrics_notes.md",
            "agent_tool_usage_notes.md",
            "rag_qa_examples.md",
        ],
        "example_queries": [
            "完整分析股票数据，并按夏普比率生成策略研究报告",
            "帮我做一次完整的均线策略研究",
            "按最大回撤生成完整策略研究报告",
        ],
    },
    {
        "name": "rag_qa_skill",
        "display_name": "RAG 知识问答 Skill",
        "description": "用于基于本地 documents 知识库回答策略、指标和工具使用相关问题。",
        "required_file_type": None,
        "tools": [],
        "workflows": [],
        "documents": [
            "ma_strategy_notes.md",
            "risk_metrics_notes.md",
            "agent_tool_usage_notes.md",
            "rag_qa_examples.md",
        ],
        "example_queries": [
            "最大回撤是什么意思？",
            "夏普比率高说明什么？",
            "MA5-MA10 策略适合震荡行情吗？",
            "如果用户问最大回撤，sort_by 应该是什么？",
        ],
    },
]


def list_skills() -> list[dict[str, Any]]:
    """Return all registered skills.

    A deep copy is returned to prevent callers from mutating the registry.
    """

    return deepcopy(SKILL_REGISTRY)


def get_skill(skill_name: str) -> Optional[dict[str, Any]]:
    """Return a skill by name, or None when it is not registered."""

    for skill in SKILL_REGISTRY:
        if skill["name"] == skill_name:
            return deepcopy(skill)
    return None


def get_skills_for_file_type(file_type: Optional[str]) -> list[dict[str, Any]]:
    """Return skills that can work with the given file type.

    Skills whose required_file_type is None are considered file-independent.
    """

    matched: list[dict[str, Any]] = []

    for skill in SKILL_REGISTRY:
        required_file_type = skill.get("required_file_type")
        if required_file_type is None or required_file_type == file_type:
            matched.append(deepcopy(skill))

    return matched


def format_skill_list(skills: Optional[list[dict[str, Any]]] = None) -> str:
    """Format skills into a CLI-friendly text block."""

    skills_to_format = skills if skills is not None else list_skills()

    if not skills_to_format:
        return "当前没有已注册 Skill。"

    lines = ["已注册 Skill："]

    for index, skill in enumerate(skills_to_format, start=1):
        required_file_type = skill.get("required_file_type") or "不限"
        tools = skill.get("tools", [])
        workflows = skill.get("workflows", [])
        documents = skill.get("documents", [])

        lines.extend(
            [
                f"{index}. {skill['display_name']} ({skill['name']})",
                f"   描述：{skill['description']}",
                f"   适用文件类型：{required_file_type}",
                f"   工具数：{len(tools)}",
                f"   Workflow 数：{len(workflows)}",
                f"   关联文档数：{len(documents)}",
            ]
        )

        examples = skill.get("example_queries", [])
        if examples:
            lines.append(f"   示例：{examples[0]}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(format_skill_list())
