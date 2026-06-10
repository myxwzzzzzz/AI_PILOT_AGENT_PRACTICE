import os
import time

from openai import OpenAI

from rag_retriever import format_retrieved_context
from real_llm_tool_selector import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


def build_rag_answer_prompt(
    user_input: str,
    retrieved_chunks: list[dict],
) -> str:
    """
    构造 RAG 知识问答 prompt。

    注意：
    - 这里不是让 LLM 选工具；
    - 而是让 LLM 基于检索到的本地文档片段回答问题。
    """
    retrieved_context = format_retrieved_context(retrieved_chunks)

    prompt = f"""
你是一个 AI Pilot 项目的 RAG 知识问答助手。

你的任务是基于“本地知识文档片段”回答用户问题。

请严格遵守：

1. 只能根据给定的本地知识文档片段回答；
2. 不要编造文档里没有的信息；
3. 如果文档信息不足，请明确说明“本地知识库信息不足”；
4. 回答要简洁、清楚、偏实用；
5. 如果问题涉及策略适用性，请说明适合什么场景、不适合什么场景，以及需要关注哪些指标；
6. 不要输出 Markdown 表格；
7. 不要调用工具；
8. 不要生成 JSON；
9. 直接输出中文自然语言答案。

用户问题：

{user_input}

本地知识文档片段：

{retrieved_context}

请基于以上文档片段回答用户问题。
"""

    return prompt.strip()


def generate_rag_answer_with_llm(
    user_input: str,
    retrieved_chunks: list[dict],
) -> dict:
    """
    使用 DeepSeek 基于 RAG 检索片段生成回答。

    如果 API 不可用，返回 success=False，交给上层 fallback。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return {
            "success": False,
            "stage": "api_key_check",
            "message": "未检测到 DEEPSEEK_API_KEY，无法调用 DeepSeek 生成 RAG 回答。",
            "provider": "deepseek",
            "model": DEEPSEEK_MODEL,
        }

    if not retrieved_chunks:
        return {
            "success": False,
            "stage": "retrieval_check",
            "message": "没有可用于生成回答的 RAG 检索片段。",
            "provider": "deepseek",
            "model": DEEPSEEK_MODEL,
        }

    prompt = build_rag_answer_prompt(
        user_input=user_input,
        retrieved_chunks=retrieved_chunks,
    )

    start_time = time.perf_counter()

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL,
            timeout=30.0,
        )

        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格基于本地文档片段回答问题的 RAG 助手。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=800,
        )

        elapsed_seconds = round(time.perf_counter() - start_time, 3)
        answer = response.choices[0].message.content.strip()

        return {
            "success": True,
            "stage": "ok",
            "answer": answer,
            "provider": "deepseek",
            "model": DEEPSEEK_MODEL,
            "elapsed_seconds": elapsed_seconds,
            "raw_response": answer,
        }

    except Exception as e:
        elapsed_seconds = round(time.perf_counter() - start_time, 3)

        return {
            "success": False,
            "stage": "api_call",
            "message": f"调用 DeepSeek 生成 RAG 回答失败：{str(e)}",
            "provider": "deepseek",
            "model": DEEPSEEK_MODEL,
            "elapsed_seconds": elapsed_seconds,
        }