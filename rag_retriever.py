import re
from typing import Optional

from rag_document_loader import build_document_chunks


def normalize_text(text: str) -> str:
    """
    简单文本归一化：
    - 转小写；
    - 去掉多余空白。
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_query_terms(query: str) -> list[str]:
    """
    从用户问题中提取检索关键词。

    当前是轻量实现：
    - 提取英文、数字、下划线组合，例如 ma5、ma10、sort_by；
    - 提取中文连续片段；
    - 对中文片段生成 2~4 字 ngram，提高中文检索召回。
    """
    query = normalize_text(query)

    terms = []

    # 英文 / 数字 / 下划线关键词
    alpha_numeric_terms = re.findall(r"[a-zA-Z0-9_]+", query)
    terms.extend(alpha_numeric_terms)

    # 中文连续片段
    chinese_segments = re.findall(r"[\u4e00-\u9fff]+", query)

    for segment in chinese_segments:
        # 如果中文片段较短，直接加入
        if len(segment) <= 4:
            terms.append(segment)

        # 生成 2~4 字 ngram
        for n in [2, 3, 4]:
            if len(segment) >= n:
                for i in range(len(segment) - n + 1):
                    terms.append(segment[i:i + n])

    # 去重，同时保留顺序
    unique_terms = []
    seen = set()

    for term in terms:
        if term and term not in seen:
            unique_terms.append(term)
            seen.add(term)

    return unique_terms


def score_chunk(query: str, chunk_text: str) -> int:
    """
    计算一个 chunk 与 query 的简单相关性分数。

    分数逻辑：
    - 完整 query 命中，加较高分；
    - 关键词命中，根据关键词长度加分；
    - 较长关键词权重更高。
    """
    normalized_query = normalize_text(query)
    normalized_chunk = normalize_text(chunk_text)

    score = 0

    if normalized_query and normalized_query in normalized_chunk:
        score += 20

    terms = extract_query_terms(query)

    for term in terms:
        if term in normalized_chunk:
            if len(term) >= 4:
                score += 5
            elif len(term) == 3:
                score += 3
            else:
                score += 2

    return score


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 3,
    min_score: int = 1,
    source_filter: Optional[list[str]] = None,
) -> list[dict]:
    """
    根据用户问题检索最相关的文档 chunk。

    当前是关键词检索版，不依赖 embedding。

    source_filter:
        可选的文档名过滤列表。传入后，只会从指定文档构建 chunks 并打分。
        这使 Skill-aware RAG 可以在检索前缩小候选范围。
    """
    chunks = build_document_chunks(source_filter=source_filter)

    scored_chunks = []

    for chunk in chunks:
        score = score_chunk(query, chunk["text"])

        if score >= min_score:
            scored_chunk = {
                **chunk,
                "score": score,
                "retrieval_mode": "keyword",
            }
            scored_chunks.append(scored_chunk)

    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_chunks[:top_k]


def format_retrieved_context(chunks: list[dict]) -> str:
    """
    将检索到的 chunks 格式化成可放进 LLM prompt 的上下文。
    """
    if not chunks:
        return "未检索到相关文档片段。"

    lines = []

    for index, chunk in enumerate(chunks, start=1):
        lines.append(f"[文档片段 {index}]")
        lines.append(f"来源：{chunk['source']}")
        lines.append(f"chunk_id：{chunk['chunk_id']}")
        lines.append(f"相关性分数：{chunk['score']}")
        lines.append("内容：")
        lines.append(chunk["text"])
        lines.append("")

    return "\n".join(lines).strip()
