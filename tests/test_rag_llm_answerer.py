import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag_retriever import retrieve_relevant_chunks
from rag_qa import answer_with_retrieved_context


user_input = "MA5-MA10 策略适合震荡行情吗？"

chunks = retrieve_relevant_chunks(
    query=user_input,
    top_k=3,
    min_score=1,
)

print("检索到的 chunks：")
for chunk in chunks:
    print("-", chunk["chunk_id"], "score=", chunk["score"])


print("\n测试 1：优先使用 LLM 生成 RAG 回答")
result = answer_with_retrieved_context(
    user_input=user_input,
    retrieved_chunks=chunks,
    use_llm_answer=True,
)

print({
    "success": result.get("success"),
    "answer_type": result.get("answer_type"),
    "answer_source": result.get("answer_source"),
    "llm_success": (
        result.get("llm_answer_result") or {}
    ).get("success"),
    "llm_stage": (
        result.get("llm_answer_result") or {}
    ).get("stage"),
    "llm_message": (
        result.get("llm_answer_result") or {}
    ).get("message"),
})

print("\n回答：")
print(result.get("answer"))


print("\n测试 2：关闭 LLM，使用本地规则 fallback")
result = answer_with_retrieved_context(
    user_input=user_input,
    retrieved_chunks=chunks,
    use_llm_answer=False,
)

print({
    "success": result.get("success"),
    "answer_type": result.get("answer_type"),
    "answer_source": result.get("answer_source"),
})

print("\n回答：")
print(result.get("answer"))