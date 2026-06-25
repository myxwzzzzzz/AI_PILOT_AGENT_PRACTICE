from cli_command_handler import handle_cli_command
from cli_state import AppState
from response_formatter import format_response
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
            "generated_file_count": 1,
            "generated_files": ["data/output/reports/workflow_summary.md"],
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
            "elapsed_seconds": 0.12,
        },
        "step_results": [
            {
                "step_index": 1,
                "step_id": "generate_summary",
                "description": "生成策略研究总结。",
                "tool_name": "generate_strategy_research_summary",
                "arguments": {"sort_by": "sharpe_ratio"},
                "success": True,
                "elapsed_seconds": 0.12,
                "output_paths": ["data/output/reports/workflow_summary.md"],
            }
        ],
        "outputs": {},
        "generated_files": ["data/output/reports/workflow_summary.md"],
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
            "elapsed_seconds": 0.12,
            "step_traces": [
                {
                    "step_index": 1,
                    "step_id": "generate_summary",
                    "tool_name": "generate_strategy_research_summary",
                    "arguments": {"sort_by": "sharpe_ratio"},
                    "execution_status": "success",
                    "success": True,
                    "elapsed_seconds": 0.12,
                    "output_paths": ["data/output/reports/workflow_summary.md"],
                }
            ],
            "generated_files": ["data/output/reports/workflow_summary.md"],
        },
    }


def test_run_agent_task_dispatches_workflow_before_rule_router(monkeypatch):
    captured = {}

    def fake_run_workflow(user_input: str, file_path: str):
        captured["user_input"] = user_input
        captured["file_path"] = file_path
        return _sample_workflow_result()

    monkeypatch.setattr(main, "run_workflow", fake_run_workflow)

    state = AppState(current_file_path=STOCK_FILE_PATH)
    result = main.run_agent_task(
        user_input="帮我完整分析这份股票数据，并按夏普比率生成策略研究报告",
        state=state,
    )

    assert result["is_workflow"] is True
    assert result["workflow_status"] == "success"
    assert captured["file_path"] == STOCK_FILE_PATH


def test_format_response_supports_workflow_result():
    response = format_response(_sample_workflow_result())

    assert "Workflow 执行结果" in response
    assert "股票策略研究工作流" in response
    assert "本次 Workflow 生成文件" in response


def test_format_trace_supports_workflow_trace():
    formatted = format_trace(_sample_workflow_result())

    assert "Workflow 多步任务编排" in formatted
    assert "Step trace" in formatted
    assert "generate_strategy_research_summary" in formatted
    assert "data/output/reports/workflow_summary.md" in formatted


def test_cli_command_lists_supported_workflows():
    state = AppState(current_file_path=STOCK_FILE_PATH)
    result = handle_cli_command("查看工作流", state)

    assert result.handled is True
    assert "当前已支持 Workflow" in result.message
    assert "stock_strategy_research" in result.message
