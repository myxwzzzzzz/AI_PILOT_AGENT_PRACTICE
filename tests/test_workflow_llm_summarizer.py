from workflow_llm_summarizer import (
    build_workflow_llm_summary_prompt,
    generate_local_workflow_summary,
    generate_workflow_final_summary,
)


def _sample_workflow_result():
    return {
        "success": True,
        "is_workflow": True,
        "workflow_name": "stock_strategy_research",
        "workflow_display_name": "股票策略研究工作流",
        "workflow_summary": {
            "planned_step_count": 7,
            "executed_step_count": 7,
            "successful_step_count": 7,
            "failed_step_count": 0,
            "sort_by": "sharpe_ratio",
            "sort_by_name": "夏普比率",
        },
        "workflow_judgement": {
            "success": True,
            "overall_label": "具备继续研究价值",
            "risk_level": "low",
            "quality_level": "good",
            "excess_return_level": "positive",
            "findings": ["夏普比率表现较好。"],
            "warnings": ["仍可能存在过拟合风险。"],
            "suggestions": ["建议继续做样本外测试。"],
        },
        "generated_files": [
            "data/output/reports/strategy_research_summary_sharpe_ratio.md",
            "data/output/reports/workflow_summary_report_sharpe_ratio.md",
        ],
        "step_results": [
            {
                "step_index": 1,
                "success": True,
                "tool_name": "read_stock_price_data",
                "description": "读取数据",
            },
            {
                "step_index": 2,
                "success": True,
                "tool_name": "calculate_stock_metrics",
                "description": "计算指标",
            },
        ],
        "plan": {
            "trace": {
                "user_input": "完整分析股票数据，并按夏普比率生成策略研究报告",
            }
        },
    }


def test_build_workflow_llm_summary_prompt_contains_core_fields():
    prompt = build_workflow_llm_summary_prompt(_sample_workflow_result())

    assert "完整分析股票数据" in prompt
    assert "股票策略研究工作流" in prompt
    assert "夏普比率" in prompt
    assert "具备继续研究价值" in prompt
    assert "read_stock_price_data" in prompt


def test_generate_local_workflow_summary_returns_readable_text():
    text = generate_local_workflow_summary(_sample_workflow_result())

    assert "执行状态为成功" in text
    assert "夏普比率" in text
    assert "具备继续研究价值" in text
    assert "建议" in text


def test_generate_workflow_final_summary_can_force_local_summary():
    result = generate_workflow_final_summary(
        _sample_workflow_result(),
        use_llm=False,
    )

    assert result["success"] is True
    assert result["summary_source"] == "local"
    assert result["provider"] == "local_rules"
    assert "执行状态为成功" in result["summary_text"]


def test_generate_workflow_final_summary_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = generate_workflow_final_summary(_sample_workflow_result())

    assert result["success"] is True
    assert result["summary_source"] == "local_fallback"
    assert "DEEPSEEK_API_KEY" in result["fallback_reason"]
    assert result["summary_text"]
