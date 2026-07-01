from skill_dispatcher import dispatch_skill
from skill_router import route_skill


def test_dispatch_skill_selects_bound_workflow_for_stock_research_skill():
    skill_route = route_skill(
        "按最大回撤生成策略研究报告",
        current_file_type="stock_price",
    )

    dispatch = dispatch_skill(
        user_input="按最大回撤生成策略研究报告",
        skill_route=skill_route,
        current_file_type="stock_price",
    )

    assert dispatch["success"] is True
    assert dispatch["dispatch_status"] == "workflow_selected"
    assert dispatch["selected_execution_path"] == "workflow"
    assert dispatch["should_run_workflow"] is True
    assert dispatch["skill_name"] == "stock_strategy_research_skill"
    assert dispatch["skill_workflow_name"] == "stock_strategy_research_workflow"
    assert dispatch["workflow_name"] == "stock_strategy_research"


def test_dispatch_skill_keeps_tool_route_when_skill_has_no_workflow():
    skill_route = route_skill(
        "分析风险收益并生成金融指标报告",
        current_file_type="stock_price",
    )

    dispatch = dispatch_skill(
        user_input="分析风险收益并生成金融指标报告",
        skill_route=skill_route,
        current_file_type="stock_price",
    )

    assert dispatch["success"] is False
    assert dispatch["dispatch_status"] == "no_bound_workflow"
    assert dispatch["should_run_workflow"] is False
    assert dispatch["selected_execution_path"] is None


def test_dispatch_skill_blocks_workflow_when_file_type_incompatible():
    skill_route = route_skill(
        "完整分析股票数据，并按夏普比率生成策略研究报告",
        current_file_type="channel_data",
    )

    dispatch = dispatch_skill(
        user_input="完整分析股票数据，并按夏普比率生成策略研究报告",
        skill_route=skill_route,
        current_file_type="channel_data",
    )

    assert skill_route["skill_name"] == "stock_strategy_research_skill"
    assert skill_route["file_type_compatible"] is False
    assert dispatch["success"] is False
    assert dispatch["dispatch_status"] == "blocked_by_file_type"
    assert dispatch["should_run_workflow"] is False
