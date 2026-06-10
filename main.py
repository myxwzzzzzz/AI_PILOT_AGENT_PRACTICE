from cli_state import AppState
from cli_command_handler import handle_cli_command, format_current_file_info

from config import ensure_output_dirs
from router import route_task
from llm_agent_runner import run_llm_agent_task
from response_formatter import format_response
from trace_formatter import format_trace
from logger import write_tool_log


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
    print("20. 使用真实LLM")
    print("21. 开启RAG模式")
    print("22. 检查LLM连接")
    print("23. MA5-MA10 策略适合震荡行情吗？")
    print("\n输入 exit、quit 或 退出 可以结束程序")
    print("=" * 80)


def run_agent_task(user_input: str, state: AppState) -> dict:
    """
    根据当前模式运行任务。

    - 规则模式：route_task
    - LLM 模式：run_llm_agent_task
    """
    if state.use_llm_mode:
        return run_llm_agent_task(
            user_input=user_input,
            file_path=state.current_file_path,
            selector_mode=state.llm_selector_mode,
            fallback_to_mock=True,
            fallback_to_rule=True,
            use_rag=state.use_rag_mode,
            rag_top_k=3,
        )

    return route_task(
        user_input=user_input,
        file_path=state.current_file_path,
    )


def main() -> None:
    ensure_output_dirs()

    state = AppState(
        current_file_path="data/channel_data.csv",
        show_trace=False,
        use_llm_mode=False,
        llm_selector_mode="mock",
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