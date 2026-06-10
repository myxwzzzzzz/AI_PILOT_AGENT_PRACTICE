import os

from config import ensure_output_dirs

from file_inspector import describe_file_type
from router import route_task
from response_formatter import format_response
from logger import write_tool_log, read_recent_logs
from tool_registry import list_available_tools
from trace_formatter import format_trace
from llm_tool_selector import select_tool
from llm_router import route_llm_tool_call
from llm_agent_runner import run_llm_agent_task
from llm_health_check import (
    check_deepseek_connection,
    format_llm_health_check_result,
)

def print_available_tools() -> None:
    """
    打印当前系统已注册的工具。
    """
    tools = list_available_tools()

    print("\nAI 助手回复：")
    print("当前已注册工具如下：")

    for idx, tool in enumerate(tools, start=1):
        print(f"\n[{idx}] {tool['name']}")
        print(f"用途：{tool['description']}")
        print(f"适用数据：{tool['required_file_type_name']}")
        print(f"触发关键词：{', '.join(tool['keywords'])}")

def is_switch_file_command(user_input: str) -> bool:
    """
    判断用户是否想切换当前数据文件。
    """
    keywords = ["切换文件", "使用文件", "换成文件", "更换文件"]
    return any(keyword in user_input for keyword in keywords)


def extract_file_path(user_input: str) -> str:
    """
    从用户输入中提取文件路径。

    支持示例：
    - 切换文件 data/channel_data.csv
    - 使用文件 data/channel_data_new.csv
    - 换成文件 data/test.csv
    """
    keywords = ["切换文件", "使用文件", "换成文件", "更换文件"]

    file_path = user_input

    for keyword in keywords:
        file_path = file_path.replace(keyword, "")

    return file_path.strip()


def print_recent_logs(limit: int = 5) -> None:
    """
    打印最近 N 条工具调用日志。
    """
    log_result = read_recent_logs(limit=limit)

    print("\nAI 助手回复：")

    if not log_result.get("logs"):
        print(log_result.get("message", "暂无工具调用日志"))
        return

    print(f"最近 {limit} 条工具调用日志：")

    for idx, log in enumerate(log_result["logs"], start=1):
        print(f"\n[{idx}]")
        print(f"时间：{log.get('timestamp')}")
        print(f"用户输入：{log.get('user_input')}")
        print(f"使用文件：{log.get('file_path')}")
        print(f"选择工具：{log.get('selected_tool')}")
        print(f"路由是否成功：{log.get('success')}")
        print(f"工具是否成功：{log.get('tool_success')}")

        if log.get("output_path"):
            print(f"输出文件：{log.get('output_path')}")

        if log.get("error"):
            print(f"错误信息：{log.get('error')}")

        if log.get("tool_error"):
            print(f"工具错误：{log.get('tool_error')}")


def main():
    ensure_output_dirs()
    
    current_file_path = "data/channel_data.csv"
    show_trace = False
    use_llm_mode = False
    llm_selector_mode = "mock"
    use_rag_mode = False

    print("=" * 80)
    print("AI Pilot 数据分析助手已启动")
    print(f"当前默认数据文件：{current_file_path}")
    print(describe_file_type(current_file_path))
    print()
    print("你可以尝试输入：")
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
    print("12. 查看轨迹")
    print("14. 运行均线策略回测")
    print("15. 生成回测报告")
    print("16. 扫描均线参数")
    print("17. 生成参数扫描报告")
    print("18. 生成策略研究总结报告")
    print("19. 生成 MA5-MA10 回测图表")
    print("20. 生成参数扫描图表")
    print("输入 开启LLM模式，可以使用模拟 LLM Tool Calling 路由")
    print("输入 关闭LLM模式，可以恢复规则路由")
    print()
    print("输入 exit、quit 或 退出 可以结束程序")
    print("=" * 80)

    while True:
        user_input = input("\n请输入你的问题：").strip()

        if user_input.lower() in ["exit", "quit"] or user_input in ["退出", "结束"]:
            print("\nAI 助手已退出。")
            break

        # 查看工具调用日志
        if user_input in ["查看日志", "最近日志", "工具日志"]:
            print_recent_logs(limit=5)
            continue

        if user_input in ["开启LLM模式", "开启 LLM 模式", "打开LLM模式", "打开 LLM 模式"]:
            use_llm_mode = True
            print("\n已开启 LLM 模式。后续任务将走 mock_llm_tool_selector → llm_router。")
            continue

        if user_input in ["关闭LLM模式", "关闭 LLM 模式", "退出LLM模式", "退出 LLM 模式"]:
            use_llm_mode = False
            print("\n已关闭 LLM 模式。后续任务将恢复使用规则 router。")
            continue

        if user_input in ["使用Mock LLM", "使用mock LLM", "使用模拟LLM", "使用模拟 LLM"]:
            llm_selector_mode = "mock"
            print("\n已切换为 mock LLM selector。")
            continue

        if user_input in ["使用真实LLM", "使用真实 LLM", "使用Real LLM", "使用real LLM"]:
            llm_selector_mode = "real"
            print("\n已切换为 real LLM selector。后续任务会调用deepseek来完成。")
            continue

        if user_input in ["开启RAG模式", "开启 RAG 模式", "打开RAG模式", "打开 RAG 模式"]:
            use_rag_mode = True
            print("\n已开启 RAG 模式。后续 LLM 模式会检索 documents/ 中的相关知识片段。")
            continue

        if user_input in ["关闭RAG模式", "关闭 RAG 模式", "退出RAG模式", "退出 RAG 模式"]:
            use_rag_mode = False
            print("\n已关闭 RAG 模式。")
            continue

        if user_input in ["查看工具", "工具列表", "可用工具"]:
            print_available_tools()
            continue

        if user_input in ["开启轨迹", "显示轨迹", "打开轨迹"]:
            show_trace = True
            print("\nAI 助手回复：")
            print("已开启工具调用轨迹显示。")
            continue

        if user_input in ["检查LLM连接", "检查 LLM 连接", "测试LLM连接", "测试 LLM 连接"]:
            result = check_deepseek_connection()
            print(format_llm_health_check_result(result))
            continue

        if user_input in ["关闭轨迹", "隐藏轨迹", "关掉轨迹"]:
            show_trace = False
            print("\nAI 助手回复：")
            print("已关闭工具调用轨迹显示。")
            continue

        # 处理切换文件命令
        if is_switch_file_command(user_input):
            new_file_path = extract_file_path(user_input)

            print("\nAI 助手回复：")

            if not new_file_path:
                print("请提供要切换的数据文件路径，例如：切换文件 data/channel_data.csv")
                continue

            if not os.path.exists(new_file_path):
                print(f"文件不存在：{new_file_path}")
                print("请检查路径是否正确。")
                continue

            current_file_path = new_file_path
            print(f"已切换当前数据文件为：{current_file_path}")
            print(describe_file_type(current_file_path))
            continue
        

        # 普通任务：路由 → 工具执行 → 格式化回复 → 写日志

        print(f"[DEBUG] use_llm_mode={use_llm_mode}, llm_selector_mode={llm_selector_mode}, use_rag_mode={use_rag_mode}")
        
        if use_llm_mode:
            route_result = run_llm_agent_task(
                user_input=user_input,
                file_path=current_file_path,
                selector_mode=llm_selector_mode,
                fallback_to_mock=True,
                fallback_to_rule=True,
                use_rag=use_rag_mode,
                rag_top_k=3,
            )
        else:
            route_result = route_task(user_input, current_file_path)

        response = format_response(route_result)

        write_tool_log(
            user_input=user_input,
            file_path=current_file_path,
            route_result=route_result,
        )

        print("\nAI 助手回复：")
        print(response)

        if show_trace:
            print(format_trace(route_result))


if __name__ == "__main__":
    main()