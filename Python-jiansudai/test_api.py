#!/usr/bin/env python3
"""
API测试脚本
用于测试后端API是否正常工作
"""

import requests
import json

BASE_URL = 'http://localhost:5001'

def test_health():
    """测试健康检查API"""
    print("🏥 测试健康检查API...")
    try:
        response = requests.get(
            f'{BASE_URL}/api/health',
            headers={'Accept': 'application/json'},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {data}")
            return True
        else:
            print(f"❌ 失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics():
    """测试统计数据API"""
    print("📊 测试统计数据API...")
    try:
        response = requests.get(
            f'{BASE_URL}/api/statistics',
            headers={'Accept': 'application/json'},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {data}")
            return True
        else:
            print(f"❌ 失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyze():
    """测试分析API"""
    print("\n🔍 测试分析API...")
    try:
        data = {
            'session_id': 'test_session_001',
            'vehicle': '节能型小型车',
            'bump': '橡胶减速带',
            'location': '学校门口',
            'speed': 30,
            'survival_rate': 85
        }
        response = requests.post(
            f'{BASE_URL}/api/analyze',
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30  # 分析API可能需要更长时间
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功!")
            print(f"   会话ID: {result.get('session_id')}")
            if result.get('results'):
                print(f"   角色分析数量: {len(result.get('results', {}))}")
                for role, analysis in result.get('results', {}).items():
                    if 'error' not in analysis:
                        print(f"   - {role}: ✅")
                    else:
                        print(f"   - {role}: ❌ {analysis.get('error', '未知错误')}")
            return True
        else:
            print(f"❌ 失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat():
    """测试对话API"""
    print("\n💬 测试对话API...")
    try:
        data = {
            'session_id': 'test_session_001',
            'role': 'ethicist',
            'message': '你好，我想了解一下这个实验的伦理意义',
            'history': []
        }
        response = requests.post(
            f'{BASE_URL}/api/chat',
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30  # 对话API可能需要更长时间
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功!")
            print(f"   角色: {result.get('role')}")
            print(f"   回复: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ 失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("飞跃减速带实验系统 - API测试")
    print("=" * 50)
    print(f"测试服务器: {BASE_URL}")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get(
            f'{BASE_URL}/api/health',
            headers={'Accept': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ 服务器正在运行\n")
        elif response.status_code in [403, 401, 404]:
            print(f"⚠️  服务器在运行但响应异常: {response.status_code}")
            print("   这可能是CORS或路由配置问题\n")
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}\n")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("   请确保后端服务器正在运行:")
        print("   python3 app.py")
        print("   或使用启动脚本:")
        print("   ./start_server.sh")
        return
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("   请检查服务器是否正在运行")
        return
    
    # 运行测试
    results = []
    results.append(("健康检查", test_health()))
    results.append(("统计数据", test_statistics()))
    results.append(("分析API", test_analyze()))
    results.append(("对话API", test_chat()))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print("=" * 50)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("=" * 50)
    if all_passed:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查后端日志")

if __name__ == '__main__':
    main()

