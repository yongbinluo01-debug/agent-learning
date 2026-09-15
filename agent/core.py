import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from agent.tools import (
    TOOLS,
    search_tool,
    read_url_tool,
    calculator_tool,
)


# =========================
# 1. 基础配置
# =========================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError(
        "没有读取到 DEEPSEEK_API_KEY，请检查 .env"
    )


client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


MODEL = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-flash"
)


# =========================
# 2. 执行 Tool
# =========================

def execute_tool(tool_name, arguments):

    if tool_name == "search_tool":
        return search_tool(
            arguments["query"]
        )

    elif tool_name == "read_url_tool":
        return read_url_tool(
            arguments["url"]
        )

    elif tool_name == "calculator_tool":
        return calculator_tool(
            arguments["expression"]
        )

    else:
        return f"未知工具：{tool_name}"

# =========================
# 3. Agent Loop
# =========================

def run_agent(user_input, history):

    # 复制一份历史记录，
    # 避免直接修改外部 history
    conversation = history.copy()

    # 加入用户当前的问题
    conversation.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # 最多允许 Agent 连续执行 8 步
    max_steps = 8

    for step in range(max_steps):

        print(
            f"\n--- Agent Step {step + 1} ---"
        )


        # =========================
        # 让 DeepSeek 判断下一步
        # =========================

        response = client.responses.create(
            model=MODEL,
            input=conversation,
            tools=TOOLS,
            max_output_tokens=1000
        )


        function_calls = []

        # 查找模型返回的 function_call
        for item in response.output:

            if item.type == "function_call":
                function_calls.append(item)


        # =========================
        # 没有 Tool Call
        # = 模型已经准备最终回答
        # =========================

        if not function_calls:

            answer = response.output_text

            if not answer:
                return "模型没有返回文字内容。"

            return answer


        # =========================
        # 把模型本轮输出加入上下文
        # =========================

        for item in response.output:

            conversation.append(
                item.model_dump(
                    exclude_none=True
                )
            )


        # =========================
        # 执行模型要求的所有工具
        # =========================

        tool_outputs = []

        for item in function_calls:

            tool_name = item.name

            try:

                arguments = json.loads(
                    item.arguments
                )

            except json.JSONDecodeError:

                arguments = {}


            print(
                "模型决定调用：",
                tool_name
            )

            print(
                "模型生成参数：",
                arguments
            )


            try:

                result = execute_tool(
                    tool_name,
                    arguments
                )

            except Exception as error:

                result = (
                    f"工具执行失败：{error}"
                )


            print("工具执行完成。")

            if tool_name == "search_tool":
                print("已获取搜索结果。")

            elif tool_name == "read_url_tool":
                print("已成功读取网页正文。")

            elif tool_name == "calculator_tool":
                print("计算结果：", result)


            # 把工具执行结果与 call_id 对应起来
            tool_output = {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": str(result)
            }

            tool_outputs.append(
                tool_output
            )


        # =========================
        # 把所有工具结果加入上下文
        # =========================

        conversation.extend(
            tool_outputs
        )


        # 然后 for loop 会再次调用 DeepSeek
        #
        # DeepSeek 会看到：
        #
        # 用户问题
        # ↓
        # 自己刚才发出的 function_call
        # ↓
        # Python 返回的 function_call_output
        # ↓
        # 决定下一步


    return (
        "Agent 执行步骤超过限制，已停止。"
    )