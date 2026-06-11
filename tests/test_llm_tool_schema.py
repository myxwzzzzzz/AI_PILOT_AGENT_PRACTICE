import json

from llm_tool_schema import build_all_llm_tool_schemas, get_llm_tool_schema_by_name


def test_build_all_llm_tool_schemas():
    schemas = build_all_llm_tool_schemas()

    assert isinstance(schemas, list)
    assert len(schemas) > 0
    assert all("name" in schema for schema in schemas)


def test_get_backtest_report_schema_is_json_serializable():
    schema = get_llm_tool_schema_by_name("generate_backtest_report")

    assert schema is not None
    assert schema["name"] == "generate_backtest_report"
    assert "parameters" in schema
    json.dumps(schema, ensure_ascii=False)


def test_get_parameter_scan_chart_schema_is_json_serializable():
    schema = get_llm_tool_schema_by_name("generate_parameter_scan_chart")

    assert schema is not None
    assert schema["name"] == "generate_parameter_scan_chart"
    assert "parameters" in schema
    json.dumps(schema, ensure_ascii=False)
