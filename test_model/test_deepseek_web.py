import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.responses.create(
    model="deepseek-v4-flash",

    input="搜索今天最新的一条 AI 新闻，并告诉我标题和来源。",

    tools=[
        {
            "type": "web_search"
        }
    ],

    tool_choice={
        "type": "web_search"
    }
)


print("最终回答：")
print(response.output_text)

print("\n输出类型：")

for item in response.output:
    print(item.type)