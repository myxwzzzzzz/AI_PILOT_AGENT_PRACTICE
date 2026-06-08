from file_inspector import detect_file_type
from parameter_parser import extract_ma_windows, extract_scan_sort_by

from tool_registry import (
    find_matching_tool_with_trace,
    get_tool_by_name
)


def build_file_type_error(
    expected_type_name: str,
    current_type_name: str,
    file_path: str,
    suggestion: str,
    trace: dict | None = None
) -> dict:
    """
    构造文件类型不匹配时的错误信息。
    """
    if trace is None:
        trace = {}

    trace["file_type_check"] = "failed"
    trace["execution_status"] = "blocked_by_file_type_check"

    return {
        "success": False,
        "error": (
            f"当前任务需要使用【{expected_type_name}】，"
            f"但当前文件 {file_path} 被识别为【{current_type_name}】。"
        ),
        "suggestion": suggestion,
        "trace": trace
    }


def get_file_switch_suggestion(required_file_type: str) -> str:
    """
    根据所需文件类型，给出切换文件建议。
    """
    if required_file_type == "channel_data":
        return "请先输入：切换文件 data/channel_data.csv"

    if required_file_type == "stock_price":
        return "请先输入：切换文件 data/stock_price.csv"

    return "请切换到符合该任务要求的数据文件。"


def build_base_trace(
    user_input: str,
    file_path: str,
    file_type: str,
    file_type_name: str
) -> dict:
    """
    构建基础工具调用轨迹。
    """
    return {
        "user_input": user_input,
        "current_file_path": file_path,
        "current_file_type": file_type,
        "current_file_type_name": file_type_name
    }


def execute_tool(
    tool: dict,
    file_path: str,
    file_type: str,
    file_type_name: str,
    trace: dict | None = None,
    tool_params: dict | None = None
) -> dict:
    """
    执行工具前，先检查文件类型是否匹配，并记录工具调用轨迹。
    支持为部分工具传入额外参数。
    """
    if trace is None:
        trace = {}

    if tool_params is None:
        tool_params = {}

    required_file_type = tool.get("required_file_type")
    required_file_type_name = tool.get("required_file_type_name")

    trace["selected_tool"] = tool["name"]
    trace["tool_description"] = tool["description"]
    trace["required_file_type"] = required_file_type
    trace["required_file_type_name"] = required_file_type_name
    trace["tool_params"] = tool_params

    if required_file_type is not None and required_file_type != file_type:
        return build_file_type_error(
            expected_type_name=required_file_type_name or "指定类型数据",
            current_type_name=file_type_name,
            file_path=file_path,
            suggestion=get_file_switch_suggestion(required_file_type),
            trace=trace
        )

    trace["file_type_check"] = "passed"

    handler = tool["handler"]

    try:
        tool_result = handler(file_path, **tool_params)

        trace["execution_status"] = "success" if tool_result.get("success") else "tool_failed"
        trace["tool_success"] = tool_result.get("success")
        trace["tool_error"] = tool_result.get("error")

        return {
            "success": True,
            "selected_tool": tool["name"],
            "tool_description": tool["description"],
            "required_file_type": required_file_type,
            "tool_params": tool_params,
            "tool_result": tool_result,
            "trace": trace
        }

    except Exception as e:
        trace["execution_status"] = "exception"
        trace["tool_success"] = False
        trace["tool_error"] = str(e)

        return {
            "success": True,
            "selected_tool": tool["name"],
            "tool_description": tool["description"],
            "required_file_type": required_file_type,
            "tool_params": tool_params,
            "tool_result": {
                "success": False,
                "error": str(e)
            },
            "trace": trace
        }


def route_auto_report(
    user_input: str,
    file_path: str,
    file_type: str,
    file_type_name: str,
    base_trace: dict
) -> dict:
    """
    当用户只说“生成报告”时，根据当前文件类型自动选择报告工具。
    """
    trace = base_trace.copy()
    trace["match_type"] = "auto_report_by_file_type"
    trace["matched_keywords"] = ["报告"]
    trace["selection_reason"] = "用户提出泛化报告需求，系统根据当前文件类型自动选择报告工具。"

    if file_type == "channel_data":
        tool = get_tool_by_name("generate_channel_analysis_report")
        return execute_tool(tool, file_path, file_type, file_type_name, trace)

    if file_type == "stock_price":
        tool = get_tool_by_name("generate_stock_metrics_report")
        return execute_tool(tool, file_path, file_type, file_type_name, trace)

    trace["execution_status"] = "no_suitable_report_tool"

    return {
        "success": False,
        "error": f"当前文件类型为【{file_type_name}】，暂时无法自动选择报告工具。",
        "suggestion": "请使用渠道转化数据文件或股票价格数据文件。",
        "trace": trace
    }


def route_task(user_input: str, file_path: str) -> dict:
    """
    根据用户输入，选择合适的工具执行任务。

    当前版本使用 Tool Registry 工具注册表管理工具，
    支持工具调用轨迹 trace，
    并支持均线回测类工具的参数解析。
    """
    user_input = user_input.strip()

    if not user_input:
        return {
            "success": False,
            "error": "用户输入不能为空",
            "trace": {
                "user_input": user_input,
                "execution_status": "empty_input"
            }
        }

    file_info = detect_file_type(file_path)

    if not file_info.get("success"):
        return {
            "success": False,
            "error": file_info.get("error", "文件类型识别失败"),
            "trace": {
                "user_input": user_input,
                "current_file_path": file_path,
                "execution_status": "file_inspection_failed"
            }
        }

    file_type = file_info.get("file_type")
    file_type_name = file_info.get("file_type_name")

    base_trace = build_base_trace(
        user_input=user_input,
        file_path=file_path,
        file_type=file_type,
        file_type_name=file_type_name
    )

    # 1. 先尝试从 Tool Registry 精确匹配工具
    # 这样“生成 MA5-MA10 回测报告”会优先匹配 generate_backtest_report，
    # 不会被泛化“报告”逻辑提前截走。
    matched_tool, match_trace = find_matching_tool_with_trace(user_input)

    trace = base_trace.copy()
    trace.update(match_trace)

    if matched_tool is not None:
        trace["selection_reason"] = (
            f"用户输入命中了关键词 {match_trace.get('matched_keywords')}，"
            f"因此选择工具 {matched_tool['name']}。"
        )

        tool_params = {}

        # 对均线回测类工具，尝试从用户输入中提取 MA 参数
        if matched_tool["name"] in [
            "run_moving_average_backtest",
            "generate_backtest_report"
        ]:
            ma_params = extract_ma_windows(user_input)

            if not ma_params.get("success"):
                trace["execution_status"] = "parameter_parse_failed"
                trace["parameter_error"] = ma_params.get("error")

                return {
                    "success": False,
                    "error": ma_params.get("error", "均线参数解析失败"),
                    "suggestion": "请尝试输入：运行 MA5-MA10 回测，或生成 MA5-MA10 回测报告。",
                    "trace": trace
                }

            tool_params = {
                "short_window": ma_params["short_window"],
                "long_window": ma_params["long_window"]
            }

            trace["parameter_parse"] = {
                "source": ma_params.get("source"),
                "short_window": ma_params["short_window"],
                "long_window": ma_params["long_window"],
                "message": ma_params.get("message")
            }
        
        # 对参数扫描类工具，尝试从用户输入中提取排序指标
        if matched_tool["name"] in [
            "optimize_moving_average_parameters",
            "generate_parameter_scan_report"
            "generate_strategy_research_summary"
        ]:
             sort_params = extract_scan_sort_by(user_input)

             if not sort_params.get("success"):
                trace["execution_status"] = "parameter_parse_failed"
                trace["parameter_error"] = sort_params.get("error")

                return{
                    "success": False,
                    "error": sort_params.get("error", "排序指标解析失败"),
                    "suggestion": "请尝试输入：按夏普比率扫描均线参数，或按收益率生成参数扫描报告。",
                    "trace": trace
                }
             
             tool_params["sort_by"] = sort_params["sort_by"]

             trace["scan_sort_parse"]={
                "source": sort_params.get("source"),
                "sort_by": sort_params["sort_by"],
                "sort_by_name": sort_params["sort_by_name"],
                "message": sort_params.get("message")
             }


        return execute_tool(
            tool=matched_tool,
            file_path=file_path,
            file_type=file_type,
            file_type_name=file_type_name,
            trace=trace,
            tool_params=tool_params
        )

    # 2. 如果没有匹配到具体工具，再处理泛化报告需求
    if any(keyword in user_input for keyword in ["生成一份报告", "生成报告", "分析报告", "报告"]):
        return route_auto_report(
            user_input=user_input,
            file_path=file_path,
            file_type=file_type,
            file_type_name=file_type_name,
            base_trace=base_trace
        )

    trace["execution_status"] = "no_matching_tool"
    trace["selection_reason"] = "用户输入没有命中任何已注册工具的关键词。"

    return {
        "success": False,
        "error": "暂时无法识别该任务类型",
        "suggestion": (
            "你可以尝试输入：读取数据、查看统计信息、分析渠道转化率、"
            "生成渠道分析报告、分析风险收益、生成金融指标报告、查看工具"
        ),
        "trace": trace
    }