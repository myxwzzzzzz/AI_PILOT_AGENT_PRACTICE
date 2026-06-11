import pytest

pytest.importorskip("openai")

from llm_health_check import check_deepseek_connection, format_llm_health_check_result


def test_check_deepseek_connection_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = check_deepseek_connection()
    formatted = format_llm_health_check_result(result)

    assert result["success"] is False
    assert result["stage"] == "api_key_check"
    assert "DEEPSEEK_API_KEY" in formatted
