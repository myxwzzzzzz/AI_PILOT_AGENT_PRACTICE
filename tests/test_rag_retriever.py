import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag_retriever import (
    extract_query_terms,
    retrieve_relevant_chunks,
    format_retrieved_context,
)


test_queries = [
    "MA5-MA10 策略适合震荡行情吗？",
    "收益率参数扫描图表应该调用什么工具？",
    "如果用户问最大回撤，sort_by 应该是什么？",
    "随便聊聊天"
]


for query in test_queries:
    print("=" * 80)
    print("用户问题：", query)

    terms = extract_query_terms(query)
    print("提取关键词：", terms)

    chunks = retrieve_relevant_chunks(
        query=query,
        top_k=3,
        min_score=1,
    )

    print("检索结果数量：", len(chunks))

    for chunk in chunks:
        print("-" * 80)
        print("score:", chunk["score"])
        print("chunk_id:", chunk["chunk_id"])
        print("source:", chunk["source"])
        print("text:")
        print(chunk["text"])

    print("\n格式化后的 RAG 上下文：")
    print(format_retrieved_context(chunks))