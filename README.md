## 今日学习小结：Python 基础知识（基于 101.py 与 gln.py）

### 1) 101.py 涉及的基础点
- 变量赋值与动态类型：`x = 1`、`y = 2`，无需显式声明类型（自动为 int）。
- 算术运算：使用 `+` 进行加法，表达式 `x + y`。 
- 内置输出函数：`print(x + y)` 将结果输出到控制台。

示例运行输出：`3`。

---

### 2) gln.py 涉及的基础点
- 模块导入：`import requests`、`import json`（第三方库与标准库导入方式）。
- 函数定义与默认参数：
  ```python
  def call_zhipu_api(messages, model="glm-4-flash"):
      ...
  ```
- 字典与列表的使用：
  - 构造请求头与请求体（字典）：`headers = {...}`、`data = {...}`
  - 构造消息列表（列表嵌套字典）：`messages = [{"role": "user", "content": "..."}]`
- 第三方库请求：使用 `requests.post(url, headers=headers, json=data)` 进行 HTTP POST；通过 `response.status_code` 判断请求结果，`response.json()` 解析 JSON。
- 条件分支与异常：
  ```python
  if response.status_code == 200:
      return response.json()
  else:
      raise Exception(f"API调用失败: {response.status_code}, {response.text}")
  ```
  - 使用 `if/else` 分支处理成功与失败
  - 通过 `raise Exception(...)` 抛出异常；使用 f-string 构造错误信息
- 数据访问与打印：
  - 访问嵌套结构：`result['choices'][0]['message']['content']`
  - 使用 `print(...)` 输出结果
- 注释：`# 使用示例`，展示如何为代码添加说明

小提示（实践与规范）：
- 生产代码中不应在源码里硬编码密钥/令牌，建议改为环境变量或配置文件管理。
- 网络请求应考虑异常处理与超时设置（如 `requests.post(..., timeout=10)`）。

---

### 3) 本日要点回顾
- 变量、整数类型、表达式与 `print()` 输出
- 模块导入、函数定义与默认参数
- 列表与字典的组合使用（结构化数据）
- HTTP 请求与 JSON 解析（`requests` 与 `response.json()`）
- 条件分支、异常抛出与 f-string 格式化

结合两份代码，你已经覆盖了从基础运算到简单 API 调用的一条完整链路：定义数据 → 组织请求 → 发送请求 → 处理响应 → 输出结果。


