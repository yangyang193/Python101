"""
个性化模块
实现用户画像、学习偏好分析和个性化内容调整
"""
import sqlite3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter


class UserProfileManager:
    """用户画像管理器"""
    
    def __init__(self, db_path: str = 'simulation_data.db'):
        self.db_path = db_path
    
    def analyze_user_profile(self, session_id: str) -> Dict[str, Any]:
        """
        分析用户画像
        
        Args:
            session_id: 会话ID
        
        Returns:
            用户画像数据
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 获取用户历史选择
        c.execute('''
            SELECT vehicle, bump, location, speed, survival_rate
            FROM user_choices
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (session_id,))
        
        choices = c.fetchall()
        conn.close()
        
        if not choices:
            return self._get_default_profile()
        
        # 分析用户偏好
        vehicles = [c[0] for c in choices]
        locations = [c[2] for c in choices]
        speeds = [c[3] for c in choices]
        survival_rates = [c[4] for c in choices]
        
        # 知识水平评估（基于选择复杂度和分析深度）
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        avg_survival = sum(survival_rates) / len(survival_rates) if survival_rates else 0
        
        if avg_speed > 60 and avg_survival < 50:
            knowledge_level = '高级'  # 敢于探索高风险
        elif avg_speed > 40:
            knowledge_level = '中级'
        else:
            knowledge_level = '初级'
        
        # 兴趣领域分析
        interest_areas = []
        if '高性能跑车' in vehicles or '豪华轿车' in vehicles:
            interest_areas.append('性能探索')
        if '节能型小型车' in vehicles:
            interest_areas.append('环保意识')
        if '学校门口' in locations or '山地滑坡' in locations:
            interest_areas.append('伦理思考')
        if '普通跑道' in locations:
            interest_areas.append('安全测试')
        
        if not interest_areas:
            interest_areas = ['综合探索']
        
        # 风险承受度
        high_risk_count = sum(1 for s in speeds if s >= 50)
        risk_tolerance = '高风险' if high_risk_count > len(speeds) * 0.5 else '中等风险' if high_risk_count > 0 else '低风险'
        
        # 伦理倾向（基于地点选择）
        ethical_orientation = '关注伦理' if '学校门口' in locations else '技术导向'
        
        profile = {
            'session_id': session_id,
            'knowledge_level': knowledge_level,
            'interest_areas': interest_areas,
            'risk_tolerance': risk_tolerance,
            'ethical_orientation': ethical_orientation,
            'learning_preferences': {
                'preferred_depth': '详细' if knowledge_level == '高级' else '适中',
                'preferred_format': '公式推导' if knowledge_level == '高级' else '通俗解释',
                'interactive_level': '高' if len(choices) > 10 else '中'
            },
            'statistics': {
                'total_choices': len(choices),
                'avg_speed': round(avg_speed, 2),
                'avg_survival_rate': round(avg_survival, 2),
                'most_used_vehicle': Counter(vehicles).most_common(1)[0][0] if vehicles else None,
                'most_used_location': Counter(locations).most_common(1)[0][0] if locations else None
            }
        }
        
        # 保存用户画像
        self.save_user_profile(session_id, profile)
        
        return profile
    
    def _get_default_profile(self) -> Dict[str, Any]:
        """获取默认用户画像"""
        return {
            'knowledge_level': '初级',
            'interest_areas': ['综合探索'],
            'risk_tolerance': '中等风险',
            'ethical_orientation': '平衡',
            'learning_preferences': {
                'preferred_depth': '适中',
                'preferred_format': '通俗解释',
                'interactive_level': '中'
            }
        }
    
    def save_user_profile(self, session_id: str, profile: Dict[str, Any]):
        """保存用户画像到数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (session_id, knowledge_level, interest_areas, learning_preferences, 
             risk_tolerance, ethical_orientation, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            profile.get('knowledge_level'),
            json.dumps(profile.get('interest_areas', []), ensure_ascii=False),
            json.dumps(profile.get('learning_preferences', {}), ensure_ascii=False),
            profile.get('risk_tolerance'),
            profile.get('ethical_orientation'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取用户画像"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT knowledge_level, interest_areas, learning_preferences,
                   risk_tolerance, ethical_orientation
            FROM user_profiles
            WHERE session_id = ?
        ''', (session_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'knowledge_level': row[0],
            'interest_areas': json.loads(row[1]) if row[1] else [],
            'learning_preferences': json.loads(row[2]) if row[2] else {},
            'risk_tolerance': row[3],
            'ethical_orientation': row[4]
        }
    
    def adjust_analysis_depth(self, profile: Dict[str, Any], base_query: str) -> str:
        """
        根据用户画像调整分析深度
        
        Args:
            profile: 用户画像
            base_query: 基础查询
        
        Returns:
            调整后的查询
        """
        knowledge_level = profile.get('knowledge_level', '初级')
        interest_areas = profile.get('interest_areas', [])
        
        adjustments = []
        
        # 根据知识水平调整
        if knowledge_level == '高级':
            adjustments.append("请提供详细的公式推导和深入的技术分析。")
        elif knowledge_level == '中级':
            adjustments.append("请提供适中的技术细节，兼顾专业性和可理解性。")
        else:
            adjustments.append("请用通俗易懂的语言解释，避免过于专业的术语。")
        
        # 根据兴趣领域调整重点
        if '性能探索' in interest_areas:
            adjustments.append("请特别关注性能参数和极限情况的分析。")
        if '伦理思考' in interest_areas:
            adjustments.append("请特别关注伦理意义和社会影响的分析。")
        if '环保意识' in interest_areas:
            adjustments.append("请特别关注环境影响和可持续性的分析。")
        
        if adjustments:
            adjusted_query = base_query + "\n\n【个性化调整】\n" + "\n".join(adjustments)
            return adjusted_query
        
        return base_query


# 单例实例
_profile_manager_instance = None

def get_profile_manager() -> UserProfileManager:
    """获取用户画像管理器单例"""
    global _profile_manager_instance
    if _profile_manager_instance is None:
        _profile_manager_instance = UserProfileManager()
    return _profile_manager_instance

