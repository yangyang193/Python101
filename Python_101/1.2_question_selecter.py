import random

questions = [
    "Q1: 随机伴侣 SOUL MATES",
    "Q2: 激光笔 LASER POINTER",
    "Q3: 元素周期墙 Periodic Wall of the elements",
    "Q4: 匀速上升 RISING STEADILY",
    "Q5: 小世界 LITTLE PLANET",
    "Q6: 外星天文学家 ALIEN ASTRONOMERS",
    "Q7: 星级塞斯纳1 INTERPLANETARY CESSNA",
    "Q8: 一个人身体的总营养价值",
    "Q9: 氦气球降落伞 FALLING WITH HELIUM",
    "Q10: 亲吻的吸力",
    "Q11: 高掷比赛 HIGH THROW",
    "Q12: 飞越减速带 SPEED BUMP",
    "Q13: 橡树岛的宝藏",
    "Q14: 风筝"
]

# 输入要分配的组数
num_groups = 7
total_questions = len(questions)

# 计算每组分配的问题数
questions_per_group = total_questions // num_groups
remaining_questions = total_questions % num_groups

# 打乱问题顺序，确保随机分配
shuffled_questions = questions.copy()
random.shuffle(shuffled_questions)

# 按组分配问题
groups = []
question_index = 0

for i in range(num_groups):
    # 前几组可能多分配一个问题（如果有余数）
    group_size = questions_per_group + (1 if i < remaining_questions else 0)
    group_questions = shuffled_questions[question_index:question_index + group_size]
    groups.append(group_questions)
    question_index += group_size

# 显示结果
print(f"\n共 {num_groups} 组，分配 {total_questions} 个问题：")
print("=" * 60)
for i, group in enumerate(groups, 1):
    print(f"\n第 {i} 组（{len(group)} 个问题）：")
    for question in group:
        print(f"  - {question}")

