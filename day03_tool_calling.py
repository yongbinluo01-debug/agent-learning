import os
import json
import ast
import operator

from dotenv import load_dotenv
from openai import OpenAI


# =========================
# 1. 基础配置
# =========================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有读取到 OPENAI_API_KEY，请检查 .env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

MODEL = "deepseek-flash"


# =========================
# 2. 自定义计算工具
# =========================

def calculator_tool(expression):
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def calculate(node):

        # 普通数字
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("只支持数字")

        # 例如 100 + 200
        if isinstance(node, ast.BinOp):
            left = calculate(node.left)
            right = calculate(node.right)

            op_type = type(node.op)

            if op_type not in operators:
                raise ValueError("不支持这种运算符")

            return operators[op_type](left, right)

        # 支持 -10 这种负数
        if isinstance(node, ast.UnaryOp):
            value = calculate(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError("不支持的计算表达式")

    tree = ast.parse(
        expression,
        mode="eval"
    )

    return calculate(tree.body)


# =========================
# 3. 告诉模型有哪些工具
# =========================

tools = [
    {
        "type": "web_search"
    },

    {
        "type": "function",
        "name": "calculator_tool",
        "description": "当用户需要进行数学计算时使用这个工具",
        "parameters": {
            "type": "object",

            "properties": {
                "expression": {
                    "type": "string",
                    "description": "需要计算的数学表达式，例如 123 * 456"
                }
            },

            "required": [
                "expression"
            ]
        }
    }
]
# =========================
# 4. Agent Loop
# =========================

def run_agent(user_input, history):

    conversation = history + [
        {
            "role": "user",
            "content": user_input
        }
    ]

    max_steps = 8

    for step in range(max_steps):

        response = client.responses.create(
            model=MODEL,
            input=conversation,
            tools=tools,
            max_output_tokens=500
        )

        tool_outputs = []

        for item in response.output:

            if item.type != "function_call":
                continue

            tool_name = item.name
            arguments = json.loads(item.arguments)

            print("模型决定调用：", tool_name)
            print("模型生成参数：", arguments)

            if tool_name == "calculator_tool":

                try:
                    result = calculator_tool(
                        arguments["expression"]
                    )

                except Exception as error:
                    result = f"计算失败：{error}"

            else:
                result = f"未知工具：{tool_name}"

            print("工具执行结果：", result)

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": str(result)
                }
            )

        # 没有自定义 function_call
        # 普通聊天 / web_search 已经由 DeepSeek 完成
        if not tool_outputs:
            return response.output_text

        # 把模型刚刚产生的 function_call
        # 加回完整上下文
        for item in response.output:
            conversation.append(
                item.model_dump(
                    exclude_none=True
                )
            )

        # 再加入 Python 工具执行结果
        conversation.extend(tool_outputs)

    return "Agent 执行步骤过多，已停止。"
# =========================
# 5. 对话历史
# =========================

history = [
    {
        "role": "system",
        "content": (
            "你是一个有帮助的 AI Agent。"
            "需要最新网络信息时可以使用网页搜索工具，"
            "需要数学计算时可以调用 calculator_tool。"
        )
    }
]


# =========================
# 6. 主程序
# =========================

while True:

    user_input = input(
        "\n请输入任务："
    ).strip()

    # 防止用户直接按 Enter
    if not user_input:
        print("请输入内容。")
        continue

    if user_input == "退出":
        print("Agent 已退出")
        break

    try:

        answer = run_agent(
            user_input,
            history
        )

        print("\nAgent：")
        print(answer)

        # =========================
        # 把这一轮加入聊天历史
        # =========================

        history.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as error:

        print("\nAgent 运行发生错误：")
        print(error)