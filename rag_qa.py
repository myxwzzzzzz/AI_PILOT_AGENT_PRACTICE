from rag_retriever import retrieve_relevant_chunks
import os
import time
from rag_llm_answerer import generate_rag_answer_with_llm
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

def answer_with_retrieved_context(
    user_input: str,
    retrieved_chunks: list[dict] | None = None,
    use_llm_answer: bool = True,
) -> dict:
    """
    基于 RAG 检索片段生成一个本地知识问答结果。

    当前版本不调用 LLM，只使用检索到的文档内容做简洁回答。
    后续可以升级为：RAG context + LLM 生成自然语言回答。
    """
    if retrieved_chunks is None:
        retrieved_chunks = retrieve_relevant_chunks(
            query=user_input,
            top_k=3,
            min_score=1,
        )

    if not retrieved_chunks:
        return {
            "success": False,
            "answer_type": "rag_qa",
            "answer": "我没有在本地知识文档中检索到足够相关的内容，因此暂时无法基于项目知识库回答这个问题。",
            "retrieved_chunks": [],
        }
    
    llm_answer_result = None

    if use_llm_answer:
        llm_answer_result = generate_rag_answer_with_llm(
            user_input=user_input,
            retrieved_chunks=retrieved_chunks,
        )

        if llm_answer_result.get("success"):
            return {
                "success": True,
                "answer_type": "rag_qa",
                "answer": llm_answer_result.get("answer"),
                "retrieved_chunks": retrieved_chunks,
                "answer_source": "llm_rag",
                "llm_answer_result": llm_answer_result,
            }

    combined_text = "\n".join(
        chunk.get("text", "")
        for chunk in retrieved_chunks
    )

    # 针对当前项目知识库的轻量规则回答。
    # 注意：这不是最终版本，只是先让 RAG QA 路径跑通。
    if "震荡" in user_input and ("MA5" in user_input.upper() or "MA5-MA10" in user_input.upper()):
        answer = (
            "根据本地策略说明，MA5-MA10 均线策略属于趋势跟随策略。"
            "它在单边上涨行情中可能表现较好，但在震荡行情中可能频繁产生假信号。"
            "因此，它并不特别适合震荡行情；如果在震荡行情中使用，需要重点关注交易次数、最大回撤、"
            "策略收益率是否跑赢买入持有，以及夏普比率等指标。"
        )

    elif "最大回撤" in user_input and "sort_by" in user_input:
        answer = (
            "根据本地 Agent 工具使用说明，当用户关注“最大回撤”时，"
            "参数扫描相关工具的 sort_by 应该使用 max_drawdown。"
        )

    elif "收益率" in user_input and "sort_by" in user_input:
        answer = (
            "根据本地 Agent 工具使用说明，当用户关注“收益率”时，"
            "参数扫描相关工具的 sort_by 可以使用 strategy_total_return。"
        )

    elif "夏普" in user_input and "sort_by" in user_input:
        answer = (
            "根据本地 Agent 工具使用说明，当用户关注“夏普”或夏普比率时，"
            "参数扫描相关工具的 sort_by 可以使用 sharpe_ratio。"
        )

    else:
        top_chunk = retrieved_chunks[0]
        answer = (
            "根据本地知识文档，检索到的最相关内容如下：\n\n"
            f"{top_chunk.get('text', '')}"
        )

    return {
        "success": True,
        "answer_type": "rag_qa",
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
        "answer_source": "local_rule_fallback",
        "llm_answer_result": llm_answer_result,
    }