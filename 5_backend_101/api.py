import requests
import os
import sys

from requests.utils import stream_decode_response_unicode

# 尝试从环境变量或config导入API密钥
try:
    # 先尝试从环境变量获取
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    
    # 如果环境变量没有，尝试从上级目录的api.py或config导入
    if not ZHIPU_API_KEY:
        # 添加父目录到路径
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        # 尝试从config导入
        try:
            from config import ZHIPU_API_KEY
        except ImportError:
            # 使用默认值（从4.2_clonebot.py中提取）
            ZHIPU_API_KEY = "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU"
except:
    # 如果都失败，使用默认值
    ZHIPU_API_KEY = "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU"

def call_zhipu_api(messages, model="glm-4-flash"):
    """
    调用智谱API获取AI回复
    
    参数：
        messages: 对话消息列表，格式：[{"role": "user", "content": "..."}]
        model: 模型名称，默认为 "glm-4-flash"
    
    返回：
        API返回的JSON数据（字典格式）
    """
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

