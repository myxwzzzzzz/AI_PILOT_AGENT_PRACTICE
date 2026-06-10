from file_inspector import detect_file_type
from tool_registry import TOOL_REGISTRY


def get_tool_by_name(tool_name: str) -> dict | None:
    """
    根据工具名称从 Tool Registry 中查找工具。
    """
    for tool in TOOL_REGISTRY:
        if tool["name"] == tool_name:
            return tool

    return None


def validate_tool_arguments(tool_name: str, arguments: dict) -> dict:
    """
    对模拟 LLM 返回的工具参数做基础校验和默认值补全。

    注意：
    - 当前只做项目内已知工具的参数校验；
    - 后续接真实 LLM 时，这一步依然必须保留；
    - 不要完全相信 LLM 返回的 arguments。
    """

    arguments = arguments or {}

    if tool_name in [
        "run_moving_average_backtest",
        "generate_backtest_report",
        "generate_backtest_charts",
    ]:
        short_window = arguments.get("short_window", 3)
        long_window = arguments.get("long_window", 5)

        if not isinstance(short_window, int):
            return {
                "success": False,
                "error": "short_window 必须是整数"
            }

        if not isinstance(long_window, int):
            return {
                "success": False,
                "error": "long_window 必须是整数"
            }

        if short_window <= 0 or long_window <= 0:
            return {
                "success": False,
                "error": "均线窗口必须为正整数"
            }

        if short_window >= long_window:
            return {
                "success": False,
                "error": "短期均线窗口必须小于长期均线窗口"
            }

        return {
            "success": True,
            "arguments": {
                "short_window": short_window,
                "long_window": long_window
            }
        }

    if tool_name in [
        "optimize_moving_average_parameters",
        "generate_parameter_scan_report",
        "generate_parameter_scan_chart",
        "generate_strategy_research_summary",
    ]:
        sort_by = arguments.get("sort_by", "sharpe_ratio")

        allowed_sort_by = [
            "sharpe_ratio",
            "strategy_total_return",
            "excess_return",
            "max_drawdown",
        ]

        if sort_by not in allowed_sort_by:
            return {
                "success": False,
                "error": f"sort_by 不合法：{sort_by}"
            }

        return {
            "success": True,
            "arguments": {
                "sort_by": sort_by
            }
        }

    return {
        "success": True,
        "arguments": {}
    }


def route_llm_tool_call(
    llm_tool_call: dict,
    file_path: str
) -> dict:
    """
    执行模拟 LLM 返回的工具调用结果。

    llm_tool_call 示例：
    {
        "tool_name": "generate_backtest_report",
        "arguments": {
            "short_window": 5,
            "long_window": 10
        }
    }
    """
    tool_name = llm_tool_call.get("tool_name")
    arguments = llm_tool_call.get("arguments", {})

    trace = {
        "router_type": "llm_router",
        "llm_tool_call": llm_tool_call,
        "selected_tool": tool_name,
        "current_file": file_path,
    }

    if not tool_name:
        trace["execution_status"] = "failed"

        return {
            "success": False,
            "error": "LLM 工具调用结果缺少 tool_name",
            "trace": trace
        }

    matched_tool = get_tool_by_name(tool_name)

    if matched_tool is None:
        trace["execution_status"] = "failed"

        return {
            "success": False,
            "error": f"未知工具：{tool_name}",
            "trace": trace
        }

    file_info = detect_file_type(file_path)
    current_file_type = file_info.get("file_type")
    required_file_type = matched_tool.get("required_file_type")

    trace["current_file_type"] = current_file_type
    trace["required_file_type"] = required_file_type

    if required_file_type and current_file_type != required_file_type:
        trace["file_check"] = "failed"
        trace["execution_status"] = "failed"

        return {
            "success": False,
            "error": (
                f"当前文件类型不匹配。当前文件类型为 {file_info.get('file_type_name')}，"
                f"但工具 {tool_name} 需要 {matched_tool.get('required_file_type_name')}。"
            ),
            "selected_tool": tool_name,
            "trace": trace
        }

    trace["file_check"] = "passed"

    argument_validation = validate_tool_arguments(tool_name, arguments)

    if not argument_validation.get("success"):
        trace["argument_validation"] = argument_validation
        trace["execution_status"] = "failed"

        return {
            "success": False,
            "error": argument_validation.get("error"),
            "selected_tool": tool_name,
            "trace": trace
        }

    validated_arguments = argument_validation["arguments"]

    trace["validated_arguments"] = validated_arguments

    try:
        handler = matched_tool["handler"]
        tool_result = handler(file_path, **validated_arguments)

        trace["execution_status"] = "success" if tool_result.get("success") else "failed"

        return {
            "success": tool_result.get("success", False),
            "selected_tool": tool_name,
            "tool_result": tool_result,
            "trace": trace
        }

    except Exception as e:
        trace["execution_status"] = "failed"

        return {
            "success": False,
            "error": str(e),
            "selected_tool": tool_name,
            "trace": trace
        }