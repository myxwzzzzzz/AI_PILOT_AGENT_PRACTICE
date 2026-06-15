from trace_formatter import (
    format_rag_retrieval_trace_lines,
    format_single_retrieved_chunk_trace_line,
    format_trace,
)


def test_format_trace_without_trace():
    assert format_trace({}) == "暂无工具调用轨迹。"


def test_format_rag_qa_trace_shows_keyword_retrieval_metadata():
    route_result = {
        "trace": {
            "router_type": "rag_qa",
            "intent_type": "knowledge_qa",
            "user_input": "最大回撤是什么意思？",
            "selector_mode": "real",
            "llm_reason": "知识问答",
            "use_rag": True,
            "rag_answer_source": "local_rule_fallback",
            "retrieved_chunks": [
                {
                    "source": "documents/risk_metrics_notes.md",
                    "chunk_id": "risk_metrics_notes.md::chunk_0",
                    "score": 18,
                    "retrieval_mode": "keyword",
                }
            ],
            "fallback_used": False,
            "fallback_steps": [],
        }
    }

    trace_text = format_trace(route_result)

    assert "RAG 检索模式：keyword" in trace_text
    assert "RAG 检索片段数：1" in trace_text
    assert "mode=keyword" in trace_text
    assert "risk_metrics_notes.md::chunk_0" in trace_text


def test_format_hybrid_chunk_trace_shows_fusion_metadata():
    chunk = {
        "source": "documents/ma_strategy_notes.md",
        "chunk_id": "ma_strategy_notes.md::chunk_1",
        "score": 0.75,
        "retrieval_mode": "hybrid",
        "retrieval_sources": ["keyword", "embedding"],
        "keyword_score": 21,
        "embedding_score": 0.82,
        "embedding_provider": "hash",
        "embedding_status": "available",
    }

    line = format_single_retrieved_chunk_trace_line(chunk)

    assert "mode=hybrid" in line
    assert "sources=['keyword', 'embedding']" in line
    assert "keyword_score=21" in line
    assert "embedding_score=0.82" in line
    assert "embedding_provider=hash" in line
    assert "embedding_status=available" in line


def test_format_rag_retrieval_trace_lines_with_empty_chunks():
    lines = format_rag_retrieval_trace_lines([])

    assert lines == ["- RAG 检索片段数：0"]
