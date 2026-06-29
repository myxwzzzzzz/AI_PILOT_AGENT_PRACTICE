"""
LLM Agent runner.

This module is the central coordinator for v0.3 Agent execution.

Responsibilities:
1. Run LLM Tool Calling tasks.
2. Route knowledge questions to RAG QA.
3. Manage fallback from real selector to mock selector to rule router.
4. Attach trace metadata for debugging.

This module should not contain low-level data analysis logic.
"""
from rag_retrieval_router import retrieve_chunks
from llm_tool_selector import select_tool
from llm_router import route_llm_tool_call
from router import route_task
from rag_qa import answer_with_retrieved_context

def looks_like_knowledge_question(user_input: str) -> bool:
    """
    判断用户输入是否更像知识问答，而不是工具执行。

    这层是本地 intent guard，用来防止 LLM 或 fallback 把知识性问题误判成工具调用。
    """
    text = user_input.strip()

    action_keywords = [
        "生成",
        "运行",
        "执行",
        "画图",
        "图表",
        "扫描",
        "回测",
        "分析",
        "计算",
        "读取",
        "查看",
    ]

    # 如果用户明确要求执行动作，优先认为是 tool_call
    if any(keyword in text for keyword in action_keywords):
        return False

    direct_knowledge_keywords = [
        "为什么",
        "是什么意思",
        "含义",
        "原理",
        "区别",
        "怎么理解",
        "应该是什么",
        "适用性",
        "优缺点",
        "风险是什么",
    ]

    if any(keyword in text for keyword in direct_knowledge_keywords):
        return True

    # 处理“适合xxx吗 / 是否适合xxx / 适不适合xxx”这类句子
    if "适合" in text and ("吗" in text or "是否" in text or "不适合" in text):
        return True

    # 处理“是什么”类问题
    if "是什么" in text:
        return True

    return False

def should_fallback_after_router_failure(route_result: dict) -> bool:
    """
    判断 LLM 已经选中工具但执行失败时，是否应该 fallback。

    文件类型不匹配属于安全拦截，不建议 fallback 掩盖问题。
    其他情况，例如未知工具、非法参数、工具调用异常，可以尝试 fallback。
    """
    trace = route_result.get("trace", {})

    if trace.get("file_check") == "failed":
        return False

    return True


def add_llm_trace_metadata(
    route_result: dict,
    user_input: str,
    llm_tool_call: dict,
    selector_mode: str,
    fallback_used: bool,
    fallback_steps: list[str],
) -> dict:
    """
    给 LLM Router 的执行结果补充调试信息。
    """
    trace = route_result.setdefault("trace", {})

    trace["user_input"] = user_input
    trace["llm_reason"] = llm_tool_call.get("reason")
    trace["selector_mode"] = llm_tool_call.get("selector_mode", selector_mode)
    trace["fallback_used"] = fallback_used
    trace["fallback_steps"] = fallback_steps
    trace["use_rag"] = llm_tool_call.get("use_rag", False)
    trace["retrieved_chunks"] = llm_tool_call.get("retrieved_chunks", [])
    trace["rag_skill_name"] = llm_tool_call.get("rag_skill_name")
    trace["skill_aware_rag"] = bool(llm_tool_call.get("rag_skill_name"))
    

    return route_result


def add_rule_fallback_trace_metadata(
    route_result: dict,
    fallback_steps: list[str],
) -> dict:
    """
    给旧规则 router 的 fallback 结果补充信息。
    """
    trace = route_result.setdefault("trace", {})

    trace["fallback_used"] = True
    trace["fallback_steps"] = fallback_steps
    trace["fallback_final_route"] = "rule_router"

    return route_result


def run_llm_agent_task(
    user_input: str,
    file_path: str,
    selector_mode: str = "mock",
    fallback_to_mock: bool = True,
    fallback_to_rule: bool = True,
    use_rag: bool = False,
    rag_top_k: int = 3,
    skill_name: str | None = None,
) -> dict:
    """
    运行一次 LLM Agent 任务。

    流程：
    1. 使用指定 selector_mode 选择工具；
    2. 如果选中工具，则交给 llm_router 校验并执行；
    3. 如果真实 LLM 失败，可回退到 mock selector；
    4. 如果 mock selector 也失败，可回退到旧规则 router。
    """
    fallback_steps = []

    # 0. 本地知识问答 guard：明显的知识性问题优先走 RAG QA
    # 这样可以避免 LLM 把“适合吗 / 为什么 / 是什么”误判成工具执行任务。
    if use_rag and looks_like_knowledge_question(user_input):
        from rag_retriever import retrieve_relevant_chunks

        fallback_steps.append("local_intent_guard=knowledge_qa")

        retrieved_chunks = retrieve_chunks(
            query=user_input,
            top_k=rag_top_k,
            min_score=1,
            mode="keyword",
            skill_name=skill_name,
        )

        rag_answer = answer_with_retrieved_context(
            user_input=user_input,
            retrieved_chunks=retrieved_chunks,
        )

        trace = rag_answer.setdefault("trace", {})
        trace["router_type"] = "rag_qa"
        trace["user_input"] = user_input
        trace["selector_mode"] = selector_mode
        trace["intent_type"] = "knowledge_qa"
        trace["llm_reason"] = "本地意图保护规则判断这是知识问答，因此未调用工具选择器。"
        trace["use_rag"] = True
        trace["retrieved_chunks"] = retrieved_chunks
        trace["rag_skill_name"] = skill_name
        trace["skill_aware_rag"] = bool(skill_name)
        trace["rag_answer_source"] = rag_answer.get("answer_source")
        trace["llm_answer_result"] = rag_answer.get("llm_answer_result")
        trace["fallback_used"] = False
        trace["fallback_steps"] = fallback_steps

        return rag_answer

    # 1. 首选 selector
    primary_tool_call = select_tool(
        user_input=user_input,
        file_path=file_path,
        mode=selector_mode,
        use_rag=use_rag,
        rag_top_k=rag_top_k,
        skill_name=skill_name,
    )

    primary_intent_type = primary_tool_call.get("intent_type", "tool_call")
    
    if looks_like_knowledge_question(user_input):
        primary_intent_type = "knowledge_qa"

    fallback_steps.append(
        f"primary_selector={selector_mode}, intent_type={primary_intent_type},tool_name={primary_tool_call.get('tool_name')}"
    )

    if primary_intent_type == "knowledge_qa" and use_rag:
        retrieved_chunks = primary_tool_call.get("retrieved_chunks", [])

        if not retrieved_chunks:
            from rag_retriever import retrieve_relevant_chunks

            retrieved_chunks = retrieve_chunks(
                query=user_input,
                top_k=rag_top_k,
                min_score=1,
                mode="keyword",
            )

        rag_answer = answer_with_retrieved_context(
            user_input=user_input,
            retrieved_chunks=retrieved_chunks,
        )

        trace = rag_answer.setdefault("trace", {})
        trace["router_type"] = "rag_qa"
        trace["user_input"] = user_input
        trace["selector_mode"] = selector_mode
        trace["intent_type"] = primary_intent_type
        trace["llm_reason"] = primary_tool_call.get("reason")
        trace["use_rag"] = True
        trace["retrieved_chunks"] = retrieved_chunks
        trace["rag_skill_name"] = skill_name
        trace["skill_aware_rag"] = bool(skill_name)
        trace["rag_answer_source"] = rag_answer.get("answer_source")
        trace["llm_answer_result"] = rag_answer.get("llm_answer_result")
        trace["fallback_used"] = False
        trace["fallback_steps"] = fallback_steps

        return rag_answer

    if primary_intent_type == "knowledge_qa" and use_rag and primary_tool_call.get("retrieved_chunks"):
        rag_answer = answer_with_retrieved_context(
            user_input=user_input,
            retrieved_chunks=primary_tool_call.get("retrieved_chunks")
        )

        trace = rag_answer.setdefault("trace", {})
        trace["router_type"] = "rag_qa"
        trace["user_input"] = user_input
        trace["selector_mode"] = selector_mode
        trace["intent_type"] = primary_intent_type
        trace["llm_reason"] = primary_tool_call.get("reason")
        trace["use_rag"] = True
        trace["retrieved_chunks"] = primary_tool_call.get("retrieved_chunks")
        trace["fallback_used"] = False
        trace["fallback_steps"] = fallback_steps

        return rag_answer

    if primary_tool_call.get("tool_name"):
        primary_result = route_llm_tool_call(
            llm_tool_call=primary_tool_call,
            file_path=file_path
        )

        primary_result = add_llm_trace_metadata(
            route_result=primary_result,
            user_input=user_input,
            llm_tool_call=primary_tool_call,
            selector_mode=selector_mode,
            fallback_used=False,
            fallback_steps=fallback_steps,
        )

        if primary_result.get("success"):
            return primary_result

        if not should_fallback_after_router_failure(primary_result):
            return primary_result

        fallback_steps.append(
            f"primary_execution_failed={primary_result.get('error') or primary_result.get('tool_result', {}).get('message')}"
        )

    else:
        fallback_steps.append(
            f"primary_no_tool_reason={primary_tool_call.get('reason')}"
        )
        if use_rag and primary_tool_call.get("retrieved_chunks"):
            rag_answer = answer_with_retrieved_context(
                user_input=user_input,
                retrieved_chunks=primary_tool_call.get("retrieved_chunks")
            )

            trace = rag_answer.setdefault("trace", {})
            trace["router_type"] = "rag_qa"
            trace["user_input"] = user_input
            trace["selector_mode"] = selector_mode
            trace["llm_reason"] = primary_tool_call.get("reason")
            trace["use_rag"] = True
            trace["retrieved_chunks"] = primary_tool_call.get("retrieved_chunks")
            trace["fallback_used"] = False
            trace["fallback_steps"] = fallback_steps

            return rag_answer

    # 2. fallback 到 mock selector
    if fallback_to_mock and selector_mode != "mock":
        mock_tool_call = select_tool(
            user_input=user_input,
            file_path=file_path,
            mode="mock",
            use_rag=use_rag,
            rag_top_k=rag_top_k,
        )

        fallback_steps.append(
            f"fallback_selector=mock, tool_name={mock_tool_call.get('tool_name')}"
        )

        if mock_tool_call.get("tool_name"):
            mock_result = route_llm_tool_call(
                llm_tool_call=mock_tool_call,
                file_path=file_path
            )

            mock_result = add_llm_trace_metadata(
                route_result=mock_result,
                user_input=user_input,
                llm_tool_call=mock_tool_call,
                selector_mode="mock",
                fallback_used=True,
                fallback_steps=fallback_steps,
            )

            if mock_result.get("success"):
                return mock_result

            if not should_fallback_after_router_failure(mock_result):
                return mock_result

            fallback_steps.append(
                f"mock_execution_failed={mock_result.get('error') or mock_result.get('tool_result', {}).get('message')}"
            )

        else:
            fallback_steps.append(
                f"mock_no_tool_reason={mock_tool_call.get('reason')}"
            )

    # 3. fallback 到旧规则 router
    if fallback_to_rule:
        fallback_steps.append("fallback_route=rule_router")

        rule_result = route_task(
            user_input=user_input,
            file_path=file_path
        )

        return add_rule_fallback_trace_metadata(
            route_result=rule_result,
            fallback_steps=fallback_steps
        )

    # 4. 全部失败
    return {
        "success": False,
        "error": "LLM Agent 未能选择或执行合适工具，且 fallback 已关闭。",
        "selected_tool": None,
        "trace": {
            "router_type": "llm_agent_runner",
            "user_input": user_input,
            "selector_mode": selector_mode,
            "fallback_used": False,
            "fallback_steps": fallback_steps,
            "execution_status": "failed"
        }
    }