#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增的6个API端点
"""

import requests
import json

BASE_URL = 'http://localhost:5001'

def test_recommend():
    """测试智能参数推荐API"""
    print("\n" + "="*50)
    print("测试: POST /api/recommend - 智能参数推荐")
    print("="*50)
    
    response = requests.post(f'{BASE_URL}/api/recommend', json={
        'history': ['高性能跑车+70km/h', '全尺寸SUV+50km/h'],
        'preferences': {'刺激': True, '安全': True}
    })
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"推荐内容: {data.get('recommendation', '')[:200]}...")
    else:
        print(f"错误: {response.text}")

def test_risk_assess():
    """测试风险评估API"""
    print("\n" + "="*50)
    print("测试: POST /api/risk/assess - 实时风险评估")
    print("="*50)
    
    response = requests.post(f'{BASE_URL}/api/risk/assess', json={
        'vehicle': '高性能跑车',
        'speed': 70,
        'bump': '金属减速带',
        'location': '学校门口'
    })
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"风险等级: {data.get('risk_level')}")
        print(f"评估内容: {data.get('assessment', '')[:200]}...")
    else:
        print(f"错误: {response.text}")

def test_learning_path():
    """测试学习路径生成API"""
    print("\n" + "="*50)
    print("测试: POST /api/learning/path - 个性化学习路径")
    print("="*50)
    
    response = requests.post(f'{BASE_URL}/api/learning/path', json={
        'choices': [
            {'vehicle': '高性能跑车', 'speed': 70},
            {'vehicle': '全尺寸SUV', 'speed': 50}
        ],
        'session_id': 'test_session_001'
    })
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"学习路径角色数: {len(data.get('learning_path', {}))}")
    else:
        print(f"错误: {response.text}")

def test_report_title():
    """测试报告标题生成API"""
    print("\n" + "="*50)
    print("测试: POST /api/report/title - 智能报告标题生成")
    print("="*50)
    
    response = requests.post(f'{BASE_URL}/api/report/title', json={
        'analysis': '用户选择了高性能跑车，速度70km/h，体现了冒险倾向',
        'personality_traits': {'riskTaking': 80, 'safetyConsciousness': 40},
        'justice_index': {'overall': 65}
    })
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"生成的标题: {data.get('titles', [])}")
    else:
        print(f"错误: {response.text}")

def test_debate():
    """测试多角色辩论API"""
    print("\n" + "="*50)
    print("测试: POST /api/debate - 多角色辩论生成")
    print("="*50)
    
    response = requests.post(f'{BASE_URL}/api/debate', json={
        'choice': {
            'vehicle': '高性能跑车',
            'bump': '金属减速带',
            'location': '学校门口',
            'speed': 70,
            'survival_rate': 45
        },
        'session_id': 'test_session_002'
    })
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"参与辩论的角色: {list(data.get('debate', {}).keys())}")
    else:
        print(f"错误: {response.text}")

def test_questions():
    """测试问题生成API"""
    print("\n" + "="*50)
    print("测试: POST /api/questions/generate - 智能问题生成")
    print("="*50)
    
    response = requests.post(f'{BASE_URL}/api/questions/generate', json={
        'choice': {
            'vehicle': '高性能跑车',
            'bump': '金属减速带',
            'location': '学校门口',
            'speed': 70,
            'survival_rate': 45
        },
        'type': 'reflection'  # reflection, ethics, safety, physics
    })
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"问题类型: {data.get('question_type')}")
        print(f"生成的问题数: {len(data.get('questions', []))}")
        print(f"问题示例: {data.get('questions', [])[:2]}")
    else:
        print(f"错误: {response.text}")

if __name__ == '__main__':
    print("="*50)
    print("新API端点测试脚本")
    print("="*50)
    print("请确保服务器已启动: python3 app.py")
    print("或运行: ./start_server.sh")
    print("="*50)
    
    try:
        # 检查服务器是否运行
        health_check = requests.get(f'{BASE_URL}/api/health', timeout=2)
        if health_check.status_code != 200:
            print("❌ 服务器未正常运行")
            exit(1)
        print("✅ 服务器运行正常\n")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动服务器")
        exit(1)
    
    # 运行所有测试
    test_recommend()
    test_risk_assess()
    test_learning_path()
    test_report_title()
    test_debate()
    test_questions()
    
    print("\n" + "="*50)
    print("所有测试完成！")
    print("="*50)

