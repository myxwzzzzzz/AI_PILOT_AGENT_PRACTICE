from cli_state import AppState
from cli_command_handler import handle_cli_command, format_current_file_info

from config import ensure_output_dirs
from router import route_task
from response_formatter import format_response
from trace_formatter import format_trace
from logger import write_tool_log
from workflow_planner import is_workflow_request
from workflow_runner import run_workflow
from file_inspector import detect_file_type
from skill_router import route_skill


def print_startup_message(state: AppState) -> None:
    """
    打印启动说明。
    """
    print("=" * 80)
    print("AI Pilot 数据分析助手已启动")
    print(format_current_file_info(state.current_file_path))

    print("\n你可以尝试输入：")
    print("1. 帮我读取这个 CSV 文件，看看有哪些字段")
    print("2. 帮我看一下这个数据的缺失值和统计信息")
    print("3. 分析一下各渠道转化率，哪个渠道表现最好")
    print("4. 生成一份渠道分析报告")
    print("5. 切换文件 data/channel_data_new.csv")
    print("6. 查看日志")
    print("7. 切换文件 data/stock_price.csv")
    print("8. 读取股票价格数据")
    print("9. 分析风险收益")
    print("10. 生成金融指标报告")
    print("11. 查看工具")
    print("12. 开启轨迹")
    print("13. 运行 MA5-MA10 回测")
    print("14. 生成 MA5-MA10 回测报告")
    print("15. 生成 MA5-MA10 回测图表")
    print("16. 扫描均线参数")
    print("17. 生成参数扫描报告")
    print("18. 生成策略研究总结报告")
    print("19. 开启LLM模式")
    print("20. 使用模拟LLM（离线调试使用")
    print("21. 开启RAG模式")
    print("22. 检查LLM连接")
    print("23. MA5-MA10 策略适合震荡行情吗？")
    print("24. 切换文件 data/stock_price_strategy.csv")
    print("25. 完整分析股票数据，并按夏普比率生成策略研究报告")
    print("26. 查看技能")
    print("\n输入 exit、quit 或 退出 可以结束程序")
    print("=" * 80)


def _get_current_file_type(file_path: str) -> str | None:
    """
    识别当前文件类型，失败时返回 None。
    """
    file_info = detect_file_type(file_path)
    if not file_info.get("success"):
        return None
    return file_info.get("file_type")


def _compact_skill_route(skill_route: dict) -> dict:
    """
    将 skill route 压缩成适合放入 trace 的小结构。
    """
    return {
        "success": skill_route.get("success"),
        "skill_name": skill_route.get("skill_name"),
        "skill_display_name": skill_route.get("skill_display_name"),
        "confidence": skill_route.get("confidence"),
        "reason": skill_route.get("reason"),
        "matched_keywords": skill_route.get("matched_keywords", []),
        "current_file_type": skill_route.get("current_file_type"),
        "required_file_type": skill_route.get("required_file_type"),
        "file_type_compatible": skill_route.get("file_type_compatible"),
    }


def _attach_skill_route(route_result: dict, skill_route: dict) -> dict:
    """
    将 Skill 路由信息附加到任务结果和 trace 中。

    这一步不改变原有工具或 workflow 的执行结果，只增加可观测性。
    """
    if not isinstance(route_result, dict):
        return route_result

    compact_route = _compact_skill_route(skill_route)
    route_result["skill_route"] = compact_route

    trace = route_result.setdefault("trace", {})
    if isinstance(trace, dict):
        trace["skill_route"] = compact_route

    return route_result


def run_agent_task(user_input: str, state: AppState) -> dict:
    """
    根据当前模式运行任务。

    - Workflow 请求：优先交给 workflow runner 执行多步任务
    - LLM 模式：run_llm_agent_task
    - 规则模式：route_task

    Workflow 判断放在 LLM / rule router 之前，是为了让“完整分析 / 综合研究”
    这类多步目标能直接走任务编排，而不是被误分发成某个单步工具。
    """
    current_file_type = _get_current_file_type(state.current_file_path)
    skill_route = route_skill(
        user_input=user_input,
        current_file_type=current_file_type,
    )

    if is_workflow_request(user_input):
        workflow_result = run_workflow(
            user_input=user_input,
            file_path=state.current_file_path,
        )
        return _attach_skill_route(workflow_result, skill_route)

    if state.use_llm_mode:
        from llm_agent_runner import run_llm_agent_task

        llm_result = run_llm_agent_task(
            user_input=user_input,
            file_path=state.current_file_path,
            selector_mode=state.llm_selector_mode,
            fallback_to_mock=True,
            fallback_to_rule=True,
            use_rag=state.use_rag_mode,
            rag_top_k=3,
        )
        return _attach_skill_route(llm_result, skill_route)

    rule_result = route_task(
        user_input=user_input,
        file_path=state.current_file_path,
    )
    return _attach_skill_route(rule_result, skill_route)


def main() -> None:
    ensure_output_dirs()

    state = AppState(
        current_file_path="data/channel_data.csv",
        show_trace=False,
        use_llm_mode=False,
        llm_selector_mode="real",
        use_rag_mode=False,
    )

    print_startup_message(state)

    while True:
        user_input = input("\n请输入你的问题：").strip()

        if not user_input:
            continue

        command_result = handle_cli_command(
            user_input=user_input,
            state=state,
        )

        if command_result.handled:
            if command_result.message:
                print("\nAI 助手回复：")
                print(command_result.message)

            if command_result.should_exit:
                break

            continue

        route_result = run_agent_task(
            user_input=user_input,
            state=state,
        )

        response = format_response(route_result)

        write_tool_log(
            user_input=user_input,
            file_path=state.current_file_path,
            route_result=route_result,
        )

        print("\nAI 助手回复：")
        print(response)

        if state.show_trace:
            print(format_trace(route_result))


if __name__ == "__main__":
    main()