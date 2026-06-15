from rag_retriever import extract_query_terms, format_retrieved_context, retrieve_relevant_chunks


def test_extract_query_terms():
    terms = extract_query_terms("MA5-MA10 策略适合震荡行情吗？")

    assert isinstance(terms, list)
    assert len(terms) > 0


def test_retrieve_relevant_chunks():
    chunks = retrieve_relevant_chunks(
        query="MA5-MA10 策略适合震荡行情吗？",
        top_k=3,
        min_score=1,
    )

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert "score" in chunks[0]
    assert "text" in chunks[0]
    assert chunks[0]["retrieval_mode"] == "keyword"


def test_format_retrieved_context():
    chunks = retrieve_relevant_chunks(
        query="如果用户问最大回撤，sort_by 应该是什么？",
        top_k=3,
        min_score=1,
    )

    context = format_retrieved_context(chunks)

    assert isinstance(context, str)
    assert len(context) > 0
    assert "chunk" in context.lower() or "来源" in context
