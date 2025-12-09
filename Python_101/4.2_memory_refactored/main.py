from datetime import datetime
from memory import load_memory, save_memory
from roles import get_role_prompt, get_break_rules
from logic import should_exit_by_user, should_exit_by_ai
from chat import chat_once

# 全局配置
MEMORY_FILE = "3.1_memory_101/conversation_memory.json"

def main():
    """主程序入口：初始化对话历史，运行主循环，保存记忆"""
    pass

if __name__ == "__main__":
    main()

