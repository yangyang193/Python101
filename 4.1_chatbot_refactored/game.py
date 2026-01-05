from api import call_zhipu_api

def play_round(conversation_history, user_input):
    """
    进行一轮游戏对话
    
    参数：
        conversation_history: 对话历史列表
        user_input: 用户输入
    
    返回：
        AI的回复内容
    """
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API获取回复
    result = call_zhipu_api(conversation_history)
    assistant_reply = result['choices'][0]['message']['content']
    
    # 添加AI回复到历史
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    return assistant_reply

