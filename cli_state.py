from dataclasses import dataclass


@dataclass
class AppState:
    """
    CLI 主程序运行状态。

    这些变量原来散落在 main.py 中，现在统一放到 AppState 里。
    """
    current_file_path: str = "data/channel_data.csv"
    show_trace: bool = False
    use_llm_mode: bool = False
    llm_selector_mode: str = "mock"
    use_rag_mode: bool = False