from roles import get_role_prompt, get_break_rules
from logic import should_exit_by_user, should_exit_by_ai
from chat import chat_once

def main():
    """
    主程序入口
    负责初始化对话历史，运行主循环
    """
    print("欢迎使用聊天机器人！")
    print("输入'再见'可以退出\n")
    
    # 初始化角色设定
    role_prompt = get_role_prompt("小丑")
    
    # 初始化对话历史
    system_message = role_prompt + "\n\n" + get_break_rules()
    conversation_history = [{"role": "system", "content": system_message}]
    
    # 主循环
    while True:
        # 获取用户输入
        user_input = input("你：")
        
        # 检查用户是否要退出
        if should_exit_by_user(user_input):
            print("再见！")
            break
        
        # 进行一次对话
        try:
            reply = chat_once(conversation_history, user_input, role_prompt)
            print(f"AI：{reply}\n")
            
            # 检查AI是否表示要结束
            if should_exit_by_ai(reply):
                print("对话已结束")
                break
                
        except Exception as e:
            print(f"发生错误: {e}")
            break

if __name__ == "__main__":
    main()

