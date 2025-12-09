import requests
import json
import random

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

# 游戏设置
role_system = ["小丑", "人质"]
current_role = random.choice(role_system)

# 系统提示词
game_system = f"""你正在玩"谁是卧底"游戏。你的身份是：{current_role}

游戏规则：
1. 用户会通过提问来猜测你的身份
2. 你要通过描述自己的特征、感受、处境来暗示，但绝对不能直接说出"{current_role}"这个词
3. 不要直接回答"是"或"否"，而是通过描述特征让用户自己判断
4. 不要说"我不是XX"这种直接否定，而是说"我更像是..."来描述
5. 不要提及其他可能的身份选项
6. 当用户准确说出"{current_role}"这个词时，你只回复"再见"来结束游戏
7. 保持神秘感，让游戏有趣

回答示例：
- 如果你是"人质"，用户问"你是小丑吗？"
  好的回答："我现在的处境可不太妙，我需要被救援..."
  坏的回答："不是小丑，我是人质" 或 "既不是小丑也不是人质"

- 如果你是"小丑"，用户问"你是人质吗？"  
  好的回答："我喜欢表演，喜欢让别人笑..."
  坏的回答："不是人质，我是小丑" 或 "我不是人质"

现在开始游戏，用户会开始提问。保持角色，通过描述特征来暗示，不要直接否定或肯定。"""

# 维护对话历史
conversation_history = [
    {"role": "system", "content": game_system}
]

# 多轮对话循环
while True:
    user_input = input("请输入你要说的话：")
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API
    result = call_zhipu_api(conversation_history)
    assistant_reply = result['choices'][0]['message']['content']
    
    # 添加助手回复到历史
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    # 打印回复
    print(assistant_reply)
    print(conversation_history)
    
    # 检查是否猜对（模型回复"再见"）
    if "再见" in assistant_reply:
        print(f"\n游戏结束！正确答案是：{current_role}")
        break