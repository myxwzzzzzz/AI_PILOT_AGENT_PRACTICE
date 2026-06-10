from tool_registry import TOOL_REGISTRY


def get_tool_parameter_schema(tool_name: str) -> dict:
    """
    根据工具名称返回该工具需要暴露给 LLM 的参数 schema。

    当前版本不绑定任何具体大模型 API，只使用通用 JSON Schema 风格。
    """

    # 均线回测类工具：需要 short_window / long_window
    if tool_name in [
        "run_moving_average_backtest",
        "generate_backtest_report",
        "generate_backtest_charts",
    ]:
        return {
            "type": "object",
            "properties": {
                "short_window": {
                    "type": "integer",
                    "description": "短期均线窗口，例如 MA5-MA10 中的 5。",
                    "default": 3,
                    "minimum": 1,
                },
                "long_window": {
                    "type": "integer",
                    "description": "长期均线窗口，例如 MA5-MA10 中的 10。",
                    "default": 5,
                    "minimum": 2,
                },
            },
            "required": [],
        }

    # 参数扫描类工具：需要 sort_by
    if tool_name in [
        "optimize_moving_average_parameters",
        "generate_parameter_scan_report",
        "generate_parameter_scan_chart",
        "generate_strategy_research_summary",
    ]:
        return {
            "type": "object",
            "properties": {
                "sort_by": {
                    "type": "string",
                    "description": "参数扫描排序指标。",
                    "enum": [
                        "sharpe_ratio",
                        "strategy_total_return",
                        "excess_return",
                        "max_drawdown",
                    ],
                    "default": "sharpe_ratio",
                }
            },
            "required": [],
        }

    # 其他工具暂时不需要额外参数
    return {
        "type": "object",
        "properties": {},
        "required": [],
    }


def build_llm_tool_schema(tool: dict) -> dict:
    """
    将 Tool Registry 中的单个工具转换为 LLM 可读工具 schema。
    """
    tool_name = tool["name"]

    return {
        "name": tool_name,
        "description": tool.get("description", ""),
        "required_file_type": tool.get("required_file_type"),
        "required_file_type_name": tool.get("required_file_type_name"),
        "parameters": get_tool_parameter_schema(tool_name),
    }


def build_all_llm_tool_schemas() -> list[dict]:
    """
    将全部工具注册表转换为 LLM 可读工具 schema 列表。
    """
    return [
        build_llm_tool_schema(tool)
        for tool in TOOL_REGISTRY
    ]


def get_llm_tool_schema_by_name(tool_name: str) -> dict | None:
    """
    根据工具名称获取单个 LLM tool schema。
    """
    for tool in TOOL_REGISTRY:
        if tool["name"] == tool_name:
            return build_llm_tool_schema(tool)

    return None