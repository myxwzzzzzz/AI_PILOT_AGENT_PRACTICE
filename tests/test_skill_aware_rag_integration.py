import sys
import types

if "openai" not in sys.modules:
    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = object
    sys.modules["openai"] = fake_openai

from cli_state import AppState
from trace_formatter import format_trace

import main


STOCK_FILE_PATH = "data/stock_price_strategy.csv"


def test_run_agent_task_passes_skill_name_to_rag(monkeypatch):
    def fake_detect_file_type(file_path: str):
        return {
            "success": True,
            "file_type": "stock_price",
            "file_type_name": "股票价格数据",
            "columns": ["date", "close"],
        }

    monkeypatch.setattr(main, "detect_file_type", fake_detect_file_type)

    state = AppState(
        current_file_path=STOCK_FILE_PATH,
        use_llm_mode=True,
        llm_selector_mode="mock",
        use_rag_mode=True,
    )

    result = main.run_agent_task("最大回撤是什么意思？", state)

    assert result["answer_type"] == "rag_qa"
    assert result["trace"]["skill_route"]["skill_name"] == "rag_qa_skill"
    assert result["trace"]["rag_skill_name"] == "rag_qa_skill"
    assert result["trace"]["skill_aware_rag"] is True
    assert len(result["trace"]["retrieved_chunks"]) > 0
    assert all(
        chunk.get("skill_aware_rag") is True
        for chunk in result["trace"]["retrieved_chunks"]
    )


def test_trace_formatter_shows_skill_aware_rag_metadata(monkeypatch):
    def fake_detect_file_type(file_path: str):
        return {
            "success": True,
            "file_type": "stock_price",
            "file_type_name": "股票价格数据",
            "columns": ["date", "close"],
        }

    monkeypatch.setattr(main, "detect_file_type", fake_detect_file_type)

    state = AppState(
        current_file_path=STOCK_FILE_PATH,
        use_llm_mode=True,
        llm_selector_mode="mock",
        use_rag_mode=True,
    )

    result = main.run_agent_task("最大回撤是什么意思？", state)
    trace_text = format_trace(result)

    assert "Skill-aware RAG" in trace_text
    assert "rag_qa_skill" in trace_text
    assert "RAG 检索范围" in trace_text
