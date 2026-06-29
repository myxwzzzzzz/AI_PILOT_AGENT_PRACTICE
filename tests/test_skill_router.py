from skill_router import format_skill_route, route_skill


def test_route_stock_strategy_research_skill():
    result = route_skill(
        "完整分析股票数据，并按夏普比率生成策略研究报告",
        current_file_type="stock_price",
    )

    assert result["success"] is True
    assert result["skill_name"] == "stock_strategy_research_skill"
    assert result["file_type_compatible"] is True
    assert result["confidence"] >= 0.9


def test_route_rag_qa_skill_for_concept_question():
    result = route_skill("最大回撤是什么意思？", current_file_type="stock_price")

    assert result["success"] is True
    assert result["skill_name"] == "rag_qa_skill"
    assert result["required_file_type"] is None
    assert result["file_type_compatible"] is True


def test_route_channel_analysis_skill():
    result = route_skill("哪个渠道表现最好？", current_file_type="channel_data")

    assert result["success"] is True
    assert result["skill_name"] == "channel_analysis_skill"
    assert result["file_type_compatible"] is True


def test_route_ma_strategy_backtest_skill():
    result = route_skill("运行 MA5-MA10 回测", current_file_type="stock_price")

    assert result["success"] is True
    assert result["skill_name"] == "ma_strategy_backtest_skill"
    assert result["file_type_compatible"] is True


def test_route_stock_metrics_skill():
    result = route_skill("分析风险收益并生成金融指标报告", current_file_type="stock_price")

    assert result["success"] is True
    assert result["skill_name"] == "stock_metrics_skill"


def test_route_reports_file_type_mismatch_without_blocking():
    result = route_skill("哪个渠道表现最好？", current_file_type="stock_price")

    assert result["success"] is True
    assert result["skill_name"] == "channel_analysis_skill"
    assert result["required_file_type"] == "channel_data"
    assert result["file_type_compatible"] is False


def test_route_unknown_input_returns_no_match():
    result = route_skill("你好，随便聊聊", current_file_type="stock_price")

    assert result["success"] is False
    assert result["skill_name"] is None
    assert result["confidence"] == 0.0


def test_route_empty_input_returns_no_match():
    result = route_skill("", current_file_type="stock_price")

    assert result["success"] is False
    assert result["skill_name"] is None


def test_format_skill_route_success():
    result = route_skill("运行 MA5-MA10 回测", current_file_type="stock_price")
    text = format_skill_route(result)

    assert "Skill 路由结果" in text
    assert "ma_strategy_backtest_skill" in text
    assert "文件类型是否匹配：是" in text


def test_format_skill_route_no_match():
    result = route_skill("你好", current_file_type="stock_price")
    text = format_skill_route(result)

    assert "未命中" in text
