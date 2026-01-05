import json
import os

# 记忆文件夹路径（相对于项目根目录）
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "姥姥": "grandma_memory.json"
}

def load_memory(role_name, memory_folder=None):
    """
    加载角色的外部记忆文件
    
    参数：
        role_name: 角色名称
        memory_folder: 记忆文件夹路径（如果为None，使用默认路径）
    
    返回：
        记忆内容字符串，如果加载失败返回空字符串
    """
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if not memory_file:
        return memory_content
    
    # 确定记忆文件夹路径
    if memory_folder is None:
        # 从当前文件位置向上两级找到项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        memory_folder = os.path.join(parent_dir, MEMORY_FOLDER)
    
    memory_path = os.path.join(memory_folder, memory_file)
    
    try:
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                if isinstance(data, list):
                    # 提取所有 content 字段，每句换行
                    contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                    memory_content = '\n'.join(contents)
                # 处理字典格式：{ "content": "..." }
                elif isinstance(data, dict):
                    memory_content = data.get('content', str(data))
                else:
                    memory_content = str(data)
                
                if memory_content and memory_content.strip():
                    record_count = len(data) if isinstance(data, list) else 1
                    print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_file} ({record_count} 条记录)")
                    return memory_content
                else:
                    return ""
        else:
            print(f"⚠ 记忆文件不存在: {memory_path}")
            return ""
    except Exception as e:
        print(f"⚠ 加载记忆失败: {e}")
        return ""

