from pathlib import Path

from rag_document_loader import build_document_chunks, list_document_files
from rag_retriever import retrieve_relevant_chunks
from rag_retrieval_router import retrieve_chunks


def test_list_document_files_can_prefilter_by_source_name():
    files = list_document_files(source_filter=["risk_metrics_notes.md"])
    file_names = {path.name for path in files}

    assert file_names == {"risk_metrics_notes.md"}


def test_build_document_chunks_can_prefilter_by_source_name():
    chunks = build_document_chunks(source_filter=["risk_metrics_notes.md"])

    assert chunks
    assert all(Path(chunk["source"]).name == "risk_metrics_notes.md" for chunk in chunks)


def test_keyword_retriever_uses_source_filter_before_scoring():
    chunks = retrieve_relevant_chunks(
        query="最大回撤是什么意思",
        top_k=5,
        min_score=1,
        source_filter=["risk_metrics_notes.md"],
    )

    assert chunks
    assert all(Path(chunk["source"]).name == "risk_metrics_notes.md" for chunk in chunks)


def test_retrieve_chunks_with_skill_uses_prefiltered_scope():
    chunks = retrieve_chunks(
        query="最大回撤是什么意思",
        top_k=3,
        min_score=1,
        mode="keyword",
        skill_name="stock_metrics_skill",
    )

    assert chunks
    assert all(chunk["rag_retrieval_scope"] == "skill_documents_prefiltered" for chunk in chunks)
    assert all(chunk["rag_skill_name"] == "stock_metrics_skill" for chunk in chunks)
    assert all(chunk["skill_document_match"] is True for chunk in chunks)


def test_retrieve_chunks_with_skill_can_still_disable_global_fallback():
    chunks = retrieve_chunks(
        query="一个故意很难匹配到本地知识库的随机问题xyz",
        top_k=3,
        min_score=999,
        mode="keyword",
        skill_name="stock_metrics_skill",
        fallback_to_global=False,
    )

    assert chunks == []
