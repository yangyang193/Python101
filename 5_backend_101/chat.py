from api import call_zhipu_api
from roles import get_break_rules

def chat_once(conversation_history, user_input, role_prompt):
    """
    进行一次对话交互
    
    参数：
        conversation_history: 对话历史列表
        user_input: 用户输入
        role_prompt: 角色设定
    
    返回：
        AI的回复内容
    """
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 构造API调用消息
    # 第一个消息是系统提示（角色设定 + 结束规则）
    system_message = role_prompt + "\n\n" + get_break_rules()
    api_messages = [{"role": "system", "content": system_message}] + conversation_history[1:]
    
    # 调用API获取回复
    result = call_zhipu_api(api_messages)
    reply = result['choices'][0]['message']['content']
    
    # 添加AI回复到历史
    conversation_history.append({"role": "assistant", "content": reply})
    
    return reply

