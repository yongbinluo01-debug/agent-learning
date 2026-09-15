import os

from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

 

def call_llm(message):
    response = client.responses.create(
        model = "gpt-5.6-luna",
        input = message
    )
    return response.output_text


def search_tool(task):
    return f"搜索工具收到任务：{task}"


def calculate_tool(task):
    return f"计算工具收到任务：{task}"


def agent_router(task,messages):
    if "搜索" in task:
        return search_tool(task)

    elif "计算" in task:
        return calculate_tool(task)

    else:
        return call_llm(messages)


messages = [
    {
        "role": "system",
        "content": "你是一个 Agent 助手"
    }
]

while True:
    user_input = input("请输入任务：")

    if user_input == "退出":
        print("Agent 已退出")
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    result = agent_router(user_input, messages)

    messages.append(
        {
            "role": "assistant",
            "content": result
        }
    )

    print("Agent：", result)
    print("\n当前对话历史：")
    for message in messages:
        print(message)
    print("-"*40)