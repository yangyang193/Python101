# 克隆人对话系统 - 重构版

这是 `4.2_clonebot.py` 的重构版本，参考了 `Python_101/4.1_chatbot_refactored` 的解耦思路，并增加了记忆加载功能。

## 📁 文件结构

```
5_backend_101/
├── api.py          # API调用模块
├── memory.py       # 记忆加载模块
├── roles.py        # 角色管理模块
├── chat.py         # 聊天逻辑模块
├── logic.py        # 业务逻辑判断模块
├── main.py         # 主程序入口
└── README.md       # 说明文档（本文件）
```

## 📋 模块说明

### 1. `api.py` - API调用模块
- **职责**：处理与智谱AI API的交互
- **功能**：
  - 从环境变量 `ZHIPU_API_KEY` 或上级目录的 `config.py` 导入API密钥
  - 提供 `call_zhipu_api()` 函数调用API
  - 处理API错误

### 2. `memory.py` - 记忆加载模块
- **职责**：从JSON文件加载角色的外部记忆
- **功能**：
  - `load_memory(role_name)`: 加载指定角色的记忆文件
  - 支持数组格式和字典格式的JSON文件
  - 自动处理文件路径（相对于项目根目录）

### 3. `roles.py` - 角色管理模块
- **职责**：管理角色设定、记忆整合和对话规则
- **功能**：
  - `get_role_personality(role_name)`: 获取角色的基础人格设定
  - `get_role_prompt(role_name)`: 整合记忆和人格，生成完整的角色提示词
  - `get_break_rules()`: 获取结束对话的规则说明

### 4. `chat.py` - 聊天逻辑模块
- **职责**：处理单次对话交互
- **功能**：
  - `chat_once()`: 进行一次对话交互，调用API并更新对话历史

### 5. `logic.py` - 业务逻辑判断模块
- **职责**：判断对话状态和用户意图
- **功能**：
  - `should_exit_by_user()`: 判断用户是否想要结束对话
  - `should_exit_by_ai()`: 判断AI的回复是否表示要结束对话

### 6. `main.py` - 主程序入口
- **职责**：协调各个模块，运行主循环
- **功能**：
  - 初始化角色设定和对话历史
  - 运行主循环
  - 显示ASCII头像和AI回复
  - 处理用户输入和对话结束逻辑

## 🚀 使用方法

```bash
cd 5_backend_101
python3 main.py
```

## 🔧 配置

### API密钥配置

如果需要使用自己的API密钥，可以：

1. **设置环境变量**：
```bash
export ZHIPU_API_KEY="你的智谱AI_API_KEY"
```

2. **或在上级目录创建 `config.py`**：
```python
ZHIPU_API_KEY = "你的智谱AI_API_KEY"
```

如果没有配置，程序会使用默认值（需要手动修改 `api.py` 中的默认值）。

### 记忆文件配置

记忆文件位于 `4.2_memory_clonebot/` 目录下，支持以下格式：

1. **数组格式**：
```json
[
  {"content": "老孩子吃饭没？外卖别老吃了[憨笑]"},
  {"content": "咋还不睡？都3点了，快睡吧。"}
]
```

2. **字典格式**：
```json
{
  "content": "记忆内容..."
}
```

## ✨ 解耦优势

1. **职责分离**：每个模块只负责一个明确的功能
2. **易于维护**：修改某个功能只需要修改对应模块
3. **易于测试**：可以单独测试每个模块
4. **易于扩展**：添加新角色或新功能只需修改相应模块
5. **代码复用**：API模块和记忆模块可以被其他项目复用
6. **记忆管理**：记忆加载独立模块化，便于管理

## 🎯 与原版的区别

| 特性 | 原版 `4.2_clonebot.py` | 重构版 |
|------|----------------------|--------|
| 代码组织 | 单文件，所有逻辑混在一起 | 多模块，职责清晰 |
| API密钥 | 硬编码在代码中 | 可从环境变量或config导入 |
| 记忆加载 | 直接在主程序中 | 独立的memory模块 |
| 角色管理 | 直接在主程序中 | 独立的roles模块 |
| 聊天逻辑 | 混在主循环中 | 独立的chat模块 |
| 判断逻辑 | 简单的if判断 | 独立的logic模块 |
| ASCII头像 | 硬编码在主程序中 | 封装在main.py的函数中 |
| 可维护性 | 低 | 高 |
| 可扩展性 | 低 | 高 |

## 📝 代码示例

### 加载记忆
```python
from memory import load_memory

memory = load_memory("姥姥")
```

### 获取角色提示词
```python
from roles import get_role_prompt

prompt = get_role_prompt("姥姥")
```

### 进行对话
```python
from chat import chat_once

reply = chat_once(conversation_history, user_input, role_prompt)
```

### 判断退出
```python
from logic import should_exit_by_user, should_exit_by_ai

if should_exit_by_user(user_input):
    # 用户想要退出
    pass

if should_exit_by_ai(ai_reply):
    # AI表示要结束
    pass
```

## 🔗 相关项目

- `Python_101/4.1_chatbot_refactored/` - 聊天机器人重构版（参考项目）
- `4.1_chatbot_refactored/` - 基础版游戏重构
- `4.2_chatbot_refactored/` - 游戏版本的重构（带TTS）

## 📌 注意事项

1. 记忆文件路径：默认从 `4.2_memory_clonebot/` 目录加载
2. 对话历史：只在内存中维护，程序关闭后不会保存
3. API密钥建议通过环境变量或config文件配置，不要硬编码在代码中

