import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

response = client.responses.create(
  model="gpt-5.6-luna",
  input=("请用三句话解释什么是API")
)
print(response.output_text)