import requests
import json
import random

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
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
role_system = [
    "你不可是一个人脉广阔的高官，表面十分热情却有许多告人的秘密",
    "你是一个心思缜密不擅长与人争辩的警察",
    "你是一个执着于真相的记者"
]
break_message = "当你判定我描述了真凶为真的时候，你只回复我'游戏结束'，不要有其他任何回答。"

# 随机选择一个角色
current_role = random.choice(role_system)
print(f"当前角色：{current_role}")

# 初始化消息列表，包含 system 角色（明确告诉AI不要以诗歌形式回答）
messages = [
    {"role": "system", "content": "【重要规则】你必须用普通对话的方式回答，禁止使用诗歌、诗句、押韵、分行等文学形式。用正常的口语化对话回答。你的角色是：" + current_role + "。" + break_message}
]

# 多轮对话循环，直到用户输入 '再见' 结束
while True:  # 表示"当条件为真时一直循环"。由于 True 永远为真，这个循环会一直运行，直到遇到 break 才会停止。
    user_input = input("请输入你要说的话：")
    
    # 添加用户消息到对话历史
    messages.append({"role": "user", "content": user_input})
    
    # 调用 API
    result = call_zhipu_api(messages)
    
    # 获取 AI 回复
    assistant_reply = result['choices'][0]['message']['content']
    
    # 打印 AI 回复
    print(assistant_reply)
    
    # 将 AI 回复添加到对话历史
    messages.append({"role": "assistant", "content": assistant_reply})
    
    # 如果 AI 回复中包含"游戏结束"，退出循环
    if "游戏结束" in assistant_reply:
        break
    