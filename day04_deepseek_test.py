import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.responses.create(
    model="deepseek-flash",
    input="请用一句话解释什么是 AI Agent"
)

print(response.output_text)