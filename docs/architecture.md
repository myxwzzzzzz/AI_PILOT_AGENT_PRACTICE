# 系统架构说明

## 总体流程

```text
用户输入
→ main.py
→ file_inspector.py 识别文件类型
→ tool_registry.py 匹配工具
→ parameter_parser.py 解析参数
→ router.py 校验并执行工具
→ tools.py / finance_tools.py
→ response_formatter.py 输出自然语言回复
→ trace_formatter.py 输出调用轨迹
→ logger.py 记录日志