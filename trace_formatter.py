def format_trace(route_result: dict) -> str:
    """
    将工具调用轨迹格式化为可读文本。
    """
    trace = route_result.get("trace")

    if not trace:
        return "暂无工具调用轨迹。"

    lines = []
    lines.append("工具调用轨迹：")

    user_input = trace.get("user_input")
    if user_input is not None:
        lines.append(f"- 用户输入：{user_input}")

    match_type = trace.get("match_type")
    if match_type:
        lines.append(f"- 匹配方式：{translate_match_type(match_type)}")

    matched_keywords = trace.get("matched_keywords")
    if matched_keywords:
        lines.append(f"- 命中关键词：{', '.join(matched_keywords)}")

    selection_reason = trace.get("selection_reason")
    if selection_reason:
        lines.append(f"- 选择原因：{selection_reason}")

    selected_tool = trace.get("selected_tool")
    if selected_tool:
        lines.append(f"- 选择工具：{selected_tool}")

    tool_description = trace.get("tool_description")
    if tool_description:
        lines.append(f"- 工具用途：{tool_description}")

    current_file_path = trace.get("current_file_path")
    if current_file_path:
        lines.append(f"- 当前文件：{current_file_path}")

    current_file_type_name = trace.get("current_file_type_name")
    if current_file_type_name:
        lines.append(f"- 当前文件类型：{current_file_type_name}")

    required_file_type_name = trace.get("required_file_type_name")
    if required_file_type_name:
        lines.append(f"- 工具要求文件类型：{required_file_type_name}")

    parameter_parse = trace.get("parameter_parse") 
    if isinstance(parameter_parse, dict):
      lines.append(
        f"- 参数解析：短期均线={parameter_parse.get('short_window')}，"
        f"长期均线={parameter_parse.get('long_window')}，"
        f"来源={parameter_parse.get('source')}"
    )

      if parameter_parse.get("message"):
          lines.append(f"- 参数说明：{parameter_parse.get('message')}")
    
    scan_sort_parse = trace.get("scan_sort_parse")
    if isinstance(scan_sort_parse, dict):
        lines.append(
            f"- 扫描排序解析：排序字段={scan_sort_parse.get('sort_by')}，"
            f"排序指标={scan_sort_parse.get('sort_by_name')}，"
            f"来源={scan_sort_parse.get('source')}"
        )

        if scan_sort_parse.get("message"):
            lines.append(f"- 排序说明：{scan_sort_parse.get('message')}")

    tool_params = trace.get("tool_params")
    if isinstance(tool_params, dict) and tool_params:
        lines.append(f"- 实际传入参数：{tool_params}")

    file_type_check = trace.get("file_type_check")
    if file_type_check:
        lines.append(f"- 文件类型校验：{translate_file_type_check(file_type_check)}")

    execution_status = trace.get("execution_status")
    if execution_status:
        lines.append(f"- 工具执行状态：{translate_execution_status(execution_status)}")

    tool_error = trace.get("tool_error")
    if tool_error:
        lines.append(f"- 工具错误信息：{tool_error}")

    return "\n".join(lines)


def translate_match_type(match_type: str) -> str:
    """
    翻译匹配方式。
    """
    mapping = {
        "keyword": "关键词匹配",
        "no_match": "未匹配到工具",
        "auto_report_by_file_type": "根据当前文件类型自动选择报告工具"
    }
    return mapping.get(match_type, match_type)


def translate_file_type_check(check_result: str) -> str:
    """
    翻译文件类型校验结果。
    """
    mapping = {
        "passed": "通过",
        "failed": "未通过"
    }
    return mapping.get(check_result, check_result)


def translate_execution_status(status: str) -> str:
    """
    翻译工具执行状态。
    """
    mapping = {
        "success": "成功",
        "tool_failed": "工具返回失败",
        "exception": "工具执行异常",
        "blocked_by_file_type_check": "因文件类型不匹配被拦截",
        "no_matching_tool": "没有匹配到工具",
        "empty_input": "用户输入为空",
        "file_inspection_failed": "文件类型识别失败",
        "no_suitable_report_tool": "没有合适的报告工具",
        "parameter_parse_failed": "参数解析失败"
    }
    return mapping.get(status, status)