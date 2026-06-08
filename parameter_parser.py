import re


def extract_ma_windows(user_input: str) -> dict:
    """
    从用户输入中提取均线窗口参数。

    支持示例：
    - 运行 MA5-MA10 回测
    - 生成 MA5 MA20 回测报告
    - 用 5 日均线和 10 日均线做回测
    - 运行5日和20日均线策略

    返回：
    {
        "success": True,
        "short_window": 5,
        "long_window": 10,
        "source": "MA_PATTERN"
    }
    """
    user_input = user_input.strip()

    # 情况 1：匹配 MA5-MA10 / MA5 MA10 / ma5 ma20
    ma_pattern = re.findall(r"[Mm][Aa]\s*(\d+)", user_input)

    if len(ma_pattern) >= 2:
        window_1 = int(ma_pattern[0])
        window_2 = int(ma_pattern[1])

        short_window = min(window_1, window_2)
        long_window = max(window_1, window_2)

        return validate_ma_windows(
            short_window=short_window,
            long_window=long_window,
            source="MA_PATTERN"
        )

    # 情况 2：匹配 5日均线、10日均线
    day_ma_pattern = re.findall(r"(\d+)\s*日均线", user_input)

    if len(day_ma_pattern) >= 2:
        window_1 = int(day_ma_pattern[0])
        window_2 = int(day_ma_pattern[1])

        short_window = min(window_1, window_2)
        long_window = max(window_1, window_2)

        return validate_ma_windows(
            short_window=short_window,
            long_window=long_window,
            source="DAY_MA_PATTERN"
        )

    # 情况 3：没有提取到参数，使用默认 MA3-MA5
    return {
        "success": True,
        "short_window": 3,
        "long_window": 5,
        "source": "DEFAULT",
        "message": "未识别到自定义均线参数，使用默认 MA3-MA5。"
    }


def validate_ma_windows(short_window: int, long_window: int, source: str) -> dict:
    """
    校验均线参数是否合法。
    """
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

    if long_window > 250:
        return {
            "success": False,
            "error": "长期均线窗口过大，当前 demo 建议不超过 250"
        }

    return {
        "success": True,
        "short_window": short_window,
        "long_window": long_window,
        "source": source
    }

def extract_scan_sort_by(user_input: str) -> dict:
    """
    从用户输入中提取参数扫描排序指标。

    支持：
    - 夏普 / 夏普比率 / sharpe
    - 收益率 / 策略收益
    - 超额收益
    - 最大回撤 / 回撤
    """
    user_input = user_input.strip().lower()

    if any(keyword in user_input for keyword in ["夏普", "夏普比率", "sharpe"]):
        return {
            "success": True,
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
            "source": "USER_SPECIFIED"
        }

    if any(keyword in user_input for keyword in ["超额收益", "超额"]):
        return {
            "success": True,
            "sort_by": "excess_return",
            "sort_by_name": "超额收益",
            "source": "USER_SPECIFIED"
        }

    if any(keyword in user_input for keyword in ["最大回撤", "回撤"]):
        return {
            "success": True,
            "sort_by": "max_drawdown",
            "sort_by_name": "最大回撤",
            "source": "USER_SPECIFIED"
        }

    if any(keyword in user_input for keyword in ["收益率", "策略收益", "收益"]):
        return {
            "success": True,
            "sort_by": "strategy_total_return",
            "sort_by_name": "策略收益率",
            "source": "USER_SPECIFIED"
        }

    return {
        "success": True,
        "sort_by": "sharpe_ratio",
        "sort_by_name": "夏普比率",
        "source": "DEFAULT",
        "message": "未识别到排序指标，默认按夏普比率排序。"
    }