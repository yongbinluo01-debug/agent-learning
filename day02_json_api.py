messages = [
  {"role":"system",
    "content":"你是一个agent助手"
  },
{"role":"user",
"content":"你能帮我写一篇关于人工智能的文章吗？"
}

]
print(messages)
print(messages[0])
print(messages[1]["content"])
import json


json_data = json.dumps(
    messages,
    ensure_ascii=False,
    indent=2
)

print(json_data)


import requests
url = "https://httpbin.org/get"
response = requests.get(url)
get_data = response.json()

print("GET 状态码：", response.status_code)
print("GET URL:", get_data["url"])
print("GET 来源 IP:", get_data["origin"])

post_url = "https://httpbin.org/post"
data = {
      "role": "user",
      "content": "请帮我写一篇关于人工智能的文章"
 }  
post_response = requests.post(
  post_url,
  json=data
)
post_data = post_response.json()

print("POST 状态码：", post_response.status_code)
print("POST 收到的数据：", post_data["json"])


llm_request ={
  "model":"demo-model",
  "messages":[
    {"role":"system",
     "content":"你是一个agent助手"
     },
     {
"role":"user",
      "content":"请用一句话介绍人工智能"
     }
  ]
}
print("准备发送给大模型数据：")
print(
  json.dumps(
    llm_request,
    ensure_ascii=False,
    indent=2
  )
)

fake_response = {
  "id":"123456",
  "model":"demo-model",
"choices":[
  
    {
      "message":{
        "role":"assistant",
        "content":"人工智能是指计算机系统模拟人类智能行为的技术。"
      }
    }
  ]
}
answer = fake_response["choices"][0]["message"]["content"]
print("大模型返回的回答：")
print(answer)

