"""
社交功能模块
实现评论、分享和协作学习功能
"""
import sqlite3
import json
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime


class SocialFeaturesManager:
    """社交功能管理器"""
    
    def __init__(self, db_path: str = 'simulation_data.db'):
        self.db_path = db_path
    
    # ========== 评论功能 ==========
    
    def add_comment(self, session_id: str, user_id: str, content: str, 
                   parent_id: Optional[int] = None) -> Dict[str, Any]:
        """
        添加评论
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            content: 评论内容
            parent_id: 父评论ID（用于回复）
        
        Returns:
            评论信息
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO comments (session_id, parent_id, user_id, content)
            VALUES (?, ?, ?, ?)
        ''', (session_id, parent_id, user_id, content))
        
        comment_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': comment_id,
            'session_id': session_id,
            'user_id': user_id,
            'content': content,
            'parent_id': parent_id,
            'likes': 0,
            'created_at': datetime.now().isoformat()
        }
    
    def get_comments(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取评论列表
        
        Args:
            session_id: 会话ID
            limit: 返回数量限制
        
        Returns:
            评论列表
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, parent_id, user_id, content, likes, created_at
            FROM comments
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = c.fetchall()
        conn.close()
        
        comments = []
        for row in rows:
            comments.append({
                'id': row[0],
                'parent_id': row[1],
                'user_id': row[2],
                'content': row[3],
                'likes': row[4],
                'created_at': row[5]
            })
        
        return comments
    
    def like_comment(self, comment_id: int) -> bool:
        """
        点赞评论
        
        Args:
            comment_id: 评论ID
        
        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE comments
            SET likes = likes + 1
            WHERE id = ?
        ''', (comment_id,))
        
        conn.commit()
        conn.close()
        return True
    
    # ========== 分享功能 ==========
    
    def create_share(self, session_id: str, share_type: str = 'report', 
                    share_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        创建分享
        
        Args:
            session_id: 会话ID
            share_type: 分享类型（report, analysis, debate等）
            share_data: 分享数据
        
        Returns:
            分享信息（包含分享码）
        """
        # 生成唯一分享码
        share_code = self._generate_share_code(session_id, share_type)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO shares (session_id, share_code, share_type, share_data)
            VALUES (?, ?, ?, ?)
        ''', (
            session_id,
            share_code,
            share_type,
            json.dumps(share_data or {}, ensure_ascii=False)
        ))
        
        share_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': share_id,
            'share_code': share_code,
            'share_type': share_type,
            'share_url': f'/share/{share_code}',
            'created_at': datetime.now().isoformat()
        }
    
    def get_share(self, share_code: str) -> Optional[Dict[str, Any]]:
        """
        获取分享内容
        
        Args:
            share_code: 分享码
        
        Returns:
            分享内容
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, session_id, share_type, share_data, view_count, created_at
            FROM shares
            WHERE share_code = ?
        ''', (share_code,))
        
        row = c.fetchone()
        
        if row:
            # 增加查看次数
            c.execute('''
                UPDATE shares
                SET view_count = view_count + 1
                WHERE id = ?
            ''', (row[0],))
            conn.commit()
        
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'session_id': row[1],
            'share_type': row[2],
            'share_data': json.loads(row[3]) if row[3] else {},
            'view_count': row[4] + 1,  # 已更新
            'created_at': row[5]
        }
    
    def _generate_share_code(self, session_id: str, share_type: str) -> str:
        """生成唯一分享码"""
        # 使用会话ID、类型和时间戳生成哈希
        data = f"{session_id}_{share_type}_{datetime.now().timestamp()}"
        hash_obj = hashlib.md5(data.encode())
        return hash_obj.hexdigest()[:12]  # 12位分享码
    
    # ========== 协作学习功能 ==========
    
    def create_collaboration(self, session_id: str, collaborator_id: str,
                           collaboration_type: str, content: str) -> Dict[str, Any]:
        """
        创建协作学习记录
        
        Args:
            session_id: 会话ID
            collaborator_id: 协作者ID
            collaboration_type: 协作类型（discussion, comparison, learning_path等）
            content: 协作内容
        
        Returns:
            协作记录
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO collaborations (session_id, collaborator_id, collaboration_type, content)
            VALUES (?, ?, ?, ?)
        ''', (session_id, collaborator_id, collaboration_type, content))
        
        collab_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': collab_id,
            'session_id': session_id,
            'collaborator_id': collaborator_id,
            'collaboration_type': collaboration_type,
            'content': content,
            'created_at': datetime.now().isoformat()
        }
    
    def get_collaborations(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取协作学习记录
        
        Args:
            session_id: 会话ID
        
        Returns:
            协作记录列表
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, collaborator_id, collaboration_type, content, created_at
            FROM collaborations
            WHERE session_id = ?
            ORDER BY created_at DESC
        ''', (session_id,))
        
        rows = c.fetchall()
        conn.close()
        
        collaborations = []
        for row in rows:
            collaborations.append({
                'id': row[0],
                'collaborator_id': row[1],
                'collaboration_type': row[2],
                'content': row[3],
                'created_at': row[4]
            })
        
        return collaborations
    
    def compare_sessions(self, session_id1: str, session_id2: str) -> Dict[str, Any]:
        """
        比较两个会话的结果（协作学习）
        
        Args:
            session_id1: 会话ID 1
            session_id2: 会话ID 2
        
        Returns:
            比较结果
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 获取两个会话的选择
        c.execute('''
            SELECT vehicle, bump, location, speed, survival_rate
            FROM user_choices
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (session_id1,))
        choice1 = c.fetchone()
        
        c.execute('''
            SELECT vehicle, bump, location, speed, survival_rate
            FROM user_choices
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (session_id2,))
        choice2 = c.fetchone()
        
        conn.close()
        
        if not choice1 or not choice2:
            return {'error': '无法找到会话数据'}
        
        comparison = {
            'session1': {
                'vehicle': choice1[0],
                'bump': choice1[1],
                'location': choice1[2],
                'speed': choice1[3],
                'survival_rate': choice1[4]
            },
            'session2': {
                'vehicle': choice2[0],
                'bump': choice2[1],
                'location': choice2[2],
                'speed': choice2[3],
                'survival_rate': choice2[4]
            },
            'differences': {
                'speed_diff': abs(choice1[3] - choice2[3]),
                'survival_diff': abs(choice1[4] - choice2[4]),
                'same_vehicle': choice1[0] == choice2[0],
                'same_location': choice1[2] == choice2[2]
            }
        }
        
        return comparison


# 单例实例
_social_manager_instance = None

def get_social_manager() -> SocialFeaturesManager:
    """获取社交功能管理器单例"""
    global _social_manager_instance
    if _social_manager_instance is None:
        _social_manager_instance = SocialFeaturesManager()
    return _social_manager_instance

