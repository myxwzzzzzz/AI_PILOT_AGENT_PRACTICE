from copy import deepcopy

import pytest

from tool_registry import TOOL_REGISTRY
from workflow_planner import plan_workflow
from workflow_runner import format_workflow_result, run_workflow, run_workflow_plan


STOCK_FILE_PATH = "data/stock_price_strategy.csv"
CHANNEL_FILE_PATH = "data/channel_data.csv"


def _get_tool(tool_name: str) -> dict:
    for tool in TOOL_REGISTRY:
        if tool["name"] == tool_name:
            return tool
    raise AssertionError(f"tool not found: {tool_name}")


@pytest.fixture
def restore_tool_handlers():
    original_handlers = {
        tool["name"]: tool["handler"]
        for tool in TOOL_REGISTRY
    }
    yield
    for tool in TOOL_REGISTRY:
        tool["handler"] = original_handlers[tool["name"]]


def _make_success_handler(tool_name: str, calls: list[str]):
    def handler(file_path: str, **kwargs):
        calls.append(tool_name)
        return {
            "success": True,
            "message": f"{tool_name} executed",
            "summary": {
                "file_path": file_path,
                "arguments": kwargs,
            },
        }

    return handler


def _make_path_handler(tool_name: str, calls: list[str], **paths):
    def handler(file_path: str, **kwargs):
        calls.append(tool_name)
        return {
            "success": True,
            "message": f"{tool_name} executed",
            **paths,
        }

    return handler


def test_run_workflow_plan_executes_steps_in_order(restore_tool_handlers):
    calls: list[str] = []
    _get_tool("read_stock_price_data")["handler"] = _make_success_handler("read_stock_price_data", calls)
    _get_tool("calculate_stock_metrics")["handler"] = _make_success_handler("calculate_stock_metrics", calls)

    plan = {
        "success": True,
        "is_workflow": True,
        "workflow_name": "test_workflow",
        "workflow_display_name": "测试工作流",
        "steps": [
            {
                "step_id": "read_data",
                "description": "读取数据",
                "tool_name": "read_stock_price_data",
                "arguments": {},
                "output_key": "data_overview",
            },
            {
                "step_id": "calculate_metrics",
                "description": "计算指标",
                "tool_name": "calculate_stock_metrics",
                "arguments": {},
                "output_key": "metrics",
            },
        ],
    }

    result = run_workflow_plan(plan=plan, file_path=STOCK_FILE_PATH)

    assert result["success"] is True
    assert result["workflow_status"] == "success"
    assert calls == ["read_stock_price_data", "calculate_stock_metrics"]
    assert len(result["step_results"]) == 2
    assert result["outputs"]["data_overview"]["success"] is True
    assert result["trace"]["completed_steps"] == 2
    assert result["trace"]["step_traces"][0]["tool_name"] == "read_stock_price_data"
    assert result["workflow_summary"]["successful_step_count"] == 2


def test_run_workflow_plan_stops_on_failed_step(restore_tool_handlers):
    calls: list[str] = []
    _get_tool("read_stock_price_data")["handler"] = _make_success_handler("read_stock_price_data", calls)

    def failing_handler(file_path: str, **kwargs):
        calls.append("calculate_stock_metrics")
        return {
            "success": False,
            "error": "metrics failed",
        }

    _get_tool("calculate_stock_metrics")["handler"] = failing_handler
    _get_tool("generate_stock_metrics_report")["handler"] = _make_success_handler(
        "generate_stock_metrics_report",
        calls,
    )

    plan = {
        "success": True,
        "is_workflow": True,
        "workflow_name": "test_workflow",
        "workflow_display_name": "测试工作流",
        "steps": [
            {
                "step_id": "read_data",
                "description": "读取数据",
                "tool_name": "read_stock_price_data",
                "arguments": {},
                "output_key": "data_overview",
            },
            {
                "step_id": "calculate_metrics",
                "description": "计算指标",
                "tool_name": "calculate_stock_metrics",
                "arguments": {},
                "output_key": "metrics",
            },
            {
                "step_id": "generate_report",
                "description": "生成报告",
                "tool_name": "generate_stock_metrics_report",
                "arguments": {},
                "output_key": "report",
            },
        ],
    }

    result = run_workflow_plan(plan=plan, file_path=STOCK_FILE_PATH)

    assert result["success"] is False
    assert result["workflow_status"] == "failed"
    assert result["failed_step"]["step_id"] == "calculate_metrics"
    assert result["trace"]["failed_step_id"] == "calculate_metrics"
    assert calls == ["read_stock_price_data", "calculate_stock_metrics"]
    assert "report" not in result["outputs"]
    assert result["workflow_summary"]["failed_step_count"] == 1


def test_run_workflow_plan_rejects_non_workflow_plan():
    plan = {
        "success": True,
        "is_workflow": False,
        "reason": "当前输入不像 workflow 请求。",
        "steps": [],
    }

    result = run_workflow_plan(plan=plan, file_path=STOCK_FILE_PATH)

    assert result["success"] is False
    assert result["workflow_status"] == "not_workflow"
    assert "workflow 请求" in result["error"]
    assert result["workflow_summary"]["executed_step_count"] == 0


def test_run_workflow_plan_returns_planning_failure_for_blocked_plan():
    plan = plan_workflow(
        user_input="帮我完整分析这份股票数据，并生成策略研究报告",
        file_path=CHANNEL_FILE_PATH,
    )

    result = run_workflow_plan(plan=plan, file_path=CHANNEL_FILE_PATH)

    assert result["success"] is False
    assert result["workflow_status"] == "planning_failed"
    assert "股票价格数据" in result["error"]
    assert result["suggestion"]
    assert result["workflow_summary"]["workflow_status"] == "planning_failed"


def test_run_workflow_executes_planned_stock_strategy_steps(restore_tool_handlers):
    calls: list[str] = []
    workflow_tool_names = [
        "read_stock_price_data",
        "calculate_stock_metrics",
        "generate_stock_metrics_report",
        "optimize_moving_average_parameters",
        "generate_parameter_scan_report",
        "generate_parameter_scan_chart",
        "generate_strategy_research_summary",
    ]

    for tool_name in workflow_tool_names:
        _get_tool(tool_name)["handler"] = _make_success_handler(tool_name, calls)

    result = run_workflow(
        user_input="帮我完整分析这份股票数据，并按最大回撤生成策略研究报告",
        file_path=STOCK_FILE_PATH,
    )

    assert result["success"] is True
    assert result["workflow_name"] == "stock_strategy_research"
    assert result["plan"]["planning_metadata"]["sort_by"] == "max_drawdown"
    assert result["workflow_summary"]["sort_by"] == "max_drawdown"
    assert calls == workflow_tool_names
    assert len(result["step_results"]) == len(workflow_tool_names)


def test_run_workflow_plan_collects_generated_file_paths(restore_tool_handlers):
    calls: list[str] = []
    _get_tool("generate_stock_metrics_report")["handler"] = _make_path_handler(
        "generate_stock_metrics_report",
        calls,
        output_path="data/output/reports/stock_metrics_report.md",
    )
    _get_tool("generate_parameter_scan_chart")["handler"] = _make_path_handler(
        "generate_parameter_scan_chart",
        calls,
        chart_path="data/output/charts/parameter_scan_sharpe_ratio.png",
    )

    plan = {
        "success": True,
        "is_workflow": True,
        "workflow_name": "test_workflow",
        "workflow_display_name": "测试工作流",
        "planning_metadata": {
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
        },
        "steps": [
            {
                "step_id": "report",
                "description": "生成报告",
                "tool_name": "generate_stock_metrics_report",
                "arguments": {},
                "output_key": "metrics_report",
            },
            {
                "step_id": "chart",
                "description": "生成图表",
                "tool_name": "generate_parameter_scan_chart",
                "arguments": {"sort_by": "sharpe_ratio"},
                "output_key": "scan_chart",
            },
        ],
    }

    result = run_workflow_plan(plan=deepcopy(plan), file_path=STOCK_FILE_PATH)

    assert result["success"] is True
    assert result["generated_files"] == [
        "data/output/reports/stock_metrics_report.md",
        "data/output/charts/parameter_scan_sharpe_ratio.png",
    ]
    assert result["outputs"]["scan_chart"]["primary_output_path"] == "data/output/charts/parameter_scan_sharpe_ratio.png"
    assert result["step_results"][1]["output_paths"] == ["data/output/charts/parameter_scan_sharpe_ratio.png"]
    assert result["trace"]["generated_files"] == result["generated_files"]
    assert result["trace"]["step_traces"][1]["arguments"] == {"sort_by": "sharpe_ratio"}
    assert result["workflow_summary"]["generated_file_count"] == 2


def test_format_workflow_result_includes_step_status(restore_tool_handlers):
    calls: list[str] = []
    _get_tool("read_stock_price_data")["handler"] = _make_success_handler("read_stock_price_data", calls)

    plan = {
        "success": True,
        "is_workflow": True,
        "workflow_name": "test_workflow",
        "workflow_display_name": "测试工作流",
        "steps": [
            {
                "step_id": "read_data",
                "description": "读取数据",
                "tool_name": "read_stock_price_data",
                "arguments": {},
                "output_key": "data_overview",
            },
        ],
    }

    result = run_workflow_plan(plan=deepcopy(plan), file_path=STOCK_FILE_PATH)
    formatted = format_workflow_result(result)

    assert "Workflow 执行结果" in formatted
    assert "读取数据" in formatted
    assert "成功" in formatted
    assert "data_overview" in formatted
    assert "步骤概览" in formatted
    assert "参数：无" in formatted
    assert "总耗时" in formatted


def test_format_workflow_result_includes_generated_files_and_arguments(restore_tool_handlers):
    calls: list[str] = []
    _get_tool("generate_parameter_scan_chart")["handler"] = _make_path_handler(
        "generate_parameter_scan_chart",
        calls,
        chart_path="data/output/charts/parameter_scan_sharpe_ratio.png",
    )

    plan = {
        "success": True,
        "is_workflow": True,
        "workflow_name": "test_workflow",
        "workflow_display_name": "测试工作流",
        "planning_metadata": {
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
        },
        "steps": [
            {
                "step_id": "chart",
                "description": "生成图表",
                "tool_name": "generate_parameter_scan_chart",
                "arguments": {"sort_by": "sharpe_ratio"},
                "output_key": "scan_chart",
            },
        ],
    }

    result = run_workflow_plan(plan=deepcopy(plan), file_path=STOCK_FILE_PATH)
    formatted = format_workflow_result(result)

    assert "排序指标：夏普比率 (sharpe_ratio)" in formatted
    assert "参数：sort_by=sharpe_ratio" in formatted
    assert "本次 Workflow 生成文件" in formatted
    assert "data/output/charts/parameter_scan_sharpe_ratio.png" in formatted
