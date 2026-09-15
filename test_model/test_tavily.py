import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

client = TavilyClient(
    api_key=api_key
)

response = client.search(
    query="今天最新的 AI 新闻",
    search_depth="basic",
    max_results=3
)

for item in response["results"]:
    print("标题：", item["title"])
    print("链接：", item["url"])
    print("摘要：", item["content"])
    print("-" * 50)