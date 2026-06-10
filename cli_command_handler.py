from dataclasses import dataclass
from pathlib import Path

from cli_state import AppState
from file_inspector import detect_file_type
from tool_registry import TOOL_REGISTRY
from llm_health_check import (
    check_deepseek_connection,
    format_llm_health_check_result,
)


@dataclass
class CommandResult:
    """
    系统命令处理结果。
    """
    handled: bool
    should_exit: bool = False
    message: str = ""


def format_current_file_info(file_path: str) -> str:
    """
    格式化当前文件信息。
    """
    file_info = detect_file_type(file_path)

    return (
        f"当前文件：{file_path}\n"
        f"当前文件类型：{file_info.get('file_type_name')}；"
        f"字段：{', '.join(file_info.get('columns', []))}"
    )


def format_tool_list() -> str:
    """
    格式化当前 Tool Registry 中的工具列表。
    """
    lines = []
    lines.append("当前已注册工具：")

    for index, tool in enumerate(TOOL_REGISTRY, start=1):
        lines.append(
            f"{index}. {tool.get('name')}：{tool.get('description', '')}"
        )

    return "\n".join(lines)


def read_recent_logs(log_path: str = "data/logs/tool_calls.jsonl", limit: int = 5) -> str:
    """
    读取最近几条工具调用日志。
    """
    path = Path(log_path)

    if not path.exists():
        return "暂无工具调用日志。"

    lines = path.read_text(encoding="utf-8").splitlines()

    if not lines:
        return "暂无工具调用日志。"

    recent_lines = lines[-limit:]

    return "最近工具调用日志：\n" + "\n".join(recent_lines)


def handle_cli_command(user_input: str, state: AppState) -> CommandResult:
    """
    处理不需要进入 Agent 执行链路的系统命令。

    例如：
    - 退出
    - 切换文件
    - 开启/关闭 LLM 模式
    - 使用真实/模拟 LLM
    - 开启/关闭 RAG 模式
    - 开启/关闭 trace
    - 查看工具
    - 检查 LLM 连接
    """
    text = user_input.strip()

    if text in ["exit", "quit", "退出"]:
        return CommandResult(
            handled=True,
            should_exit=True,
            message="程序已退出。"
        )

    if text.startswith("切换文件"):
        file_path = text.replace("切换文件", "", 1).strip()

        if not file_path:
            return CommandResult(
                handled=True,
                message="请在“切换文件”后面提供文件路径，例如：切换文件 data/stock_price_strategy.csv"
            )

        if not Path(file_path).exists():
            return CommandResult(
                handled=True,
                message=f"文件不存在：{file_path}"
            )

        state.current_file_path = file_path
        file_info = detect_file_type(file_path)

        return CommandResult(
            handled=True,
            message=(
                f"已切换当前数据文件为：{file_path}\n"
                f"当前文件类型：{file_info.get('file_type_name')}；"
                f"字段：{', '.join(file_info.get('columns', []))}"
            )
        )

    if text in ["查看当前状态", "当前状态", "状态"]:
        return CommandResult(
            handled=True,
            message=(
                f"{format_current_file_info(state.current_file_path)}\n"
                f"LLM 模式：{state.use_llm_mode}\n"
                f"LLM Selector：{state.llm_selector_mode}\n"
                f"RAG 模式：{state.use_rag_mode}\n"
                f"Trace 显示：{state.show_trace}"
            )
        )

    if text in ["开启轨迹", "查看轨迹", "打开轨迹"]:
        state.show_trace = True
        return CommandResult(
            handled=True,
            message="已开启工具调用轨迹显示。"
        )

    if text in ["关闭轨迹", "隐藏轨迹"]:
        state.show_trace = False
        return CommandResult(
            handled=True,
            message="已关闭工具调用轨迹显示。"
        )

    if text in ["开启LLM模式", "开启 LLM 模式", "打开LLM模式", "打开 LLM 模式"]:
        state.use_llm_mode = True
        return CommandResult(
            handled=True,
            message="已开启 LLM 模式。后续任务将走 LLM Agent Runner。"
        )

    if text in ["关闭LLM模式", "关闭 LLM 模式", "退出LLM模式", "退出 LLM 模式"]:
        state.use_llm_mode = False
        return CommandResult(
            handled=True,
            message="已关闭 LLM 模式。后续任务将恢复使用规则 router。"
        )

    if text in ["使用Mock LLM", "使用mock LLM", "使用模拟LLM", "使用模拟 LLM"]:
        state.llm_selector_mode = "mock"
        return CommandResult(
            handled=True,
            message="已切换为 mock LLM selector。"
        )

    if text in ["使用真实LLM", "使用真实 LLM", "使用Real LLM", "使用real LLM"]:
        state.llm_selector_mode = "real"
        return CommandResult(
            handled=True,
            message="已切换为 real LLM selector。后续 LLM 模式会调用 DeepSeek。"
        )

    if text in ["开启RAG模式", "开启 RAG 模式", "打开RAG模式", "打开 RAG 模式"]:
        state.use_rag_mode = True
        return CommandResult(
            handled=True,
            message="已开启 RAG 模式。后续 LLM 模式会检索 documents/ 中的相关知识片段。"
        )

    if text in ["关闭RAG模式", "关闭 RAG 模式", "退出RAG模式", "退出 RAG 模式"]:
        state.use_rag_mode = False
        return CommandResult(
            handled=True,
            message="已关闭 RAG 模式。"
        )

    if text in ["检查LLM连接", "检查 LLM 连接", "测试LLM连接", "测试 LLM 连接"]:
        result = check_deepseek_connection()
        return CommandResult(
            handled=True,
            message=format_llm_health_check_result(result)
        )

    if text in ["查看工具", "工具列表"]:
        return CommandResult(
            handled=True,
            message=format_tool_list()
        )

    if text in ["查看日志", "最近日志"]:
        return CommandResult(
            handled=True,
            message=read_recent_logs()
        )

    return CommandResult(handled=False)