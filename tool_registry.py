from tools import (
    read_csv_file,
    summarize_csv,
    analyze_channel_conversion,
    generate_channel_analysis_report
)

from finance_tools import (
    read_stock_price_data,
    calculate_stock_metrics,
    generate_stock_metrics_report,
    run_moving_average_backtest,
    generate_backtest_report,
    generate_backtest_charts,
    optimize_moving_average_parameters,
    generate_parameter_scan_report,
    generate_parameter_scan_chart,
    generate_strategy_research_summary,
)


TOOL_REGISTRY = [
    {
        "name": "read_stock_price_data",
        "description": "读取股票/策略价格数据，返回日期区间、起始价格、结束价格和字段信息。",
        "keywords": ["股票数据", "价格数据", "行情数据", "收盘价", "读取股票"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": read_stock_price_data
    },
    {
        "name": "generate_strategy_research_summary",
        "description": "综合基础风险收益指标、默认均线策略回测和参数扫描结果，生成策略研究总结报告。",
        "keywords": ["策略研究总结", "策略研究报告", "策略总结报告", "综合策略报告", "总结策略研究", "总结回测结果"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": generate_strategy_research_summary
    },
    {
        "name": "generate_parameter_scan_chart",
        "description": "生成均线参数扫描图表，用于对比不同 MA 参数组合在夏普比率、策略收益率、超额收益或最大回撤等指标上的表现。",
        "keywords": ["参数扫描图表", "扫描图表", "参数对比图", "均线参数图表", "生成参数图表", "生成扫描图表"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": generate_parameter_scan_chart
    },
    {
        "name": "generate_parameter_scan_report",
        "description": "批量扫描多组均线策略参数，并生成参数扫描对比报告。",
        "keywords": ["参数扫描报告", "参数优化报告", "生成参数扫描报告", "生成参数优化报告"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": generate_parameter_scan_report
    },
    {
        "name": "optimize_moving_average_parameters",
        "description": "批量扫描多组均线策略参数，比较收益率、超额收益、最大回撤和夏普比率，并找出表现较好的参数组合。",
        "keywords": ["参数扫描", "参数优化", "优化均线", "扫描均线", "优化均线策略", "扫描均线参数"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": optimize_moving_average_parameters
    },
    {
        "name": "generate_backtest_charts",
        "description": "生成均线策略回测图表，包括策略净值曲线和策略回撤曲线。",
        "keywords": ["回测图表", "净值曲线", "回撤曲线", "生成图表", "策略图表", "生成回测图表"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": generate_backtest_charts
    },
    {
        "name": "generate_backtest_report",
        "description": "基于股票价格数据生成均线策略回测报告。",
        "keywords": ["回测报告", "策略回测报告", "生成回测报告", "策略报告"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": generate_backtest_report
    },
    {
        "name": "run_moving_average_backtest",
        "description": "运行 MA3-MA5 简单均线策略回测，计算策略收益、基准收益、最大回撤、夏普比率和最新信号。",
        "keywords": ["均线策略", "策略回测", "运行回测", "回测", "MA策略", "移动平均"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": run_moving_average_backtest
    },
    {
        "name": "generate_stock_metrics_report",
        "description": "基于股票价格数据生成金融风险收益分析报告。",
        "keywords": ["金融报告", "风险收益报告", "指标报告", "股票报告"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": generate_stock_metrics_report
    },
    {
        "name": "calculate_stock_metrics",
        "description": "计算区间收益率、年化波动率、最大回撤、夏普比率等金融指标。",
        "keywords": ["风险收益", "最大回撤", "夏普", "波动率", "收益率", "金融指标"],
        "required_file_type": "stock_price",
        "required_file_type_name": "股票价格数据",
        "handler": calculate_stock_metrics
    },
    {
        "name": "generate_channel_analysis_report",
        "description": "基于渠道数据生成渠道转化率分析报告。",
        "keywords": ["渠道报告", "渠道分析报告"],
        "required_file_type": "channel_data",
        "required_file_type_name": "渠道转化数据",
        "handler": generate_channel_analysis_report
    },
    {
        "name": "analyze_channel_conversion",
        "description": "分析各渠道注册转化率、付费转化率和注册到付费转化率。",
        "keywords": ["转化率", "渠道表现", "哪个渠道", "渠道分析"],
        "required_file_type": "channel_data",
        "required_file_type_name": "渠道转化数据",
        "handler": analyze_channel_conversion
    },
    {
        "name": "summarize_csv",
        "description": "查看 CSV 数据规模、字段、缺失值和基础统计信息。",
        "keywords": ["统计", "缺失值", "描述", "概览", "总结"],
        "required_file_type": None,
        "required_file_type_name": "任意 CSV 数据",
        "handler": summarize_csv
    },
    {
        "name": "read_csv_file",
        "description": "读取 CSV 文件，返回行数、字段和前几行数据预览。",
        "keywords": ["读取", "字段", "列名", "预览", "看看数据"],
        "required_file_type": None,
        "required_file_type_name": "任意 CSV 数据",
        "handler": read_csv_file
    }
]


def match_keywords(user_input: str, keywords: list[str]) -> bool:
    """
    判断用户输入是否命中任意关键词。
    """
    return any(keyword in user_input for keyword in keywords)


def find_matching_tool(user_input: str) -> dict | None:
    """
    根据用户输入，从工具注册表中寻找匹配工具。

    注意：
    TOOL_REGISTRY 的顺序就是匹配优先级。
    越具体的工具应该放在越前面。
    """
    for tool in TOOL_REGISTRY:
        if match_keywords(user_input, tool["keywords"]):
            return tool

    return None


def get_tool_by_name(tool_name: str) -> dict | None:
    """
    根据工具名称获取工具定义。
    """
    for tool in TOOL_REGISTRY:
        if tool["name"] == tool_name:
            return tool

    return None


def list_available_tools() -> list[dict]:
    """
    返回所有可用工具的简要信息。
    """
    tools = []

    for tool in TOOL_REGISTRY:
        tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "required_file_type_name": tool["required_file_type_name"],
            "keywords": tool["keywords"]
        })

    return tools

def get_matched_keywords(user_input: str, keywords: list[str]) -> list[str]:
    """
    返回用户输入中命中的关键词列表。
    """
    return [keyword for keyword in keywords if keyword in user_input]


def find_matching_tool_with_trace(user_input: str) -> tuple[dict | None, dict]:
    """
    根据用户输入，从工具注册表中寻找匹配工具，并返回匹配轨迹信息。
    """
    for tool in TOOL_REGISTRY:
        matched_keywords = get_matched_keywords(user_input, tool["keywords"])

        if matched_keywords:
            trace = {
                "match_type": "keyword",
                "matched_keywords": matched_keywords,
                "candidate_tool": tool["name"],
                "candidate_tool_description": tool["description"]
            }
            return tool, trace

    trace = {
        "match_type": "no_match",
        "matched_keywords": [],
        "candidate_tool": None,
        "candidate_tool_description": None
    }

    return None, trace