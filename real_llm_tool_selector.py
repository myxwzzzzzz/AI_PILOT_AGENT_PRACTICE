import os
import json

from openai import OpenAI

from llm_tool_schema import build_all_llm_tool_schemas


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"


def build_tool_selection_prompt(
        user_input: str, 
        current_file_info: dict | None = None,
        retrieved_context: str | None = None
        ) -> str:
    """
    构造给真实 LLM 的工具选择提示词。
    """
    tool_schemas = build_all_llm_tool_schemas()

    current_file_info = current_file_info or {}
    retrieved_context = retrieved_context or "未启用 RAG，或未检索到相关文档片段。"
    
    prompt = f"""
你是一个 AI Pilot 工具选择助手。

你的任务是判断用户意图，并在需要时从可用工具中选择最合适的一个工具。

请注意：

1. 你只负责判断意图、选择工具和生成参数；
2. 你不要执行工具；
3. 你必须只返回 JSON；
4. 不要返回 Markdown；
5. 不要返回解释性文字；
6. 如果用户是在询问概念、适用性、含义、规则或文档知识，请将 intent_type 设置为 "knowledge_qa"，并且 tool_name 返回 null；
7. 如果用户明确要求执行动作，例如“生成报告”“运行回测”“画图”“扫描参数”“分析数据”，请将 intent_type 设置为 "tool_call"，并选择合适工具；
8. 如果没有合适工具，tool_name 返回 null；
9. arguments 必须是一个 JSON object；
10. 参数必须符合工具 schema；
11. 如果用户没有指定参数，请使用工具 schema 中的默认含义；
12. 当前文件类型会影响工具是否适合，但最终文件类型校验由 Python 系统完成。

当前文件信息：

{json.dumps(current_file_info, ensure_ascii=False, indent=2)}

检索到的相关知识文档片段：

{retrieved_context}

用户输入：

{user_input}

可用工具列表：

{json.dumps(tool_schemas, ensure_ascii=False, indent=2)}

请只返回如下 JSON 格式：

{{
  "intent_type": "knowledge_qa 或 tool_call 或 unknown",
  "tool_name": "工具名称或 null",
  "arguments": {{}},
  "reason": "简短说明为什么这样判断"
}}
"""

    return prompt.strip()


def parse_llm_tool_selection_response(response_text: str) -> dict:
    """
    解析真实 LLM 返回的工具选择结果。
    """
    try:
        result = json.loads(response_text)

        if not isinstance(result, dict):
            return {
                "intent_type": "unknown",
                "tool_name": None,
                "arguments": {},
                "reason": "LLM 返回结果不是 JSON object。"
            }

        return {
            "intent_type": result.get("intent_type", "tool_call"),
            "tool_name": result.get("tool_name"),
            "arguments": result.get("arguments") or {},
            "reason": result.get("reason", "")
        }

    except json.JSONDecodeError:
        return {
            "intent_type": "unknown",
            "tool_name": None,
            "arguments": {},
            "reason": "LLM 返回内容不是合法 JSON。"
        }


def real_select_tool(
        user_input: str, 
        current_file_info: dict | None = None,
        retrieved_context: str | None = None,
        ) -> dict:
    """
    使用 DeepSeek V4-Pro 进行真实 LLM 工具选择。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return {
            "intent_type": "unknown",
            "tool_name": None,
            "arguments": {},
            "reason": "未检测到 DEEPSEEK_API_KEY，请先在环境变量中设置 DeepSeek API Key。"
        }

    prompt = build_tool_selection_prompt(
        user_input=user_input,
        current_file_info=current_file_info,
        retrieved_context=retrieved_context,
    )

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL
        )

        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格的 JSON 工具选择器。你只能输出合法 JSON。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0
        )

        response_text = response.choices[0].message.content

        parsed = parse_llm_tool_selection_response(response_text)

        parsed["raw_response"] = response_text
        parsed["model"] = DEEPSEEK_MODEL
        parsed["provider"] = "deepseek"

        return parsed

    except Exception as e:
        return {
            "intent_type": "unknown",
            "tool_name": None,
            "arguments": {},
            "reason": f"调用 DeepSeek API 失败：{str(e)}"
        }