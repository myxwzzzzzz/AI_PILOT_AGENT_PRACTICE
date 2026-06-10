import os
import json
import time

from openai import OpenAI

from real_llm_tool_selector import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


def check_deepseek_connection() -> dict:
    """
    检查 DeepSeek LLM API 是否可用。

    检查内容：
    - API Key 是否存在；
    - API 是否可连接；
    - 模型是否能返回合法 JSON；
    - 请求耗时。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return {
            "success": False,
            "stage": "api_key_check",
            "message": "未检测到 DEEPSEEK_API_KEY 环境变量。",
            "base_url": DEEPSEEK_BASE_URL,
            "model": DEEPSEEK_MODEL,
        }

    start_time = time.perf_counter()

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL,
            timeout=20.0,
        )

        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格的 JSON 输出助手，只能返回合法 JSON。"
                },
                {
                    "role": "user",
                    "content": '请只返回这个 JSON：{"status":"ok","message":"pong"}'
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0,
            max_tokens=100,
        )

        elapsed_seconds = round(time.perf_counter() - start_time, 3)

        response_text = response.choices[0].message.content

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "success": False,
                "stage": "json_parse",
                "message": "API 已返回内容，但不是合法 JSON。",
                "base_url": DEEPSEEK_BASE_URL,
                "model": DEEPSEEK_MODEL,
                "elapsed_seconds": elapsed_seconds,
                "raw_response": response_text,
            }

        return {
            "success": True,
            "stage": "ok",
            "message": "DeepSeek API 连接正常，模型成功返回合法 JSON。",
            "base_url": DEEPSEEK_BASE_URL,
            "model": DEEPSEEK_MODEL,
            "elapsed_seconds": elapsed_seconds,
            "raw_response": response_text,
            "parsed_response": parsed,
        }

    except Exception as e:
        elapsed_seconds = round(time.perf_counter() - start_time, 3)

        return {
            "success": False,
            "stage": "api_call",
            "message": f"调用 DeepSeek API 失败：{str(e)}",
            "base_url": DEEPSEEK_BASE_URL,
            "model": DEEPSEEK_MODEL,
            "elapsed_seconds": elapsed_seconds,
        }


def format_llm_health_check_result(result: dict) -> str:
    """
    将 LLM 健康检查结果格式化为命令行可读文本。
    """
    lines = []
    lines.append("\nLLM 连接健康检查结果：")
    lines.append(f"- 检查状态：{'通过' if result.get('success') else '失败'}")
    lines.append(f"- 失败/检查阶段：{result.get('stage')}")
    lines.append(f"- 模型供应商：DeepSeek")
    lines.append(f"- Base URL：{result.get('base_url')}")
    lines.append(f"- 模型名称：{result.get('model')}")

    if result.get("elapsed_seconds") is not None:
        lines.append(f"- 请求耗时：{result.get('elapsed_seconds')} 秒")

    lines.append(f"- 说明：{result.get('message')}")

    if result.get("parsed_response") is not None:
        lines.append(f"- 解析结果：{result.get('parsed_response')}")

    if result.get("raw_response") is not None:
        lines.append(f"- 原始返回：{result.get('raw_response')}")

    return "\n".join(lines)