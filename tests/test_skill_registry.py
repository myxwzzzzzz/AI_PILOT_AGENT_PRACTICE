from skill_registry import (
    format_skill_list,
    get_skill,
    get_skills_for_file_type,
    list_skills,
)


def test_list_skills_returns_registered_skills():
    skills = list_skills()

    skill_names = {skill["name"] for skill in skills}

    assert "channel_analysis_skill" in skill_names
    assert "stock_metrics_skill" in skill_names
    assert "ma_strategy_backtest_skill" in skill_names
    assert "stock_strategy_research_skill" in skill_names
    assert "rag_qa_skill" in skill_names


def test_get_skill_returns_copy_by_name():
    skill = get_skill("stock_strategy_research_skill")

    assert skill is not None
    assert skill["display_name"] == "股票策略研究 Skill"
    assert "stock_strategy_research_workflow" in skill["workflows"]
    assert "generate_strategy_research_summary" in skill["tools"]

    skill["tools"].append("mutated_tool")

    fresh_skill = get_skill("stock_strategy_research_skill")
    assert "mutated_tool" not in fresh_skill["tools"]


def test_get_skill_returns_none_for_unknown_skill():
    assert get_skill("unknown_skill") is None


def test_get_skills_for_stock_price_file_type():
    skills = get_skills_for_file_type("stock_price")
    skill_names = {skill["name"] for skill in skills}

    assert "stock_metrics_skill" in skill_names
    assert "ma_strategy_backtest_skill" in skill_names
    assert "stock_strategy_research_skill" in skill_names
    assert "rag_qa_skill" in skill_names
    assert "channel_analysis_skill" not in skill_names


def test_get_skills_for_channel_data_file_type():
    skills = get_skills_for_file_type("channel_data")
    skill_names = {skill["name"] for skill in skills}

    assert "channel_analysis_skill" in skill_names
    assert "rag_qa_skill" in skill_names
    assert "stock_strategy_research_skill" not in skill_names


def test_format_skill_list_contains_key_information():
    text = format_skill_list([get_skill("stock_strategy_research_skill")])

    assert "股票策略研究 Skill" in text
    assert "stock_strategy_research_skill" in text
    assert "适用文件类型：stock_price" in text
    assert "Workflow 数：1" in text
    assert "工具数：" in text


def test_format_skill_list_handles_empty_list():
    assert format_skill_list([]) == "当前没有已注册 Skill。"
