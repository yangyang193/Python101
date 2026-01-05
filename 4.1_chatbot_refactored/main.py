from roles import select_random_role, get_game_system_prompt
from logic import is_game_over, should_exit_by_user
from game import play_round

def main():
    """
    主程序入口
    负责初始化游戏，运行主循环
    """
    print("=" * 50)
    print("欢迎来到'谁是卧底'游戏！")
    print("=" * 50)
    print("\n游戏规则：")
    print("我会随机选择一个身份（小丑或人质）")
    print("你需要通过提问来猜测我的身份")
    print("我会通过描述特征来暗示，但不会直接说出答案")
    print("当你猜对时，我会说'再见'，游戏结束")
    print("输入'退出'可以随时退出游戏\n")
    
    # 随机选择角色
    current_role = select_random_role()
    
    # 生成游戏系统提示词
    game_system = get_game_system_prompt(current_role)
    
    # 初始化对话历史
    conversation_history = [
        {"role": "system", "content": game_system}
    ]
    
    # 主循环
    while True:
        # 获取用户输入
        user_input = input("请输入你要说的话：")
        
        # 检查用户是否要退出
        if should_exit_by_user(user_input):
            print(f"\n游戏结束！正确答案是：{current_role}")
            break
        
        # 进行一轮游戏
        try:
            assistant_reply = play_round(conversation_history, user_input)
            print(assistant_reply)
            
            # 检查游戏是否结束
            if is_game_over(assistant_reply, current_role, user_input):
                print(f"\n游戏结束！正确答案是：{current_role}")
                break
                
        except Exception as e:
            print(f"发生错误: {e}")
            break

if __name__ == "__main__":
    main()

