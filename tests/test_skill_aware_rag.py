from skill_aware_rag import (
    annotate_chunks_with_skill_scope,
    chunk_matches_skill_documents,
    filter_chunks_for_skill,
    get_skill_document_names,
)


def test_get_skill_document_names_from_registry():
    documents = get_skill_document_names("stock_strategy_research_skill")

    assert "ma_strategy_notes.md" in documents
    assert "risk_metrics_notes.md" in documents
    assert "agent_tool_usage_notes.md" in documents


def test_get_skill_document_names_for_unknown_skill_returns_empty_list():
    assert get_skill_document_names("unknown_skill") == []


def test_chunk_matches_skill_documents_by_source_filename():
    chunk = {
        "source": "documents/risk_metrics_notes.md",
        "text": "最大回撤用于衡量风险。",
    }

    assert chunk_matches_skill_documents(chunk, ["risk_metrics_notes.md"]) is True
    assert chunk_matches_skill_documents(chunk, ["ma_strategy_notes.md"]) is False


def test_filter_chunks_for_skill_keeps_only_skill_documents():
    chunks = [
        {
            "chunk_id": "risk_metrics_notes.md::chunk_0",
            "source": "documents/risk_metrics_notes.md",
            "text": "最大回撤用于衡量风险。",
            "score": 10,
        },
        {
            "chunk_id": "unrelated.md::chunk_0",
            "source": "documents/unrelated.md",
            "text": "无关内容。",
            "score": 9,
        },
    ]

    filtered = filter_chunks_for_skill(
        chunks,
        skill_name="stock_metrics_skill",
        top_k=3,
    )

    assert len(filtered) == 1
    assert filtered[0]["source"].endswith("risk_metrics_notes.md")
    assert filtered[0]["skill_aware_rag"] is True
    assert filtered[0]["rag_skill_name"] == "stock_metrics_skill"
    assert filtered[0]["rag_retrieval_scope"] == "skill_documents"
    assert filtered[0]["skill_document_match"] is True


def test_annotate_chunks_with_skill_scope_does_not_mutate_input():
    chunks = [
        {
            "chunk_id": "risk_metrics_notes.md::chunk_0",
            "source": "documents/risk_metrics_notes.md",
            "text": "最大回撤用于衡量风险。",
            "score": 10,
        }
    ]

    annotated = annotate_chunks_with_skill_scope(
        chunks,
        skill_name="stock_metrics_skill",
        skill_document_names=["risk_metrics_notes.md"],
        retrieval_scope="global_fallback",
    )

    assert "skill_aware_rag" not in chunks[0]
    assert annotated[0]["skill_aware_rag"] is True
    assert annotated[0]["rag_retrieval_scope"] == "global_fallback"
