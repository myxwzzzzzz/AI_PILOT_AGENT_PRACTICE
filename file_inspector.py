import os
import pandas as pd


def detect_file_type(file_path: str) -> dict:
    """
    根据 CSV 文件字段，识别当前文件类型。

    返回类型：
    - channel_data：渠道转化数据
    - stock_price：股票价格数据
    - unknown：未知类型
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "file_type": None,
            "error": f"文件不存在：{file_path}"
        }

    try:
        df = pd.read_csv(file_path)
        columns = set(df.columns)

        channel_required = {"channel", "visits", "signups", "payments"}
        stock_required = {"date", "close"}

        if channel_required.issubset(columns):
            return {
                "success": True,
                "file_type": "channel_data",
                "file_type_name": "渠道转化数据",
                "columns": list(df.columns)
            }

        if stock_required.issubset(columns):
            return {
                "success": True,
                "file_type": "stock_price",
                "file_type_name": "股票价格数据",
                "columns": list(df.columns)
            }

        return {
            "success": True,
            "file_type": "unknown",
            "file_type_name": "未知类型数据",
            "columns": list(df.columns)
        }

    except Exception as e:
        return {
            "success": False,
            "file_type": None,
            "error": str(e)
        }


def describe_file_type(file_path: str) -> str:
    """
    返回当前文件类型的自然语言描述。
    """
    result = detect_file_type(file_path)

    if not result.get("success"):
        return f"文件类型识别失败：{result.get('error')}"

    file_type_name = result.get("file_type_name")
    columns = result.get("columns", [])

    return f"当前文件类型：{file_type_name}；字段：{', '.join(columns)}"