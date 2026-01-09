"""
提示词版本注册脚本

用于将当前所有角色的提示词注册到版本管理系统
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

from prompt_version_manager import PromptVersionManager
from ren import ll, aqy, jt, wl, d3, gcs

# 角色映射
ROLES = {
    'ethicist': {'module': ll, 'name': '伦理学家'},
    'safety': {'module': aqy, 'name': '安全员'},
    'traffic': {'module': jt, 'name': '交通工程师'},
    'physicist': {'module': wl, 'name': '物理学家'},
    'designer': {'module': d3, 'name': '可视化设计师'},
    'engineer': {'module': gcs, 'name': '资深后端工程师'}
}


def register_all_versions(version: str = "v1.0.0", change_log: str = "初始版本"):
    """
    注册所有角色的提示词版本
    
    Args:
        version: 版本号
        change_log: 变更日志
    """
    manager = PromptVersionManager()
    
    print(f"开始注册提示词版本 {version}...")
    print("=" * 50)
    
    success_count = 0
    fail_count = 0
    
    for role_key, role_info in ROLES.items():
        role_name = role_info['name']
        role_module = role_info['module']
        
        try:
            # 获取角色提示词
            prompt_content = role_module.roles(role_name)
            
            # 注册版本
            success = manager.register_version(
                role_name=role_name,
                version=version,
                prompt_content=prompt_content,
                change_log=change_log,
                created_by="system"
            )
            
            if success:
                print(f"✓ {role_name}: 版本 {version} 注册成功")
                success_count += 1
                
                # 设置为活动版本
                manager.set_active_version(role_name, version)
            else:
                print(f"✗ {role_name}: 版本 {version} 注册失败")
                fail_count += 1
                
        except Exception as e:
            print(f"✗ {role_name}: 注册时发生错误 - {e}")
            fail_count += 1
    
    print("=" * 50)
    print(f"注册完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    
    return success_count, fail_count


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='注册提示词版本')
    parser.add_argument('--version', type=str, default='v1.0.0', help='版本号')
    parser.add_argument('--change-log', type=str, default='初始版本', help='变更日志')
    
    args = parser.parse_args()
    
    register_all_versions(args.version, args.change_log)

