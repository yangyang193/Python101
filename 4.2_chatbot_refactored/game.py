import sys
import os

from api import call_zhipu_api

# 导入TTS功能（从上级目录）
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from xunfei_tts import text_to_speech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ 警告: 未找到 xunfei_tts 模块，TTS功能将不可用")

def play_round(conversation_history, user_input, enable_tts=True):
    """
    进行一轮游戏对话
    
    参数：
        conversation_history: 对话历史列表
        user_input: 用户输入
        enable_tts: 是否启用TTS语音播放
    
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
    
    # 打印回复
    print(f"\n🤖 AI回复: {assistant_reply}\n")
    
    # 使用TTS播放AI的回复（如果启用且可用）
    if enable_tts and TTS_AVAILABLE:
        try:
            print("🔊 正在生成并播放语音，请稍候...")
            text_to_speech(assistant_reply)
            print("✅ 语音播放完成\n")
        except Exception as e:
            print(f"⚠️ 语音播放失败: {e}")
            import traceback
            traceback.print_exc()
    
    return assistant_reply

