def should_exit_by_user(user_input):
    """
    判断用户是否想要结束对话
    
    参数：
        user_input: 用户输入的内容
    
    返回：
        True 表示要结束，False 表示继续
    """
    exit_words = ['再见', '退出', '结束', 'bye', 'exit']
    return user_input.strip() in exit_words

def should_exit_by_ai(ai_reply):
    """
    判断AI的回复是否表示要结束对话
    
    参数：
        ai_reply: AI的回复内容
    
    返回：
        True 表示要结束，False 表示继续
    """
    # 清理回复：去除空格和标点
    reply_cleaned = ai_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
    
    # 如果回复只包含"再见"或很短且包含"再见"，则认为要结束
    if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
        return True
    return False

