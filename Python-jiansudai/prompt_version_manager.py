"""
提示词版本管理系统

功能：
1. 管理提示词的版本号
2. 记录版本变更历史
3. 支持版本回滚
4. 版本对比功能
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3


class PromptVersionManager:
    """提示词版本管理器"""
    
    def __init__(self, db_path: str = "prompt_versions.db"):
        """
        初始化版本管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # 版本记录表
            c.execute('''
                CREATE TABLE IF NOT EXISTS prompt_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    prompt_content TEXT NOT NULL,
                    change_log TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    created_by TEXT,
                    UNIQUE(role_name, version)
                )
            ''')
            
            # 版本变更历史表
            c.execute('''
                CREATE TABLE IF NOT EXISTS version_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_name TEXT NOT NULL,
                    from_version TEXT,
                    to_version TEXT,
                    change_type TEXT,
                    change_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def register_version(
        self,
        role_name: str,
        version: str,
        prompt_content: str,
        change_log: str = "",
        created_by: str = "system"
    ) -> bool:
        """
        注册新版本
        
        Args:
            role_name: 角色名称
            version: 版本号（格式：v1.0.0）
            prompt_content: 提示词内容
            change_log: 变更日志
            created_by: 创建者
            
        Returns:
            是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                
                # 如果已存在相同版本，先取消激活
                c.execute('''
                    UPDATE prompt_versions
                    SET is_active = 0
                    WHERE role_name = ? AND version = ?
                ''', (role_name, version))
                
                # 插入新版本
                c.execute('''
                    INSERT INTO prompt_versions 
                    (role_name, version, prompt_content, change_log, created_by)
                    VALUES (?, ?, ?, ?, ?)
                ''', (role_name, version, prompt_content, change_log, created_by))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"注册版本失败: {e}")
            return False
    
    def get_version(
        self,
        role_name: str,
        version: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取指定版本
        
        Args:
            role_name: 角色名称
            version: 版本号，如果为None则返回最新版本
            
        Returns:
            版本信息字典
        """
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            if version:
                c.execute('''
                    SELECT version, prompt_content, change_log, created_at, created_by
                    FROM prompt_versions
                    WHERE role_name = ? AND version = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (role_name, version))
            else:
                c.execute('''
                    SELECT version, prompt_content, change_log, created_at, created_by
                    FROM prompt_versions
                    WHERE role_name = ? AND is_active = 1
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (role_name,))
            
            result = c.fetchone()
            if result:
                return {
                    'version': result[0],
                    'prompt_content': result[1],
                    'change_log': result[2],
                    'created_at': result[3],
                    'created_by': result[4]
                }
            return None
    
    def list_versions(self, role_name: str) -> List[Dict]:
        """
        列出所有版本
        
        Args:
            role_name: 角色名称
            
        Returns:
            版本列表
        """
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            c.execute('''
                SELECT version, change_log, created_at, created_by, is_active
                FROM prompt_versions
                WHERE role_name = ?
                ORDER BY created_at DESC
            ''', (role_name,))
            
            results = c.fetchall()
            return [
                {
                    'version': r[0],
                    'change_log': r[1],
                    'created_at': r[2],
                    'created_by': r[3],
                    'is_active': bool(r[4])
                }
                for r in results
            ]
    
    def set_active_version(self, role_name: str, version: str) -> bool:
        """
        设置活动版本
        
        Args:
            role_name: 角色名称
            version: 版本号
            
        Returns:
            是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                
                # 获取旧的活动版本
                c.execute('''
                    SELECT version FROM prompt_versions
                    WHERE role_name = ? AND is_active = 1
                ''', (role_name,))
                old_version = c.fetchone()
                old_version = old_version[0] if old_version else None
                
                # 取消所有版本的激活状态
                c.execute('''
                    UPDATE prompt_versions
                    SET is_active = 0
                    WHERE role_name = ?
                ''', (role_name,))
                
                # 激活指定版本
                c.execute('''
                    UPDATE prompt_versions
                    SET is_active = 1
                    WHERE role_name = ? AND version = ?
                ''', (role_name, version))
                
                # 记录版本变更历史
                if old_version and old_version != version:
                    c.execute('''
                        INSERT INTO version_history 
                        (role_name, from_version, to_version, change_type, change_description)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (role_name, old_version, version, 'rollback', f'切换到版本 {version}'))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"设置活动版本失败: {e}")
            return False
    
    def compare_versions(
        self,
        role_name: str,
        version1: str,
        version2: str
    ) -> Dict:
        """
        对比两个版本
        
        Args:
            role_name: 角色名称
            version1: 版本1
            version2: 版本2
            
        Returns:
            对比结果
        """
        v1 = self.get_version(role_name, version1)
        v2 = self.get_version(role_name, version2)
        
        if not v1 or not v2:
            return {'error': '版本不存在'}
        
        return {
            'version1': {
                'version': v1['version'],
                'created_at': v1['created_at'],
                'length': len(v1['prompt_content'])
            },
            'version2': {
                'version': v2['version'],
                'created_at': v2['created_at'],
                'length': len(v2['prompt_content'])
            },
            'diff_length': len(v2['prompt_content']) - len(v1['prompt_content'])
        }
    
    def get_version_history(self, role_name: str) -> List[Dict]:
        """
        获取版本变更历史
        
        Args:
            role_name: 角色名称
            
        Returns:
            历史记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            c.execute('''
                SELECT from_version, to_version, change_type, change_description, created_at
                FROM version_history
                WHERE role_name = ?
                ORDER BY created_at DESC
            ''', (role_name,))
            
            results = c.fetchall()
            return [
                {
                    'from_version': r[0],
                    'to_version': r[1],
                    'change_type': r[2],
                    'change_description': r[3],
                    'created_at': r[4]
                }
                for r in results
            ]


# 全局版本管理器实例
version_manager = PromptVersionManager()


def get_prompt_version(role_name: str, version: Optional[str] = None) -> Optional[str]:
    """
    获取提示词版本（便捷函数）
    
    Args:
        role_name: 角色名称
        version: 版本号，None表示最新版本
        
    Returns:
        提示词内容
    """
    version_info = version_manager.get_version(role_name, version)
    if version_info:
        return version_info['prompt_content']
    return None


if __name__ == '__main__':
    # 测试代码
    manager = PromptVersionManager()
    
    # 注册测试版本
    test_prompt = "【角色设定】\n你是一个测试角色。"
    manager.register_version(
        role_name="测试角色",
        version="v1.0.0",
        prompt_content=test_prompt,
        change_log="初始版本",
        created_by="test_user"
    )
    
    # 获取版本
    version = manager.get_version("测试角色", "v1.0.0")
    print(f"获取版本: {version['version'] if version else 'None'}")
    
    # 列出所有版本
    versions = manager.list_versions("测试角色")
    print(f"版本列表: {len(versions)} 个版本")

