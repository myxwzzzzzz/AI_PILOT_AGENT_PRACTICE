from file_inspector import detect_file_type
from mock_llm_tool_selector import mock_select_tool
from real_llm_tool_selector import real_select_tool
from rag_retriever import format_retrieved_context
from rag_retrieval_router import retrieve_chunks

SUPPORTED_SELECTOR_MODES = ["mock", "real"]


def build_current_file_info(file_path: str | None) -> dict:
    """
    构造传给 LLM Selector 的当前文件信息。

    mock selector 当前不依赖这个信息；
    real selector 后续会把这个信息放进 prompt。
    """
    if not file_path:
        return {}

    file_info = detect_file_type(file_path)

    return {
        "file_path": file_path,
        "file_type": file_info.get("file_type"),
        "file_type_name": file_info.get("file_type_name"),
        "columns": file_info.get("columns", []),
    }


def select_tool(
    user_input: str,
    file_path: str | None = None,
    mode: str = "mock",
    use_rag: bool = False,
    rag_top_k: int = 3,
) -> dict:
    """
    统一 LLM Tool Selector 入口。

    mode:
    - mock：使用规则模拟 LLM Tool Calling
    - real：使用真实 LLM Selector，占位版本暂不调用 API
    """
    current_file_info = build_current_file_info(file_path)
    retrieved_chunks = []
    retrieved_context = None

    if use_rag:
        retrieved_chunks = retrieve_chunks(
           query=user_input,
           top_k=rag_top_k,
           min_score=1,
           mode="keyword",
    )
        retrieved_context = format_retrieved_context(retrieved_chunks)

    if mode == "mock":
        result = mock_select_tool(user_input)

    elif mode == "real":
        result = real_select_tool(
            user_input=user_input,
            current_file_info=current_file_info,
            retrieved_context=retrieved_context,
        )

    else:
        result = {
            "tool_name": None,
            "arguments": {},
            "reason": f"不支持的 selector mode：{mode}"
        }

    result["selector_mode"] = mode
    result["current_file_info"] = current_file_info
    result["use_rag"] = use_rag
    result["retrieved_chunks"] = retrieved_chunks

    return result