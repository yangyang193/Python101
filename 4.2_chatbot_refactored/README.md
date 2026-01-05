# 谁是卧底游戏（语音版）- 重构版

这是 `3.2glm.py` 的重构版本，参考了 `4.1_chatbot_refactored` 的解耦思路，并增加了TTS语音播放功能。

## 📁 文件结构

```
4.2_chatbot_refactored/
├── api.py          # API调用模块
├── roles.py        # 角色管理模块
├── game.py         # 游戏逻辑模块（包含TTS功能）
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
  - `get_available_roles()`: 获取可用角色列表（保安、保镖）
  - `select_random_role()`: 随机选择角色
  - `get_game_system_prompt(role)`: 根据角色生成游戏系统提示词
  - 包含详细的角色特征和说话方式说明

### 3. `game.py` - 游戏逻辑模块
- **职责**：处理单轮游戏对话和TTS语音播放
- **功能**：
  - `play_round()`: 进行一轮游戏对话，调用API并更新对话历史
  - 自动调用TTS功能播放AI回复（如果可用）
  - 处理TTS错误，不影响游戏继续

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
cd 4.2_chatbot_refactored
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

### TTS功能配置

TTS功能依赖于上级目录的 `xunfei_tts.py` 模块。如果该模块不存在，TTS功能会自动禁用，但游戏仍可正常运行。

## ✨ 解耦优势

1. **职责分离**：每个模块只负责一个明确的功能
2. **易于维护**：修改某个功能只需要修改对应模块
3. **易于测试**：可以单独测试每个模块
4. **易于扩展**：添加新角色或新功能只需修改相应模块
5. **代码复用**：API模块可以被其他项目复用
6. **功能模块化**：TTS功能独立，可以轻松启用/禁用

## 🎯 与原版的区别

| 特性 | 原版 `3.2glm.py` | 重构版 |
|------|------------------|--------|
| 代码组织 | 单文件，所有逻辑混在一起 | 多模块，职责清晰 |
| API密钥 | 硬编码在代码中 | 可从环境变量或config导入 |
| 角色管理 | 直接在主程序中 | 独立的roles模块 |
| 游戏逻辑 | 混在主循环中 | 独立的game模块 |
| TTS功能 | 直接在主循环中调用 | 封装在game模块中 |
| 判断逻辑 | 简单的if判断 | 独立的logic模块 |
| 可维护性 | 低 | 高 |
| 可扩展性 | 低 | 高 |

## 📝 代码示例

### 使用角色
```python
from roles import select_random_role, get_game_system_prompt

role = select_random_role()
prompt = get_game_system_prompt(role)
```

### 进行对话（带TTS）
```python
from game import play_round

reply = play_round(conversation_history, user_input, enable_tts=True)
```

### 进行对话（不带TTS）
```python
from game import play_round

reply = play_round(conversation_history, user_input, enable_tts=False)
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

- `4.1_chatbot_refactored/` - 基础版游戏重构（参考项目）
- `Python_101/4.1_chatbot_refactored/` - 聊天机器人重构版
- `Python_101/4.2_game_refactored/` - 游戏版本的重构（类似结构）

## 📌 注意事项

1. TTS功能需要 `xunfei_tts.py` 模块支持
2. 如果TTS模块不可用，游戏仍可正常运行，只是没有语音播放
3. API密钥建议通过环境变量或config文件配置，不要硬编码在代码中

