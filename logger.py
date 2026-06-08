import json
from datetime import datetime
from pathlib import Path


LOG_DIR = Path("data/logs")
LOG_FILE = LOG_DIR / "tool_calls.jsonl"


def init_log_dir():
    """
    初始化日志目录。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def write_tool_log(
    user_input: str,
    file_path: str,
    route_result: dict
) -> dict:
    """
    记录一次工具调用日志。
    """
    init_log_dir()

    log_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": user_input,
        "file_path": file_path,
        "success": route_result.get("success", False),
        "selected_tool": route_result.get("selected_tool"),
        "error": route_result.get("error")
    }
    if "trace" in route_result:
        log_record["trace"] = route_result.get("trace")
        
    tool_result = route_result.get("tool_result", {})

    if isinstance(tool_result, dict):
        log_record["tool_success"] = tool_result.get("success")
        log_record["tool_error"] = tool_result.get("error")

        # 只记录摘要，避免日志太大
        if "rows" in tool_result:
            log_record["rows"] = tool_result.get("rows")

        if "columns" in tool_result:
            log_record["columns"] = tool_result.get("columns")

        if "output_path" in tool_result:
            log_record["output_path"] = tool_result.get("output_path")

        if "summary" in tool_result:
            log_record["summary"] = tool_result.get("summary")

        if "best_payment_channel" in tool_result:
            log_record["best_payment_channel"] = tool_result.get("best_payment_channel")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_record, ensure_ascii=False) + "\n")

    return {
        "success": True,
        "message": f"工具调用日志已写入：{LOG_FILE}",
        "log_file": str(LOG_FILE)
    }


def read_recent_logs(limit: int = 5) -> dict:
    """
    读取最近 N 条工具调用日志。
    """
    if not LOG_FILE.exists():
        return {
            "success": True,
            "logs": [],
            "message": "暂无工具调用日志"
        }

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    recent_lines = lines[-limit:]

    logs = [json.loads(line) for line in recent_lines]

    return {
        "success": True,
        "logs": logs
    }