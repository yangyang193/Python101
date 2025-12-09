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

# 使用示例
role_system = ["你所有的回答都要扮演成一个疯狂的小丑", "你是一个被小丑绑架的人，但不敢说真话"]
import random
current_role = random.choice(role_system)
break_message = "当我对你表达结束对话的意图时，你只回复我“再见”，不要有其他任何回答。"
# 多轮对话循环，直到用户输入 '再见' 结束
while True:  # 表示“当条件为真时一直循环”。由于 True 永远为真，这个循环会一直运行，直到遇到 break 才会停止。
    user_input = input("请输入你要说的话：")
    messages = [
        {"role": "user", "content": break_message + current_role + user_input}
    ]
    result = call_zhipu_api(messages)
    assistant_reply = result['choices'][0]['message']['content']
    print(assistant_reply)
    if "再见" in assistant_reply:
        break
    
