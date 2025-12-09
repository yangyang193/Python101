import requests
import json

from requests.utils import stream_decode_response_unicode

try:
    from config import ZHIPU_API_KEY
except ImportError:
    ZHIPU_API_KEY = "你的智谱AI_API_KEY"

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": ZHIPU_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

role_system = "你所有的回答都要扮演成一个疯狂的小丑"
user_input = input("请输入你要说的话：")

messages = [
    {
      "role": "user",
      "content": role_system + user_input
    }
]

result = call_zhipu_api(messages)
print(result['choices'][0]['message']['content'])