def is_game_over(ai_reply, correct_role, user_input):
    """
    判断游戏是否结束
    
    参数：
        ai_reply: AI的回复内容
        correct_role: 正确答案（角色名称）
        user_input: 用户输入
    
    返回：
        True 表示游戏结束，False 表示继续
    """
    # 检查AI是否回复"再见"（表示用户猜对了）
    if "再见" in ai_reply:
        return True
    
    # 检查用户是否直接说出了正确答案
    if correct_role in user_input:
        return True
    
    return False

def should_exit_by_user(user_input):
    """
    判断用户是否想要退出游戏
    
    参数：
        user_input: 用户输入的内容
    
    返回：
        True 表示要退出，False 表示继续
    """
    exit_words = ['退出', '结束', '不玩了', 'exit', 'quit']
    return user_input.strip() in exit_words

