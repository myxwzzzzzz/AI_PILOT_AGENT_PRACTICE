from workflow_planner import (
    STOCK_STRATEGY_WORKFLOW_NAME,
    format_workflow_plan,
    is_workflow_request,
    list_supported_workflows,
    plan_workflow,
)


STOCK_FILE_PATH = "data/stock_price_strategy.csv"
CHANNEL_FILE_PATH = "data/channel_data.csv"


def test_is_workflow_request_detects_complete_stock_strategy_request():
    assert is_workflow_request("帮我完整分析这份股票数据，并生成策略研究报告") is True
    assert is_workflow_request("生成 MA5-MA10 回测报告") is False


def test_list_supported_workflows_contains_stock_strategy_workflow():
    workflows = list_supported_workflows()

    assert len(workflows) >= 1
    assert workflows[0]["name"] == STOCK_STRATEGY_WORKFLOW_NAME
    assert workflows[0]["step_count"] >= 5


def test_plan_stock_strategy_workflow_success():
    plan = plan_workflow(
        user_input="帮我完整分析这份股票数据，并生成策略研究报告",
        file_path=STOCK_FILE_PATH,
    )

    assert plan["success"] is True
    assert plan["is_workflow"] is True
    assert plan["workflow_name"] == STOCK_STRATEGY_WORKFLOW_NAME
    assert len(plan["steps"]) >= 5
    assert plan["steps"][0]["tool_name"] == "read_stock_price_data"
    assert plan["steps"][-1]["tool_name"] == "generate_strategy_research_summary"
    assert plan["trace"]["planning_status"] == "success"


def test_plan_stock_strategy_workflow_parses_sort_by():
    plan = plan_workflow(
        user_input="帮我完整分析这份股票数据，并按最大回撤生成策略研究报告",
        file_path=STOCK_FILE_PATH,
    )

    assert plan["success"] is True
    assert plan["planning_metadata"]["sort_by"] == "max_drawdown"

    scan_steps = [
        step for step in plan["steps"]
        if step["tool_name"] in {
            "optimize_moving_average_parameters",
            "generate_parameter_scan_report",
            "generate_parameter_scan_chart",
            "generate_strategy_research_summary",
        }
    ]

    assert scan_steps
    assert all(step["arguments"]["sort_by"] == "max_drawdown" for step in scan_steps)


def test_plan_non_workflow_request_returns_no_workflow():
    plan = plan_workflow(
        user_input="生成 MA5-MA10 回测报告",
        file_path=STOCK_FILE_PATH,
    )

    assert plan["success"] is True
    assert plan["is_workflow"] is False
    assert plan["steps"] == []
    assert plan["trace"]["planning_status"] == "not_workflow_request"


def test_plan_workflow_rejects_wrong_file_type():
    plan = plan_workflow(
        user_input="帮我完整分析这份股票数据，并生成策略研究报告",
        file_path=CHANNEL_FILE_PATH,
    )

    assert plan["success"] is False
    assert plan["is_workflow"] is True
    assert plan["workflow_name"] == STOCK_STRATEGY_WORKFLOW_NAME
    assert "股票价格数据" in plan["error"]
    assert plan["trace"]["planning_status"] == "blocked_by_file_type_check"


def test_format_workflow_plan_includes_tools_and_arguments():
    plan = plan_workflow(
        user_input="帮我完整分析这份股票数据，并按夏普生成策略研究报告",
        file_path=STOCK_FILE_PATH,
    )

    formatted = format_workflow_plan(plan)

    assert "Workflow 计划" in formatted
    assert "read_stock_price_data" in formatted
    assert "generate_strategy_research_summary" in formatted
    assert "sort_by=sharpe_ratio" in formatted
