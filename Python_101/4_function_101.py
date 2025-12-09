# ========== 第4周：函数基础 ==========
# 
# 【什么是函数？】
# 函数就是把一段代码打包起来，给它起个名字，可以重复使用
# 就像做菜的步骤，写成一个"菜谱"，以后直接按菜谱做就行

# ========== 示例1：一个简单的函数 ==========

def z(x, y):
    x = x + 1
    y = x + 1
    return x

print(z(1, 2))  # 输出：2

# 【函数的基本结构】
# def 函数名(参数1, 参数2):
#     函数体（要执行的代码）
#     return 返回值

# 【这个函数的问题】
# 1. 函数名 z 没有意义，应该用有意义的名字
# 2. 参数 y 被计算了但没有使用
# 3. 只返回了 x，没有返回 y

# ========== 示例2：改进后的函数 ==========

def add_one(number):
    """给数字加1"""
    result = number + 1
    return result

print(add_one(5))  # 输出：6

# 【改进点】
# - 函数名 add_one 清楚表达了功能
# - 参数名 number 比 x 更有意义
# - 有文档说明（三引号里的内容）

# ========== 回顾：3.3 中我们已经用过的函数 ==========
# 
# 在 3.3_memory_clonebot_streamlit.py 中，我们已经用了这些函数：

# 1. call_zhipu_api(messages, model="glm-4-flash")
#    - 参数：messages（必须），model（可选，有默认值）
#    - 返回值：API返回的JSON数据

# 2. roles(role_name)
#    - 参数：role_name（角色名）
#    - 返回值：角色的完整设定字符串

# 3. get_portrait()
#    - 参数：无
#    - 返回值：ASCII艺术字符串

# ========== 函数的参数类型 ==========

def greet(name, greeting="你好"):
    """生成问候语"""
    return f"{greeting}，{name}！"

print(greet("小明"))              # 使用默认值：你好，小明！
print(greet("小红", "早上好"))     # 自定义：早上好，小红！

# 【参数说明】
# - name：必须参数，调用时必须传入
# - greeting：可选参数，有默认值"你好"，可以不传

# ========== 多个返回值 ==========

def calculate(a, b):
    """计算两个数的和与差"""
    add = a + b
    sub = a - b
    return add, sub  # 返回多个值（实际上是返回一个元组）

sum_result, diff = calculate(10, 3)
print(f"和={sum_result}, 差={diff}")  # 输出：和=13, 差=7

# ========== 为什么需要函数？ ==========
# 
# 1. 避免重复：写一次，用多次
# 2. 代码清晰：每个函数只做一件事
# 3. 方便修改：只需要改一个地方
# 
# 比如在 3.3 中，每次需要调用API时，只需要写：
# result = call_zhipu_api(messages)
# 而不需要每次都写完整的API调用代码
