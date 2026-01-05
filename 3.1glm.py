import requests
import random
import os


def call_zhipu_api(messages, model="glm-4-flash"):
    # 从环境变量读取API密钥，如果没有则使用默认值（请替换为你的密钥）
    api_key = os.getenv("ab16c0b7809545e99d60ae7b73023ba4.YwWPxLoEG60CWy6k")
    
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ API调用失败: 状态码 {response.status_code}")
            print(f"错误信息: {response.text}")
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求异常: {e}")
        raise


role_system = ["保安", "保镖"]
current_role = random.choice(role_system)

print("=" * 50)
print("🎮 谁是卧底游戏开始！")
print(f"💡 提示：角色可能是 {role_system[0]} 或 {role_system[1]}")
print("=" * 50)
print()

game_system = f"""你正在玩"谁是卧底"游戏。你的身份是：{current_role}

游戏规则：
1. 用户会通过提问来猜测你的身份
2. 你要通过描述自己的特征、感受、处境来暗示，但绝对不能直接说出"{current_role}"这个词
3. 不要直接回答"是"或"否"，而是通过描述特征让用户自己判断
4. 不要说"我不是XX"这种直接否定，而是说"我更像是..."来描述
5. 不要提及其他可能的身份选项
6. 当用户准确说出"{current_role}"这个词时，你只回复"再见"来结束游戏
7. 保持神秘感，让游戏有趣
"""

conversation_history = [
    {"role": "system", "content": game_system}
]

while True:
    try:
        user_input = input("请输入你要说的话：")
        
        if not user_input.strip():
            print("⚠️ 请输入有效内容！")
            continue
        
        conversation_history.append({"role": "user", "content": user_input})
        
        print("🤔 正在思考...")
        result = call_zhipu_api(conversation_history)
        
        if 'choices' not in result or len(result['choices']) == 0:
            print("⚠️ API返回格式异常，未找到回复内容")
            print(f"返回结果: {result}")
            continue
        
        assistant_reply = result['choices'][0]['message']['content']
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        print(f"\n🤖 机器人回复：{assistant_reply}\n")
        
        if "再见" in assistant_reply:
            print(f"\n🎉 游戏结束！正确答案是：{current_role}")
            break
            
    except KeyboardInterrupt:
        print("\n\n👋 游戏已退出")
        break
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("请检查网络连接和API密钥是否有效")
        retry = input("\n是否重试？(y/n): ")
        if retry.lower() != 'y':
            break
