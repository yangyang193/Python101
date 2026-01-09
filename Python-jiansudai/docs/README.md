# 提示词工程文档

本目录包含项目中所有角色的详细文档，以及提示词工程相关的使用指南。

## 目录结构

```
docs/
├── README.md                    # 本文档
├── 角色文档-伦理学家.md         # 伦理学家角色文档
├── 角色文档-安全员.md           # 安全员角色文档
├── 角色文档-物理学家.md         # 物理学家角色文档
├── 角色文档-交通工程师.md      # 交通工程师角色文档
├── 角色文档-后端工程师.md      # 后端工程师角色文档
├── 角色文档-可视化设计师.md    # 可视化设计师角色文档
├── 提示词版本管理指南.md        # 版本管理使用指南
├── 提示词测试指南.md            # 测试框架使用指南
└── A_B测试使用指南.md          # A/B测试使用指南
```

## 角色列表

项目包含以下6个专业角色：

1. **伦理学家** (`ethicist`) - 专注于技术伦理和社会影响评估
2. **安全员** (`safety`) - 识别和防范安全隐患
3. **物理学家** (`physicist`) - 专精于车辆动力学和碰撞物理学
4. **交通工程师** (`traffic`) - 从交通工程角度分析问题
5. **后端工程师** (`engineer`) - 提供技术实现方案
6. **可视化设计师** (`designer`) - 设计数据可视化方案

## 提示词工程工具

### 1. 版本管理系统

**文件**: `prompt_version_manager.py`

**功能**:
- 管理提示词的版本号
- 记录版本变更历史
- 支持版本回滚
- 版本对比功能

**使用示例**:
```python
from prompt_version_manager import PromptVersionManager

manager = PromptVersionManager()

# 注册新版本
manager.register_version(
    role_name="伦理学家",
    version="v1.1.0",
    prompt_content="新的提示词内容...",
    change_log="优化了角色设定"
)

# 获取版本
version = manager.get_version("伦理学家", "v1.1.0")

# 设置活动版本
manager.set_active_version("伦理学家", "v1.1.0")
```

### 2. 测试框架

**文件**: `prompt_tester.py`

**功能**:
- 定义测试用例
- 运行测试并评估结果
- 生成测试报告
- 支持批量测试

**使用示例**:
```python
from prompt_tester import PromptTester, PromptTestCase

tester = PromptTester()

# 创建测试用例
test_case = PromptTestCase(
    test_id='test_001',
    role_name='ethicist',
    input_message='这个项目有什么伦理风险？',
    expected_keywords=['伦理', '风险'],
    expected_length_range=(100, 2000)
)

# 运行测试
result = tester.run_test_case(test_case)

# 生成报告
report = tester.generate_report(result)
```

### 3. A/B测试系统

**文件**: `prompt_ab_test.py`

**功能**:
- 创建A/B测试实验
- 随机分配用户到不同版本
- 收集测试数据
- 分析测试结果
- 自动选择最优版本

**使用示例**:
```python
from prompt_ab_test import ABTestManager

manager = ABTestManager()

# 创建实验
manager.create_experiment(
    experiment_id="exp_001",
    role_name="伦理学家",
    version_a="v1.0.0",
    version_b="v1.1.0",
    traffic_split=0.5
)

# 分配版本
version = manager.assign_version("exp_001", "user_123")

# 记录结果
manager.record_test_result(
    experiment_id="exp_001",
    version=version,
    input_message="测试消息",
    output_message="AI回复",
    response_time=1.5,
    user_rating=5
)

# 分析结果
analysis = manager.analyze_results("exp_001", "user_rating")
```

## 版本管理规范

### 版本号格式

使用语义化版本号：`主版本号.次版本号.修订号`

- **主版本号**: 重大变更，不兼容的修改
- **次版本号**: 新增功能，向后兼容
- **修订号**: 问题修复，向后兼容

示例：
- `v1.0.0` - 初始版本
- `v1.1.0` - 新增功能
- `v1.1.1` - 修复问题
- `v2.0.0` - 重大变更

### 变更日志格式

```markdown
## v1.1.0 (2024-01-XX)

### 新增
- 新增了角色关系定义
- 新增了思考方式说明

### 优化
- 优化了沟通风格描述
- 改进了期望输出格式

### 修复
- 修复了角色定位不清晰的问题
```

## 测试规范

### 测试用例设计原则

1. **覆盖性**: 覆盖角色的核心功能
2. **真实性**: 使用真实的用户输入场景
3. **可评估性**: 有明确的评估标准
4. **可重复性**: 测试结果可重复

### 评估指标

- **关键词匹配**: 检查输出是否包含期望的关键词
- **长度范围**: 检查输出长度是否在合理范围内
- **格式检查**: 检查输出格式是否符合要求
- **用户评分**: 收集用户对输出的评分

## A/B测试规范

### 实验设计

1. **明确目标**: 确定要测试的指标
2. **版本选择**: 选择要对比的版本
3. **流量分配**: 设置合理的流量分配比例
4. **样本量**: 确保有足够的样本量

### 评估指标

- **用户评分**: 用户对输出的满意度
- **响应时间**: API响应时间
- **正面反馈率**: 用户给出正面反馈的比例

### 结果分析

- 统计显著性检验
- 置信区间计算
- 效果大小评估

## 最佳实践

### 1. 提示词设计

- **明确角色定位**: 清晰定义角色的身份和能力
- **结构化组织**: 使用结构化的模板组织提示词
- **具体化要求**: 提供具体的输出要求和格式
- **约束条件**: 明确约束条件和边界

### 2. 版本管理

- **及时记录**: 每次修改都记录版本
- **详细日志**: 详细记录变更内容
- **定期回顾**: 定期回顾版本历史
- **文档同步**: 保持文档与代码同步

### 3. 测试

- **持续测试**: 定期运行测试用例
- **覆盖全面**: 确保测试覆盖所有核心功能
- **及时修复**: 发现问题及时修复
- **记录结果**: 记录测试结果用于分析

### 4. A/B测试

- **明确目标**: 明确测试目标
- **合理设计**: 设计合理的实验
- **充分测试**: 确保有足够的样本量
- **科学分析**: 使用科学方法分析结果

## 相关资源

- [提示词工程最佳实践](https://www.promptingguide.ai/)
- [A/B测试指南](https://www.optimizely.com/optimization-glossary/ab-testing/)
- [语义化版本](https://semver.org/)

## 贡献指南

1. 修改提示词时，请更新对应的角色文档
2. 新增功能时，请更新版本号并记录变更日志
3. 添加测试用例时，请确保测试覆盖核心功能
4. 进行A/B测试时，请详细记录实验过程和结果

## 联系方式

如有问题或建议，请联系项目维护者。

