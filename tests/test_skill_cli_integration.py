from cli_command_handler import handle_cli_command
from cli_state import AppState
from trace_formatter import format_trace

import main


STOCK_FILE_PATH = "data/stock_price_strategy.csv"


def _sample_workflow_result():
    return {
        "success": True,
        "is_workflow": True,
        "workflow_name": "stock_strategy_research",
        "workflow_display_name": "股票策略研究工作流",
        "workflow_status": "success",
        "workflow_summary": {
            "planned_step_count": 1,
            "executed_step_count": 1,
            "successful_step_count": 1,
            "failed_step_count": 0,
            "generated_file_count": 0,
            "generated_files": [],
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
        },
        "step_results": [],
        "outputs": {},
        "generated_files": [],
        "trace": {
            "runner_type": "rule_based_workflow_runner",
            "workflow_name": "stock_strategy_research",
            "workflow_display_name": "股票策略研究工作流",
            "current_file_path": STOCK_FILE_PATH,
            "planned_step_count": 1,
            "execution_status": "success",
            "stop_on_failure": True,
            "completed_steps": 1,
            "failed_step_count": 0,
            "step_traces": [],
            "generated_files": [],
        },
    }


def test_cli_command_lists_registered_skills():
    state = AppState(current_file_path=STOCK_FILE_PATH)

    result = handle_cli_command("查看技能", state)

    assert result.handled is True
    assert "已注册 Skill" in result.message
    assert "stock_strategy_research_skill" in result.message
    assert "当前文件可优先使用的 Skill" in result.message


def test_run_agent_task_attaches_skill_route_to_workflow(monkeypatch):
    def fake_detect_file_type(file_path: str):
        return {
            "success": True,
            "file_type": "stock_price",
            "file_type_name": "股票价格数据",
            "columns": ["date", "close"],
        }

    def fake_run_workflow(user_input: str, file_path: str):
        return _sample_workflow_result()

    monkeypatch.setattr(main, "detect_file_type", fake_detect_file_type)
    monkeypatch.setattr(main, "run_workflow", fake_run_workflow)

    state = AppState(current_file_path=STOCK_FILE_PATH)
    result = main.run_agent_task(
        "完整分析股票数据，并按夏普比率生成策略研究报告",
        state,
    )

    assert result["skill_route"]["skill_name"] == "stock_strategy_research_skill"
    assert result["trace"]["skill_route"]["skill_name"] == "stock_strategy_research_skill"

    trace_text = format_trace(result)
    assert "命中 Skill" in trace_text
    assert "stock_strategy_research_skill" in trace_text


def test_run_agent_task_attaches_skill_route_to_rule_result(monkeypatch):
    def fake_detect_file_type(file_path: str):
        return {
            "success": True,
            "file_type": "stock_price",
            "file_type_name": "股票价格数据",
            "columns": ["date", "close"],
        }

    def fake_route_task(user_input: str, file_path: str):
        return {
            "success": True,
            "selected_tool": "calculate_stock_metrics",
            "tool_result": {"success": True},
            "trace": {
                "user_input": user_input,
                "selected_tool": "calculate_stock_metrics",
                "execution_status": "success",
            },
        }

    monkeypatch.setattr(main, "detect_file_type", fake_detect_file_type)
    monkeypatch.setattr(main, "route_task", fake_route_task)

    state = AppState(current_file_path=STOCK_FILE_PATH)
    result = main.run_agent_task("分析风险收益并生成金融指标报告", state)

    assert result["skill_route"]["skill_name"] == "stock_metrics_skill"
    assert result["trace"]["skill_route"]["skill_name"] == "stock_metrics_skill"

    trace_text = format_trace(result)
    assert "命中 Skill" in trace_text
    assert "stock_metrics_skill" in trace_text


def test_run_agent_task_records_no_skill_match(monkeypatch):
    def fake_detect_file_type(file_path: str):
        return {
            "success": True,
            "file_type": "stock_price",
            "file_type_name": "股票价格数据",
            "columns": ["date", "close"],
        }

    def fake_route_task(user_input: str, file_path: str):
        return {
            "success": False,
            "error": "no match",
            "trace": {"user_input": user_input},
        }

    monkeypatch.setattr(main, "detect_file_type", fake_detect_file_type)
    monkeypatch.setattr(main, "route_task", fake_route_task)

    state = AppState(current_file_path=STOCK_FILE_PATH)
    result = main.run_agent_task("你好，随便聊聊", state)

    assert result["skill_route"]["success"] is False
    assert result["trace"]["skill_route"]["skill_name"] is None

    trace_text = format_trace(result)
    assert "Skill 路由：未命中" in trace_text
