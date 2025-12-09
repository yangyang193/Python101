import random

names = [
    "裴浩均",
    "洪梽炫",
    "陈彦臻",
    "吴自欣",
    "陈芸",
    "潘莹",
    "吴杰",
    "梁炫澔",
    "林以乐",
    "李嘉悦",
    "洪沁涵",
    "高琰喆",
    "王孜璟",
    "楼欣晨",
    "徐哿",
    "宋曙延",
    "周欣怡",
    "侯胤竹",
    "黄亦凡",
    "杨洋",
    "张青卉"
]

# 输入要抽取的组数
num_groups = 7
students_per_group = 3

# 计算总共需要抽取的人数
total_needed = num_groups * students_per_group
total_students = len(names)

# 如果需要的总人数超过学生总数，则只抽取所有学生
if total_needed > total_students:
    print(f"注意：需要抽取 {total_needed} 人，但只有 {total_students} 名学生。")
    print(f"将抽取所有 {total_students} 名学生，分为 {total_students // students_per_group} 组。")
    selected_students = names.copy()
else:
    # 随机抽取不重复的学生
    selected_students = random.sample(names, total_needed)

# 打乱顺序，确保随机分配
random.shuffle(selected_students)

# 按组分配
groups = []
for i in range(0, len(selected_students), students_per_group):
    group = selected_students[i:i + students_per_group]
    groups.append(group)

# 显示结果
print(f"\n共抽取 {len(groups)} 组，每组 {students_per_group} 人：")
print("=" * 50)
for i, group in enumerate(groups, 1):
    print(f"\n第 {i} 组：")
    for name in group:
        print(f"  - {name}")

# 显示未抽取的学生（如果有）
if total_needed < total_students:
    remaining = [name for name in names if name not in selected_students]
    print(f"\n未抽取的学生（共 {len(remaining)} 人）：")
    for name in remaining:
        print(f"  - {name}")