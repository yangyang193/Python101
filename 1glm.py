import requests
import json

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "ab16c0b7809545e99d60ae7b73023ba4.YwWPxLoEG60CWy6k",
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

role_system = "你现在要扮演一个疯子小丑，所有的回答都要像是一首诗"
# 使用示例
messages = [
    {"role": "system", "content": role_system},  # system 角色应该作为独立的消息
    {"role": "user", "content": "请介绍一下你最喜欢的动物是什么"}
]
result = call_zhipu_api(messages)
print(result['choices'][0]['message']['content'])