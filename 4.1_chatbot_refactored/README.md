# 谁是卧底游戏 - 重构版

这是 `2glm.py` 的重构版本，参考了 `Python_101/4.1_chatbot_refactored` 的解耦思路。

## 📁 文件结构

```
4.1_chatbot_refactored/
├── api.py          # API调用模块
├── roles.py        # 角色管理模块
├── game.py         # 游戏逻辑模块
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

### 2. `roles.py` - 角色管理模块
- **职责**：管理游戏角色和系统提示词
- **功能**：
  - `get_available_roles()`: 获取可用角色列表
  - `select_random_role()`: 随机选择角色
  - `get_game_system_prompt(role)`: 根据角色生成游戏系统提示词

### 3. `game.py` - 游戏逻辑模块
- **职责**：处理单轮游戏对话
- **功能**：
  - `play_round()`: 进行一轮游戏对话，调用API并更新对话历史

### 4. `logic.py` - 业务逻辑判断模块
- **职责**：判断游戏状态和用户意图
- **功能**：
  - `is_game_over()`: 判断游戏是否结束（用户猜对或AI回复"再见"）
  - `should_exit_by_user()`: 判断用户是否想要退出游戏

### 5. `main.py` - 主程序入口
- **职责**：协调各个模块，运行主循环
- **功能**：
  - 初始化游戏（选择角色、生成提示词）
  - 运行主循环
  - 处理用户输入和游戏结束逻辑

## 🚀 使用方法

```bash
cd 4.1_chatbot_refactored
python3 main.py
```

## 🔧 配置

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

## ✨ 解耦优势

1. **职责分离**：每个模块只负责一个明确的功能
2. **易于维护**：修改某个功能只需要修改对应模块
3. **易于测试**：可以单独测试每个模块
4. **易于扩展**：添加新角色或新功能只需修改相应模块
5. **代码复用**：API模块可以被其他项目复用

## 📝 代码示例

### 使用角色
```python
from roles import select_random_role, get_game_system_prompt

role = select_random_role()
prompt = get_game_system_prompt(role)
```

### 进行对话
```python
from game import play_round

reply = play_round(conversation_history, user_input)
```

### 判断退出
```python
from logic import is_game_over, should_exit_by_user

if should_exit_by_user(user_input):
    # 用户想要退出
    pass

if is_game_over(ai_reply, correct_role, user_input):
    # 游戏结束
    pass
```

## 🔗 相关项目

- `Python_101/4.1_chatbot_refactored/` - 聊天机器人重构版（参考项目）
- `Python_101/4.2_game_refactored/` - 游戏版本的重构（类似结构）

