"""
角色协作模块
实现深入的角色辩论、相互质疑和观点融合功能
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class RoleDebateManager:
    """角色辩论管理器"""
    
    def __init__(self, call_role_api_func, get_role_personality_func, roles_dict):
        self.call_role_api = call_role_api_func
        self.get_role_personality = get_role_personality_func
        self.roles_dict = roles_dict
    
    def generate_debate_round(self, role: str, user_choice: Dict, 
                            previous_statements: List[Dict], round_num: int) -> Dict:
        """
        生成一轮辩论
        
        Args:
            role: 角色名称
            user_choice: 用户选择
            previous_statements: 之前的陈述列表
            round_num: 轮次编号
        
        Returns:
            辩论内容
        """
        choice_text = f"""
- 车辆：{user_choice.get('vehicle', '未知')}
- 减速带：{user_choice.get('bump', '未知')}
- 地点：{user_choice.get('location', '未知')}
- 速度：{user_choice.get('speed', 0)} km/h
- 幸存率：{user_choice.get('survival_rate', 0)}%
"""
        
        # 构建其他角色的观点摘要
        other_views = ""
        if previous_statements:
            for stmt in previous_statements:
                if stmt['role'] != role:
                    other_views += f"\n**{stmt['role_name']}的观点**：\n{stmt['content'][:200]}...\n"
        
        if round_num == 1:
            # 第一轮：陈述观点
            query = f"""
用户选择了：
{choice_text}

请从你的专业角度，对这个选择进行第一轮陈述：
1. 明确表达你的立场（支持、反对或中立）
2. 说明你的专业理由（至少3点）
3. 指出你认为最重要的考虑因素

请用清晰的结构，标注为"【第一轮 - 观点陈述】"。
"""
        elif round_num == 2:
            # 第二轮：回应质疑
            query = f"""
用户选择了：
{choice_text}

其他角色的观点：
{other_views}

请从你的专业角度，进行第二轮辩论：
1. 针对其他角色的观点，提出你的质疑或补充
2. 回应可能对你的观点的质疑
3. 说明你的观点与其他观点的差异和联系

请用清晰的结构，标注为"【第二轮 - 回应质疑】"。
"""
        else:
            # 第三轮：总结立场
            query = f"""
用户选择了：
{choice_text}

其他角色的观点：
{other_views}

请从你的专业角度，进行第三轮总结：
1. 总结你的核心立场
2. 说明你与其他角色的共识和分歧
3. 给出最终建议（如果可能，提出融合方案）

请用清晰的结构，标注为"【第三轮 - 总结立场】"。
"""
        
        role_personality = self.get_role_personality(role)
        messages = [
            {"role": "system", "content": role_personality},
            {"role": "user", "content": query}
        ]
        
        response = self.call_role_api(role, messages)
        content = response['choices'][0]['message']['content']
        
        return {
            'role': role,
            'role_name': self.roles_dict[role]['name'],
            'round': round_num,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_interactive_debate(self, user_choice: Dict, 
                                   roles: List[str] = None, 
                                   rounds: int = 3) -> Dict:
        """
        生成交互式辩论（角色之间真正对话）
        
        Args:
            user_choice: 用户选择
            roles: 参与辩论的角色列表
            rounds: 辩论轮数
        
        Returns:
            完整的辩论记录
        """
        if roles is None:
            roles = ['ethicist', 'safety', 'physicist', 'traffic_engineer']
        
        debate_record = {
            'user_choice': user_choice,
            'participants': [self.roles_dict[r]['name'] for r in roles],
            'rounds': []
        }
        
        # 存储每轮所有角色的陈述
        all_statements = []
        
        for round_num in range(1, rounds + 1):
            round_statements = []
            
            for role in roles:
                try:
                    statement = self.generate_debate_round(
                        role, user_choice, all_statements, round_num
                    )
                    round_statements.append(statement)
                    all_statements.append(statement)
                except Exception as e:
                    round_statements.append({
                        'role': role,
                        'role_name': self.roles_dict[role]['name'],
                        'round': round_num,
                        'error': str(e)
                    })
            
            debate_record['rounds'].append({
                'round_number': round_num,
                'statements': round_statements
            })
        
        return debate_record
    
    def extract_conflict_points(self, debate_record: Dict) -> List[Dict]:
        """
        提取观点冲突点
        
        Args:
            debate_record: 辩论记录
        
        Returns:
            冲突点列表
        """
        conflict_points = []
        
        # 分析每轮辩论中的观点差异
        for round_data in debate_record['rounds']:
            statements = round_data['statements']
            
            # 比较不同角色的观点
            for i, stmt1 in enumerate(statements):
                for j, stmt2 in enumerate(statements[i+1:], i+1):
                    if 'error' in stmt1 or 'error' in stmt2:
                        continue
                    
                    # 简单的关键词冲突检测（实际应该用更复杂的NLP）
                    conflict = {
                        'round': round_data['round_number'],
                        'role1': stmt1['role_name'],
                        'role2': stmt2['role_name'],
                        'conflict_type': '观点差异',  # 可以扩展为更细的分类
                        'description': f"{stmt1['role_name']}和{stmt2['role_name']}在第{round_data['round_number']}轮存在观点差异"
                    }
                    conflict_points.append(conflict)
        
        return conflict_points
    
    def generate_consensus_summary(self, debate_record: Dict) -> Dict:
        """
        生成共识总结
        
        Args:
            debate_record: 辩论记录
        
        Returns:
            共识总结
        """
        # 分析所有角色的最终立场
        final_round = debate_record['rounds'][-1] if debate_record['rounds'] else None
        if not final_round:
            return {'consensus': [], 'disagreements': []}
        
        consensus = []
        disagreements = []
        
        # 提取关键观点（简化版，实际应该用NLP分析）
        for stmt in final_round['statements']:
            if 'error' not in stmt:
                # 这里可以添加更复杂的共识分析逻辑
                pass
        
        return {
            'consensus': consensus,
            'disagreements': disagreements,
            'summary': '各角色从不同专业角度提供了深入分析，形成了多维度视角。'
        }


def create_debate_visualization_data(debate_record: Dict) -> Dict:
    """
    创建辩论可视化数据
    
    Args:
        debate_record: 辩论记录
    
    Returns:
        可视化数据
    """
    visualization = {
        'nodes': [],  # 角色节点
        'edges': [],  # 观点关系
        'timeline': []  # 时间线
    }
    
    # 创建角色节点
    participants = debate_record.get('participants', [])
    for i, participant in enumerate(participants):
        visualization['nodes'].append({
            'id': f'role_{i}',
            'label': participant,
            'type': 'role'
        })
    
    # 创建观点关系边
    for round_data in debate_record['rounds']:
        statements = round_data['statements']
        for i, stmt1 in enumerate(statements):
            for j, stmt2 in enumerate(statements[i+1:], i+1):
                if 'error' not in stmt1 and 'error' not in stmt2:
                    visualization['edges'].append({
                        'source': f'role_{i}',
                        'target': f'role_{j}',
                        'type': 'debate',
                        'round': round_data['round_number']
                    })
    
    # 创建时间线
    for round_data in debate_record['rounds']:
        visualization['timeline'].append({
            'round': round_data['round_number'],
            'statements_count': len(round_data['statements']),
            'timestamp': datetime.now().isoformat()
        })
    
    return visualization

