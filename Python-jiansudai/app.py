from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context, send_file
from flask_cors import CORS
import sys
import os
import sqlite3
import json
from datetime import datetime
import traceback
import time
from functools import lru_cache
from collections import OrderedDict

# 添加 ren 文件夹到路径（角色模块）
sys.path.append(os.path.join(os.path.dirname(__file__), 'ren'))

# 导入各个角色模块
from ren import gcs, ll, aqy, jt, wl, d3

# 导入新功能模块
try:
    from role_collaboration import RoleDebateManager, create_debate_visualization_data
    from personalization import get_profile_manager
    from social_features import get_social_manager
    NEW_FEATURES_ENABLED = True
except ImportError as e:
    print(f"[警告] 新功能模块导入失败: {e}")
    NEW_FEATURES_ENABLED = False

app = Flask(__name__, static_folder='.')
# 配置CORS，允许所有来源和所有方法
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     supports_credentials=False,
     allow_headers="*",
     methods="*",
     expose_headers="*",
     max_age=3600)

# 为所有响应添加CORS头（双重保险）
@app.after_request
def after_request(response):
    """为所有响应添加CORS头"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'false')
    return response

# 数据库初始化
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('simulation_data.db')
    c = conn.cursor()
    
    # 用户选择记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            vehicle TEXT,
            bump TEXT,
            location TEXT,
            speed REAL,
            survival_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 角色分析结果表
    c.execute('''
        CREATE TABLE IF NOT EXISTS role_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role_name TEXT,
            analysis_text TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 对话记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role_name TEXT,
            user_message TEXT,
            assistant_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 统计数据表
    c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 角色辩论记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS role_debates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            debate_id TEXT,
            round_number INTEGER,
            role_name TEXT,
            content TEXT,
            response_to_role TEXT,
            conflict_points TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 用户画像表
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            knowledge_level TEXT,
            interest_areas TEXT,
            learning_preferences TEXT,
            risk_tolerance TEXT,
            ethical_orientation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 评论和讨论表
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            parent_id INTEGER,
            user_id TEXT,
            content TEXT,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 分享记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            share_code TEXT UNIQUE,
            share_type TEXT,
            share_data TEXT,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 协作学习记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS collaborations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            collaborator_id TEXT,
            collaboration_type TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ========== LRU缓存实现 ==========
class LRUCache:
    """LRU缓存实现"""
    def __init__(self, capacity=1000):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        """获取缓存值"""
        if key in self.cache:
            # 移动到末尾（最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        """添加缓存值"""
        if key in self.cache:
            # 更新值并移动到末尾
            self.cache.move_to_end(key)
        else:
            # 如果超过容量，删除最旧的项
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()

# 创建全局缓存实例
chart_data_cache = LRUCache(capacity=1000)
analysis_cache = LRUCache(capacity=500)

# 角色映射
ROLES = {
    'engineer': {'module': gcs, 'name': '资深后端工程师'},
    'ethicist': {'module': ll, 'name': '伦理学家'},
    'safety': {'module': aqy, 'name': '安全员'},
    'traffic': {'module': jt, 'name': '交通工程师'},
    'physicist': {'module': wl, 'name': '物理学家'},
    'designer': {'module': d3, 'name': '可视化设计师'}
}

def get_role_personality(role_key):
    """获取角色人格设定"""
    if role_key not in ROLES:
        return None
    role_module = ROLES[role_key]['module']
    role_name = ROLES[role_key]['name']
    return role_module.roles(role_name)

def call_role_api(role_key, messages):
    """调用角色API"""
    if role_key not in ROLES:
        raise ValueError(f"Invalid role: {role_key}")
    role_module = ROLES[role_key]['module']
    return role_module.call_zhipu_api(messages)

# ========== API 路由 ==========

@app.route('/')
def index():
    """提供前端页面"""
    try:
        # 使用绝对路径确保能找到文件
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
        return send_file(html_path)
    except Exception as e:
        return f"Error loading index.html: {str(e)}", 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """健康检查路由 - 用于测试服务器是否正常运行"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    return jsonify({
        'status': 'ok',
        'message': '服务器运行正常',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """分析用户选择，返回多角色分析结果"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        vehicle = data.get('vehicle')
        bump = data.get('bump')
        location = data.get('location')
        speed = data.get('speed', 0)
        survival_rate = data.get('survival_rate', 0)
        
        # 保存用户选择到数据库
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_choices (session_id, vehicle, bump, location, speed, survival_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, vehicle, bump, location, speed, survival_rate))
        conn.commit()
        conn.close()
        
        # 构建分析查询 - 明确伦理问题
        location_ethical_issue = ""
        if location == "学校门口":
            location_ethical_issue = "⚠️ 重要伦理问题：用户选择在学校门口进行高速实验，这是对弱势群体（学生）安全的忽视。学校门口是儿童和青少年聚集的地方，任何高速驾驶实验都会严重威胁他们的生命安全。这反映了个人便利与公共安全责任的严重冲突。"
        elif location == "山地滑坡":
            location_ethical_issue = "⚠️ 极高风险：用户选择了极端危险的地点，这体现了对自身和他人安全的极度忽视。"
        elif location == "普通跑道":
            location_ethical_issue = "用户选择了相对安全的测试环境，体现了对风险控制的考虑。"
        
        user_query = f"""
用户在《飞跃减速带》实验中选择：
- 车辆：{vehicle}
- 减速带：{bump}
- 地点：{location}
- 速度：{speed} km/h
- 幸存率：{survival_rate}%

【重要伦理问题】
{location_ethical_issue}

【分析要求】
请基于你的专业角度，深入分析这个选择背后的伦理意义：
1. **地点选择的伦理含义**：选择{location}作为实验地点，特别是如果速度较高，这反映了什么伦理问题？
   - 如果地点是"学校门口"：这体现了对弱势群体（学生）安全的忽视，是严重的伦理问题，应该降低社会正义和个人责任评分
   - 如果地点是"山地滑坡"：这体现了对极端风险的追求，是对安全的极度忽视
2. **速度选择的伦理含义**：速度{speed} km/h的选择反映了什么价值观？
3. **综合伦理评估**：这个选择组合体现了什么样的伦理倾向？

请给出深刻、准确的专业分析，明确指出伦理问题，不要美化或回避问题。
"""
        
        results = {}
        
        # 伦理学家分析
        try:
            ethicist_personality = get_role_personality('ethicist')
            messages = [
                {"role": "system", "content": ethicist_personality},
                {"role": "user", "content": user_query}
            ]
            response = call_role_api('ethicist', messages)
            ethicist_analysis = response['choices'][0]['message']['content']
            
            # 计算正义度 - 修正逻辑：学校门口应该是忽视学生安全，降低分数
            social_justice = 50
            personal_responsibility = 50
            
            # 地点影响社会正义（学校门口 = 忽视学生安全 = 降低分数）
            if location == '学校门口':
                # 在学校门口进行实验本身就是忽视学生安全的行为
                social_justice -= 40  # 严重降低社会正义
                personal_responsibility -= 30  # 降低个人责任
                if speed >= 50:
                    # 高速更严重
                    social_justice -= 20
                    personal_responsibility -= 15
            elif location == '山地滑坡':
                # 选择极端危险地点 = 极度忽视安全
                social_justice -= 50
                personal_responsibility -= 40
            elif location == '普通跑道':
                # 选择安全测试环境 = 体现责任意识
                social_justice += 15
                personal_responsibility += 10
            
            # 速度影响个人责任（速度越高，责任越低）
            if speed >= 70:
                personal_responsibility -= 25
                social_justice -= 15
            elif speed >= 50:
                personal_responsibility -= 15
                social_justice -= 10
            elif speed < 30:
                personal_responsibility += 15
                social_justice += 10
            
            # 车辆类型影响社会正义（豪华车可能体现资源浪费）
            if vehicle == '豪华轿车':
                social_justice -= 10
            elif vehicle == '节能型小型车':
                social_justice += 10
            
            results['ethicist'] = {
                'analysis': ethicist_analysis,
                'role': '伦理学家',
                'social_justice': min(100, max(0, social_justice)),
                'personal_responsibility': min(100, max(0, personal_responsibility))
            }
            
            print(f"[伦理学家分析] 地点={location}, 速度={speed}km/h")
            print(f"[伦理学家分析] 计算正义度: 社会正义={results['ethicist']['social_justice']}, 个人责任={results['ethicist']['personal_responsibility']}")
            print(f"[伦理学家分析] 分析内容预览: {ethicist_analysis[:200]}...")
            
            # 保存分析结果
            conn = sqlite3.connect('simulation_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, 'ethicist', ethicist_analysis, json.dumps(results['ethicist'])))
            conn.commit()
            conn.close()
        except Exception as e:
            results['ethicist'] = {'error': str(e), 'traceback': traceback.format_exc()}
        
        # 安全员分析
        try:
            safety_personality = get_role_personality('safety')
            messages = [
                {"role": "system", "content": safety_personality},
                {"role": "user", "content": user_query}
            ]
            response = call_role_api('safety', messages)
            safety_analysis = response['choices'][0]['message']['content']
            
            risk_level = 'low' if survival_rate >= 80 else ('medium' if survival_rate >= 60 else 'high')
            recommendations = []
            if speed >= 50:
                recommendations.append('建议降低速度以提高安全性')
            if survival_rate < 60:
                recommendations.append('当前参数组合存在较高风险')
            if not recommendations:
                recommendations.append('当前参数组合相对安全')
            
            results['safety'] = {
                'analysis': safety_analysis,
                'role': '安全员',
                'risk_level': risk_level,
                'recommendations': recommendations
            }
            
            # 保存分析结果
            conn = sqlite3.connect('simulation_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, 'safety', safety_analysis, json.dumps(results['safety'])))
            conn.commit()
            conn.close()
        except Exception as e:
            results['safety'] = {'error': str(e), 'traceback': traceback.format_exc()}
        
        # 物理学家分析
        try:
            physicist_personality = get_role_personality('physicist')
            messages = [
                {"role": "system", "content": physicist_personality},
                {"role": "user", "content": user_query}
            ]
            response = call_role_api('physicist', messages)
            physicist_analysis = response['choices'][0]['message']['content']
            
            # 计算物理参数
            v0 = speed / 3.6  # m/s
            max_acceleration = v0 * 2 + 5  # 简化的加速度计算
            impact_force = v0 * 1000 + 2000  # 简化的冲击力计算
            
            results['physicist'] = {
                'analysis': physicist_analysis,
                'role': '物理学家',
                'max_acceleration': round(max_acceleration, 2),
                'impact_force': round(impact_force, 0),
                'velocity': round(v0, 2)
            }
            
            # 保存分析结果
            conn = sqlite3.connect('simulation_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, 'physicist', physicist_analysis, json.dumps(results['physicist'])))
            conn.commit()
            conn.close()
        except Exception as e:
            results['physicist'] = {'error': str(e), 'traceback': traceback.format_exc()}
        
        # 交通工程师分析
        try:
            traffic_personality = get_role_personality('traffic')
            messages = [
                {"role": "system", "content": traffic_personality},
                {"role": "user", "content": user_query}
            ]
            response = call_role_api('traffic', messages)
            traffic_analysis = response['choices'][0]['message']['content']
            
            results['traffic'] = {
                'analysis': traffic_analysis,
                'role': '交通工程师',
                'road_design_score': min(100, max(0, 50 + (survival_rate - 50) * 0.4))
            }
            
            # 保存分析结果
            conn = sqlite3.connect('simulation_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, 'traffic', traffic_analysis, json.dumps(results['traffic'])))
            conn.commit()
            conn.close()
        except Exception as e:
            results['traffic'] = {'error': str(e), 'traceback': traceback.format_exc()}
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """与特定角色对话"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        role = data.get('role')  # engineer, ethicist, safety, etc.
        message = data.get('message')
        history = data.get('history', [])
        
        if role not in ROLES:
            return jsonify({'error': 'Invalid role'}), 400
        
        # 获取角色人格设定
        role_personality = get_role_personality(role)
        
        # 构建消息列表
        messages = [{"role": "system", "content": role_personality}]
        
        # 添加历史对话（限制最近10轮）
        if history:
            recent_history = history[-20:]  # 最近20条消息（10轮对话）
            messages.extend(recent_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        # 调用API
        response = call_role_api(role, messages)
        assistant_reply = response['choices'][0]['message']['content']
        
        # 保存对话记录
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO conversations (session_id, role_name, user_message, assistant_message)
            VALUES (?, ?, ?, ?)
        ''', (session_id, role, message, assistant_reply))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'response': assistant_reply,
            'role': ROLES[role]['name']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/simulation/advanced', methods=['POST', 'OPTIONS'])
def advanced_simulation():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    """高级物理模拟（后端计算）"""
    try:
        data = request.json
        vehicle = data.get('vehicle')
        bump = data.get('bump')
        speed = data.get('speed', 0)
        location = data.get('location')
        
        # 调用物理学家进行精确计算
        physicist_personality = get_role_personality('physicist')
        query = f"""
请基于以下参数进行精确的物理计算：
- 车辆：{vehicle}
- 减速带：{bump}
- 速度：{speed} km/h
- 地点：{location}

请计算：
1. 最大加速度
2. 冲击力
3. 位移
4. 弹跳高度
5. 安全评估

请给出详细的物理计算过程和结果。
"""
        
        messages = [
            {"role": "system", "content": physicist_personality},
            {"role": "user", "content": query}
        ]
        
        response = call_role_api('physicist', messages)
        physics_analysis = response['choices'][0]['message']['content']
        
        return jsonify({
            'success': True,
            'detailed_physics': {
                'analysis': physics_analysis,
                'calculations': {}
            },
            'recommendations': []
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/generate', methods=['POST', 'OPTIONS'])
def generate_report():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    """生成完整的分析报告"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        # 从数据库获取所有分析结果
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        
        # 获取用户选择
        c.execute('''
            SELECT * FROM user_choices WHERE session_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (session_id,))
        choice = c.fetchone()
        
        # 获取所有角色分析
        c.execute('''
            SELECT role_name, analysis_text, metadata FROM role_analyses 
            WHERE session_id = ? ORDER BY created_at
        ''', (session_id,))
        analyses = c.fetchall()
        
        conn.close()
        
        if not choice:
            return jsonify({'error': 'Session not found'}), 404
        
        # 构建报告
        report = {
            'session_id': session_id,
            'user_choice': {
                'vehicle': choice[2],
                'bump': choice[3],
                'location': choice[4],
                'speed': choice[5],
                'survival_rate': choice[6]
            },
            'analyses': {}
        }
        
        for analysis in analyses:
            role_name, analysis_text, metadata = analysis
            report['analyses'][role_name] = {
                'text': analysis_text,
                'metadata': json.loads(metadata) if metadata else {}
            }
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET', 'OPTIONS'])
def get_statistics():
    """获取统计数据"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    try:
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        
        # 总模拟次数
        c.execute('SELECT COUNT(*) FROM user_choices')
        total_simulations = c.fetchone()[0]
        
        # 平均速度
        c.execute('SELECT AVG(speed) FROM user_choices WHERE speed > 0')
        avg_speed = c.fetchone()[0] or 0
        
        # 平均幸存率
        c.execute('SELECT AVG(survival_rate) FROM user_choices WHERE survival_rate > 0')
        avg_survival = c.fetchone()[0] or 0
        
        # 最受欢迎的车辆
        c.execute('''
            SELECT vehicle, COUNT(*) as count FROM user_choices 
            GROUP BY vehicle ORDER BY count DESC LIMIT 1
        ''')
        popular_vehicle = c.fetchone()
        
        # 最受欢迎的地点
        c.execute('''
            SELECT location, COUNT(*) as count FROM user_choices 
            GROUP BY location ORDER BY count DESC LIMIT 1
        ''')
        popular_location = c.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_simulations': total_simulations,
                'average_speed': round(avg_speed, 2),
                'average_survival_rate': round(avg_survival, 2),
                'popular_vehicle': popular_vehicle[0] if popular_vehicle else None,
                'popular_location': popular_location[0] if popular_location else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/<session_id>', methods=['GET', 'OPTIONS'])
def get_history(session_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response, 200
    """获取会话历史"""
    try:
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        
        # 获取用户选择
        c.execute('''
            SELECT * FROM user_choices WHERE session_id = ? ORDER BY created_at
        ''', (session_id,))
        choices = c.fetchall()
        
        # 获取对话记录
        c.execute('''
            SELECT role_name, user_message, assistant_message, created_at 
            FROM conversations WHERE session_id = ? ORDER BY created_at
        ''', (session_id,))
        conversations = c.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'choices': [
                {
                    'id': c[0],
                    'vehicle': c[2],
                    'bump': c[3],
                    'location': c[4],
                    'speed': c[5],
                    'survival_rate': c[6],
                    'created_at': c[7]
                }
                for c in choices
            ],
            'conversations': [
                {
                    'role': conv[0],
                    'user_message': conv[1],
                    'assistant_message': conv[2],
                    'created_at': conv[3]
                }
                for conv in conversations
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 创新 API 端点 ==========

@app.route('/api/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    """智能参数推荐系统 - 基于用户历史选择推荐最佳参数组合"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        user_history = data.get('history', [])
        current_preferences = data.get('preferences', {})
        
        # 构建推荐查询
        history_text = "\n".join([f"- {h}" for h in user_history[-5:]]) if user_history else "无历史记录"
        query = f"""
基于用户的历史选择：
{history_text}

当前偏好：{current_preferences}

请推荐一个既能保证安全（幸存率>80%），又能让用户体验刺激的参数组合。
推荐格式：
1. 车辆类型：[具体车型]
2. 减速带类型：[具体类型]
3. 地点：[具体地点]
4. 速度范围：[建议速度范围]
5. 推荐理由：[简要说明]

请给出专业且实用的推荐。
"""
        
        # 调用物理学家角色进行推荐
        physicist_personality = get_role_personality('physicist')
        messages = [
            {"role": "system", "content": physicist_personality},
            {"role": "user", "content": query}
        ]
        
        response = call_role_api('physicist', messages)
        recommendation = response['choices'][0]['message']['content']
        
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/risk/assess', methods=['POST', 'OPTIONS'])
def assess_risk():
    """实时风险评估与预警 - 评估用户当前选择的危险程度"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        speed = data.get('speed', 0)
        vehicle = data.get('vehicle')
        bump = data.get('bump')
        location = data.get('location')
        
        # 构建风险评估查询
        query = f"""
用户即将选择：
- 车辆：{vehicle}
- 减速带：{bump}
- 地点：{location}
- 速度：{speed} km/h

请评估这个组合的危险程度（1-10分），并给出：
1. 危险等级（低/中/高/极高）
2. 主要风险点（列出3-5个）
3. 紧急建议（如果危险等级≥高，给出3条具体建议）

请用专业且易懂的语言回答。
"""
        
        # 调用安全员角色
        safety_personality = get_role_personality('safety')
        messages = [
            {"role": "system", "content": safety_personality},
            {"role": "user", "content": query}
        ]
        
        response = call_role_api('safety', messages)
        risk_assessment = response['choices'][0]['message']['content']
        
        # 尝试提取风险等级（简单解析）
        risk_level = 'unknown'
        if '极高' in risk_assessment or '10' in risk_assessment or '9' in risk_assessment:
            risk_level = 'extreme'
        elif '高' in risk_assessment or '7' in risk_assessment or '8' in risk_assessment:
            risk_level = 'high'
        elif '中' in risk_assessment or '4' in risk_assessment or '5' in risk_assessment or '6' in risk_assessment:
            risk_level = 'medium'
        elif '低' in risk_assessment or '1' in risk_assessment or '2' in risk_assessment or '3' in risk_assessment:
            risk_level = 'low'
        
        return jsonify({
            'success': True,
            'risk_level': risk_level,
            'assessment': risk_assessment,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/learning/path', methods=['POST', 'OPTIONS'])
def generate_learning_path():
    """个性化学习路径生成 - 基于用户选择模式生成学习路径"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        user_choices = data.get('choices', [])
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        
        query = f"""
用户的选择模式：
{json.dumps(user_choices, ensure_ascii=False, indent=2)}

请为这个用户设计一个学习路径，帮助他：
1. 理解车辆动力学原理
2. 认识安全驾驶的重要性
3. 培养伦理责任感

生成格式：3-5个学习阶段，每个阶段包含：
- 阶段名称
- 学习目标（2-3个）
- 实践建议（1-2个）
- 预期收获

请用清晰的结构化格式输出。
"""
        
        # 综合多个角色视角
        learning_paths = {}
        roles_to_query = ['physicist', 'ethicist', 'safety']
        
        for role in roles_to_query:
            try:
                role_personality = get_role_personality(role)
                messages = [
                    {"role": "system", "content": role_personality},
                    {"role": "user", "content": query}
                ]
                response = call_role_api(role, messages)
                learning_paths[role] = response['choices'][0]['message']['content']
            except Exception as e:
                learning_paths[role] = {'error': str(e)}
        
        # 保存学习路径
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
            VALUES (?, ?, ?, ?)
        ''', (session_id, 'learning_path', json.dumps(learning_paths), json.dumps({'type': 'learning_path'})))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'learning_path': learning_paths,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/report/title', methods=['POST', 'OPTIONS'])
def generate_report_title():
    """智能报告标题生成 - 基于分析结果生成吸引人的报告标题"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        analysis = data.get('analysis', '')
        personality_traits = data.get('personality_traits', {})
        justice_index = data.get('justice_index', {})
        
        query = f"""
基于以下分析结果，生成3个报告标题：

分析结果：
{analysis}

性格特质：
{json.dumps(personality_traits, ensure_ascii=False)}

正义感指数：
{json.dumps(justice_index, ensure_ascii=False)}

要求：
1. 标题要吸引人且准确反映用户特点
2. 体现用户的性格特质（如冒险、谨慎、社会责任感等）
3. 长度在10-20字之间
4. 风格可以是：诗意、专业、激励、反思等不同风格
5. 每个标题后面用括号标注风格类型

格式：
标题1：[标题内容]（风格）
标题2：[标题内容]（风格）
标题3：[标题内容]（风格）
"""
        
        # 调用可视化设计师角色（更擅长创意）
        designer_personality = get_role_personality('designer')
        messages = [
            {"role": "system", "content": designer_personality},
            {"role": "user", "content": query}
        ]
        
        response = call_role_api('designer', messages)
        titles_text = response['choices'][0]['message']['content']
        
        # 简单解析标题（可以后续优化）
        titles = []
        lines = titles_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and ('标题' in line or '：' in line or ':' in line):
                # 提取标题内容
                if '：' in line:
                    title_part = line.split('：', 1)[1] if '：' in line else line.split(':', 1)[1]
                    title_part = title_part.split('（')[0].split('(')[0].strip()
                    if title_part:
                        titles.append(title_part)
        
        # 如果解析失败，返回原始文本
        if not titles:
            titles = [titles_text]
        
        return jsonify({
            'success': True,
            'titles': titles[:3],  # 最多返回3个
            'full_response': titles_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/debate', methods=['POST', 'OPTIONS'])
def generate_debate():
    """多角色辩论生成 - 让多个角色就用户的选择进行辩论"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        user_choice = data.get('choice', {})
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        
        choice_text = f"""
- 车辆：{user_choice.get('vehicle', '未知')}
- 减速带：{user_choice.get('bump', '未知')}
- 地点：{user_choice.get('location', '未知')}
- 速度：{user_choice.get('speed', 0)} km/h
- 幸存率：{user_choice.get('survival_rate', 0)}%
"""
        
        query = f"""
用户选择了：
{choice_text}

请从你的专业角度，对这个选择进行3轮辩论：
1. 第一轮：陈述你的观点（支持或反对，并说明理由）
2. 第二轮：回应其他角色的质疑（假设伦理学家、安全员、物理学家会提出不同观点）
3. 第三轮：总结你的立场（给出最终建议）

请用清晰的结构，每轮用"【第X轮】"标注。
"""
        
        debate = {}
        roles = ['ethicist', 'safety', 'physicist']
        
        for role in roles:
            try:
                role_personality = get_role_personality(role)
                messages = [
                    {"role": "system", "content": role_personality},
                    {"role": "user", "content": query}
                ]
                response = call_role_api(role, messages)
                debate[role] = {
                    'role_name': ROLES[role]['name'],
                    'content': response['choices'][0]['message']['content']
                }
            except Exception as e:
                debate[role] = {
                    'role_name': ROLES[role]['name'],
                    'error': str(e)
                }
        
        # 保存辩论记录
        conn = sqlite3.connect('simulation_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
            VALUES (?, ?, ?, ?)
        ''', (session_id, 'debate', json.dumps(debate), json.dumps({'type': 'debate'})))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'debate': debate,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/questions/generate', methods=['POST', 'OPTIONS'])
def generate_questions():
    """智能问题生成器 - 基于用户选择生成引导性思考问题"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        choice = data.get('choice', {})
        question_type = data.get('type', 'reflection')  # reflection, ethics, safety, physics
        
        choice_text = f"""
- 车辆：{choice.get('vehicle', '未知')}
- 减速带：{choice.get('bump', '未知')}
- 地点：{choice.get('location', '未知')}
- 速度：{choice.get('speed', 0)} km/h
- 幸存率：{choice.get('survival_rate', 0)}%
"""
        
        question_prompts = {
            'reflection': '反思自己的选择，理解背后的动机',
            'ethics': '理解背后的伦理意义，思考社会责任',
            'safety': '考虑安全责任，认识风险',
            'physics': '理解物理原理，学习科学知识'
        }
        
        query = f"""
用户选择了：
{choice_text}

请生成5个引导性思考问题，帮助用户：
{question_prompts.get(question_type, question_prompts['reflection'])}

要求：
1. 问题要循序渐进，从简单到深入
2. 每个问题都要有启发性，能引发思考
3. 问题要具体，不要过于抽象
4. 格式：用数字编号，每个问题一行

示例格式：
1. [问题1]
2. [问题2]
3. [问题3]
4. [问题4]
5. [问题5]
"""
        
        # 根据问题类型选择角色
        role_map = {
            'reflection': 'ethicist',
            'ethics': 'ethicist',
            'safety': 'safety',
            'physics': 'physicist'
        }
        role = role_map.get(question_type, 'ethicist')
        
        role_personality = get_role_personality(role)
        messages = [
            {"role": "system", "content": role_personality},
            {"role": "user", "content": query}
        ]
        
        response = call_role_api(role, messages)
        questions_text = response['choices'][0]['message']['content']
        
        # 解析问题（简单提取）
        questions = []
        lines = questions_text.split('\n')
        for line in lines:
            line = line.strip()
            # 匹配数字开头的行
            if line and (line[0].isdigit() or line.startswith('1.') or line.startswith('一、')):
                # 移除编号
                question = line.split('.', 1)[1] if '.' in line else line
                question = question.split('、', 1)[1] if '、' in question else question
                question = question.strip()
                if question and len(question) > 5:  # 过滤太短的内容
                    questions.append(question)
        
        # 如果解析失败，返回原始文本
        if not questions:
            questions = [questions_text]
        
        return jsonify({
            'success': True,
            'questions': questions[:5],  # 最多返回5个
            'full_response': questions_text,
            'question_type': question_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/physics/calculate', methods=['POST', 'OPTIONS'])
def physics_calculate():
    """物理学家计算模拟结果 - 计算幸存率、最大加速度、弹跳高度等（支持流式输出）"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        vehicle = data.get('vehicle', '未知')
        bump = data.get('bump', '未知')
        location = data.get('location', '未知')
        weather = data.get('weather', '晴')  # 天气条件
        speed = float(data.get('speed', 0))
        stream = data.get('stream', True)  # 默认使用流式输出
        
        # 构建计算查询，要求物理学家基于物理公式计算
        speed_mps = speed / 3.6 if speed > 0 else 0
        query = f"""
请作为物理学家，基于弹簧-质量-阻尼系统模型，计算以下参数组合的物理结果：

【输入参数】
- 车辆类型：{vehicle}
- 减速带类型：{bump}
- 地点：{location}
- 天气条件：{weather}
- 初始速度：{speed} km/h ({speed_mps:.2f} m/s)

【计算要求】
请严格按照物理公式计算，并返回JSON格式的结果：

1. **最大加速度** (maxAcceleration, 单位: m/s²)
   - 使用公式：a_max = (F₀/m) + (ω_n² × x_max)
   - 其中：ω_n = √(k/m)，x_max = (F₀/k) × [1 + exp(-ζω_n t_pass)]

2. **最大位移** (maxDisplacement, 单位: m)
   - 使用公式：x_max = (F₀/k) × [1 + exp(-ζω_n t_pass)]

3. **速度变化** (velocityChange, 单位: m/s)
   - 计算车辆通过减速带时的速度变化量

4. **弹跳高度** (bounceHeight, 单位: m)
   - 使用公式：h = max(0, (x_max - H) × 0.5)
   - 其中H是减速带高度

5. **通过时间** (t_pass, 单位: s)
   - t_pass = L / v₀，其中L是减速带长度

6. **自然频率** (omega_n, 单位: rad/s)
   - ω_n = √(k/m)

7. **阻尼比** (zeta, 无量纲)
   - ζ = c/(2√(km))

8. **幸存率** (survivalRate, 单位: %, 范围: 0-100)
   - 基于以下标准评估：
     * 最大加速度 > 3g (29.4 m/s²) → 高风险，幸存率 < 40%
     * 最大加速度 2g-3g (19.6-29.4 m/s²) → 中风险，幸存率 40-60%
     * 最大加速度 1g-2g (9.8-19.6 m/s²) → 低风险，幸存率 60-80%
     * 最大加速度 < 1g (9.8 m/s²) → 安全，幸存率 > 80%
   - 同时考虑弹跳高度：弹跳高度 > 0.1m → 降低幸存率10-20%
   - 考虑速度：速度 > 50 km/h → 降低幸存率5-15%

【输出格式】
请严格按照以下JSON格式返回，不要添加任何其他文字说明：

{{
    "maxAcceleration": 数值,
    "maxDisplacement": 数值,
    "velocityChange": 数值,
    "bounceHeight": 数值,
    "t_pass": 数值,
    "omega_n": 数值,
    "zeta": 数值,
    "survivalRate": 数值,
    "result": "安全通过" 或 "可能通过" 或 "危险" 或 "极危险",
    "calculation_steps": "简要说明计算步骤（1-2句话）"
}}

请确保所有数值都是基于物理公式的精确计算，不要随意估算。
"""
        
        # 调用物理学家角色
        if stream:
            # 流式输出模式
            def generate():
                try:
                    physicist_personality = get_role_personality('physicist')
                    if not physicist_personality:
                        yield f"data: {json.dumps({'type': 'error', 'error': '无法获取物理学家角色设定'})}\n\n"
                        return
                    
                    messages = [
                        {"role": "system", "content": physicist_personality},
                        {"role": "user", "content": query}
                    ]
                    
                    # 发送开始信号
                    yield f"data: {json.dumps({'type': 'start', 'message': '开始计算...'})}\n\n"
                    time.sleep(0.8)  # 增加到0.8秒
                    
                    yield f"data: {json.dumps({'type': 'progress', 'step': '建立物理模型', 'progress': 20})}\n\n"
                    time.sleep(1.2)  # 增加到1.2秒，让用户明显看到
                    
                    yield f"data: {json.dumps({'type': 'progress', 'step': '推导公式', 'progress': 40})}\n\n"
                    time.sleep(1.2)  # 增加到1.2秒
                    
                    yield f"data: {json.dumps({'type': 'progress', 'step': '进行计算', 'progress': 60})}\n\n"
                    time.sleep(0.8)  # 在API调用前给用户看到进度
                    
                    # 调用API（这里会阻塞，但我们已经显示了进度）
                    response = call_role_api('physicist', messages)
                    if not response or 'choices' not in response or len(response['choices']) == 0:
                        yield f"data: {json.dumps({'type': 'error', 'error': 'API返回数据格式错误'})}\n\n"
                        return
                    
                    yield f"data: {json.dumps({'type': 'progress', 'step': '验证结果', 'progress': 80})}\n\n"
                    time.sleep(0.8)
                    
                    result_text = response['choices'][0]['message']['content']
                    if not result_text:
                        yield f"data: {json.dumps({'type': 'error', 'error': 'API返回的计算结果为空'})}\n\n"
                        return
                    
                    # 尝试从返回文本中提取JSON
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', result_text)
                    if json_match:
                        result_data = json.loads(json_match.group())
                        
                        # 逐步发送计算结果，大幅增加延迟让用户明显看到逐步显示
                        yield f"data: {json.dumps({'type': 'result', 'key': 'maxAcceleration', 'value': result_data.get('maxAcceleration', 0)})}\n\n"
                        time.sleep(0.8)  # 增加到0.8秒
                        yield f"data: {json.dumps({'type': 'result', 'key': 'maxDisplacement', 'value': result_data.get('maxDisplacement', 0)})}\n\n"
                        time.sleep(0.6)
                        yield f"data: {json.dumps({'type': 'result', 'key': 'velocityChange', 'value': result_data.get('velocityChange', 0)})}\n\n"
                        time.sleep(0.6)
                        yield f"data: {json.dumps({'type': 'result', 'key': 'bounceHeight', 'value': result_data.get('bounceHeight', 0)})}\n\n"
                        time.sleep(0.8)  # 弹跳高度是重要结果，延迟更长
                        yield f"data: {json.dumps({'type': 'result', 'key': 't_pass', 'value': result_data.get('t_pass', 0)})}\n\n"
                        time.sleep(0.5)
                        yield f"data: {json.dumps({'type': 'result', 'key': 'omega_n', 'value': result_data.get('omega_n', 0)})}\n\n"
                        time.sleep(0.5)
                        yield f"data: {json.dumps({'type': 'result', 'key': 'zeta', 'value': result_data.get('zeta', 0)})}\n\n"
                        time.sleep(0.6)
                        yield f"data: {json.dumps({'type': 'result', 'key': 'survivalRate', 'value': result_data.get('survivalRate', 0)})}\n\n"
                        time.sleep(1.0)  # 幸存率是最重要的，延迟最长（1秒）
                        yield f"data: {json.dumps({'type': 'result', 'key': 'result', 'value': result_data.get('result', '未知')})}\n\n"
                        time.sleep(0.5)
                        
                        # 发送完整结果
                        yield f"data: {json.dumps({'type': 'complete', 'physics': result_data})}\n\n"
                        
                        # 保存计算结果（异步，不阻塞）
                        try:
                            session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
                            conn = sqlite3.connect('simulation_data.db')
                            c = conn.cursor()
                            c.execute('''
                                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                                VALUES (?, ?, ?, ?)
                            ''', (session_id, 'physicist_calculation', result_text, json.dumps({
                                'type': 'physics_calculation',
                                'vehicle': vehicle,
                                'bump': bump,
                                'speed': speed,
                                'location': location,
                                'result': result_data
                            })))
                            conn.commit()
                            conn.close()
                        except Exception as db_error:
                            print(f"警告：保存计算结果到数据库失败: {db_error}")
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'error': '无法从返回结果中提取JSON数据'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            response_obj = Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Methods': '*'
                }
            )
            return response_obj
        else:
            # 非流式输出模式（原有逻辑）
            try:
                physicist_personality = get_role_personality('physicist')
                if not physicist_personality:
                    raise ValueError("无法获取物理学家角色设定")
                
                messages = [
                    {"role": "system", "content": physicist_personality},
                    {"role": "user", "content": query}
                ]
                
                response = call_role_api('physicist', messages)
                if not response or 'choices' not in response or len(response['choices']) == 0:
                    raise ValueError("API返回数据格式错误")
                
                result_text = response['choices'][0]['message']['content']
                if not result_text:
                    raise ValueError("API返回的计算结果为空")
                
                # 尝试从返回文本中提取JSON
                import re
                json_match = re.search(r'\{[\s\S]*\}', result_text)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    raise ValueError("无法从返回结果中提取JSON数据")
                    
            except Exception as api_error:
                return jsonify({
                    'success': False,
                    'error': f'物理学家计算API调用失败: {str(api_error)}',
                    'traceback': traceback.format_exc()
                }), 500
            
            # 保存计算结果
            try:
                session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
                conn = sqlite3.connect('simulation_data.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, 'physicist_calculation', result_text, json.dumps({
                    'type': 'physics_calculation',
                    'vehicle': vehicle,
                    'bump': bump,
                    'speed': speed,
                    'location': location,
                    'result': result_data
                })))
                conn.commit()
                conn.close()
            except Exception as db_error:
                print(f"警告：保存计算结果到数据库失败: {db_error}")
            
            return jsonify({
                'success': True,
                'physics': result_data,
                'role': '物理学家',
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/physics/analyze', methods=['POST', 'OPTIONS'])
def physics_analyze():
    """物理学家公式分析 - 运用物理公式详细分析模拟结果"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        # 打印请求信息用于调试
        print(f"[物理学家分析] 请求方法: {request.method}")
        print(f"[物理学家分析] Content-Type: {request.content_type}")
        print(f"[物理学家分析] 请求数据长度: {len(request.data) if request.data else 0}")
        print(f"[物理学家分析] 原始请求数据: {request.data[:500] if request.data else 'None'}")
        
        # 尝试多种方式获取数据
        data = None
        if request.is_json:
            data = request.json
        else:
            # 如果不是JSON格式，尝试手动解析
            try:
                if request.data:
                    data = json.loads(request.data.decode('utf-8'))
                else:
                    # 尝试从form数据获取
                    data = request.form.to_dict()
            except Exception as parse_error:
                print(f"[物理学家分析] JSON解析失败: {parse_error}")
                return jsonify({
                    'success': False,
                    'error': f'数据格式错误: {str(parse_error)}',
                    'content_type': request.content_type,
                    'data_preview': str(request.data[:200]) if request.data else 'None'
                }), 400
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'content_type': request.content_type,
                'has_data': bool(request.data)
            }), 400
        
        # 打印接收到的数据用于调试
        print(f"[物理学家分析] 接收到的数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        vehicle = data.get('vehicle', '未知')
        bump = data.get('bump', '未知')
        location = data.get('location', '未知')
        weather = data.get('weather', '晴')  # 天气条件
        speed = float(data.get('speed', 0))
        survival_rate = float(data.get('survival_rate', 0))
        physics_data = data.get('physics', {})  # 前端计算的物理数据
        
        print(f"[物理学家分析] 解析后的参数: vehicle={vehicle}, bump={bump}, location={location}, weather={weather}, speed={speed}, survival_rate={survival_rate}")
        print(f"[物理学家分析] physics_data: {json.dumps(physics_data, ensure_ascii=False, indent=2)}")
        
        # 验证数据完整性
        if not physics_data or len(physics_data) == 0:
            print("[警告] physics_data 为空或未提供！")
        else:
            print(f"[物理学家分析] 数据验证:")
            print(f"  - maxAcceleration: {physics_data.get('maxAcceleration', '缺失')}")
            print(f"  - maxDisplacement: {physics_data.get('maxDisplacement', '缺失')}")
            print(f"  - velocityChange: {physics_data.get('velocityChange', '缺失')}")
            print(f"  - bounceHeight: {physics_data.get('bounceHeight', '缺失')}")
            print(f"  - t_pass: {physics_data.get('t_pass', '缺失')}")
            print(f"  - omega_n: {physics_data.get('omega_n', '缺失')}")
            print(f"  - zeta: {physics_data.get('zeta', '缺失')}")
        
        # 安全获取物理数据，处理 None 值
        def safe_get_float(d, key, default=0):
            value = d.get(key, default)
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        max_acceleration = safe_get_float(physics_data, 'maxAcceleration', 0)
        max_displacement = safe_get_float(physics_data, 'maxDisplacement', 0)
        velocity_change = safe_get_float(physics_data, 'velocityChange', 0)
        bounce_height = safe_get_float(physics_data, 'bounceHeight', 0)
        t_pass = safe_get_float(physics_data, 't_pass', 0)
        omega_n = safe_get_float(physics_data, 'omega_n', 0)
        zeta = safe_get_float(physics_data, 'zeta', 0)
        
        # 构建详细的物理分析查询
        speed_mps = speed / 3.6 if speed > 0 else 0
        
        # ========== 动态上下文适应 ==========
        # 根据用户选择动态调整分析深度和重点
        if survival_rate < 40:
            urgency_level = "极高风险"
            analysis_depth = "非常详细"
            safety_emphasis = "强烈"
            focus_areas = "安全评估、风险分析、物理极限"
            analysis_priority = "请特别关注安全风险，详细分析为什么这个速度/参数组合会导致如此低的幸存率，并强烈警告用户。"
        elif survival_rate < 60:
            urgency_level = "高风险"
            analysis_depth = "详细"
            safety_emphasis = "中等"
            focus_areas = "安全评估、参数影响分析"
            analysis_priority = "请重点关注安全因素，分析参数对安全性的影响，并提醒用户注意风险。"
        elif survival_rate < 80:
            urgency_level = "中等风险"
            analysis_depth = "标准"
            safety_emphasis = "提醒"
            focus_areas = "物理过程分析、参数优化"
            analysis_priority = "请进行标准的物理分析，适当提醒安全因素，并分析如何优化参数。"
        else:
            urgency_level = "相对安全"
            analysis_depth = "标准"
            safety_emphasis = "提醒"
            focus_areas = "物理过程分析、参数优化、性能分析"
            analysis_priority = "请进行标准的物理分析，可以更多关注物理过程和参数优化。"
        
        # 根据速度调整分析重点
        if speed > 80:
            speed_focus = "请特别关注高速情况下的动力学特性，分析高速通过减速带的物理极限和风险。"
        elif speed > 50:
            speed_focus = "请关注中高速情况下的动力学特性，分析参数对系统响应的影响。"
        else:
            speed_focus = "请关注低速情况下的动力学特性，分析为什么速度较低时系统响应较小。"
        
        # 根据地点调整分析重点
        if location == "山地滑坡":
            location_focus = "请特别关注山地滑坡环境下的极端风险，详细分析为什么这种环境下幸存率会大幅降低，并强烈警告用户。"
        elif location == "普通跑道":
            location_focus = "请关注普通跑道环境下的动力学特性，分析这种相对安全环境下的物理过程。"
        else:
            location_focus = "请关注当前环境下的动力学特性，分析环境因素对系统的影响。"
        
        query = f"""
请作为物理学家，运用物理公式详细分析以下模拟结果：

【情境感知分析 - 动态调整】
当前情境：{urgency_level}
- 幸存率：{survival_rate}%
- 速度：{speed} km/h ({speed_mps:.2f} m/s)
- 地点：{location}
- 天气：{weather}

根据当前情境，请进行{analysis_depth}分析，并{safety_emphasis}强调安全因素。
分析重点：{focus_areas}
{analysis_priority}
{speed_focus}
{location_focus}

【模拟参数】
- 车辆类型：{vehicle}
- 减速带类型：{bump}
- 地点：{location}
- 天气条件：{weather}
- 初始速度：{speed} km/h ({speed_mps:.2f} m/s)
- 幸存率：{survival_rate}%

【前端计算的物理数据 - 已提供，必须使用】
以下数据已经由前端计算完成，**必须直接使用这些数值**，不要再说"没有提供"或"无法计算"：

- **最大加速度**：{max_acceleration:.2f} m/s² （已提供）
- **最大位移**：{max_displacement:.4f} m （已提供）
- **速度变化**：{velocity_change:.2f} m/s （已提供）
- **弹跳高度**：{bounce_height:.4f} m ({bounce_height*100:.2f} cm) （已提供）
- **通过时间**：{t_pass:.3f} s （已提供）
- **自然频率**：{omega_n:.2f} rad/s （已提供）
- **阻尼比**：{zeta:.3f} （已提供）

**重要：这些数据已经全部提供，即使某些值为0，也要使用这些实际数值进行分析，不要再说"没有提供"或"无法计算"！**

【分析要求 - 重要提示】
**必须使用上述前端提供的实际数据，不能使用占位符、"[值]"或"待确定"！如果数据为0，请说明为什么为0（例如：速度太低、参数不合适等），但必须使用这个0值进行分析！**

请按照以下步骤进行详细分析，展示完整的思考过程，所有数值必须使用前端提供的实际数据：

1. **建立物理模型**
   - 说明使用的物理模型（弹簧-质量-阻尼系统）
   - **直接使用前端提供的物理参数**（自然频率ω_n、阻尼比ζ、最大加速度、最大位移等）
   - 写出运动方程：m(d²x/dt²) + c(dx/dt) + kx = F_ext(t)
   - **不要猜测参数值，直接使用前端计算结果**

2. **参数分析（基于前端数据）**
   - **必须使用前端提供的实际数值（已全部提供）**：
     * 自然频率ω_n = {omega_n:.2f} rad/s （已提供，直接使用）
     * 阻尼比ζ = {zeta:.3f} （已提供，直接使用）
     * 最大加速度 = {max_acceleration:.2f} m/s² （已提供，直接使用）
     * 最大位移 = {max_displacement:.4f} m （已提供，直接使用）
     * 速度变化 = {velocity_change:.2f} m/s （已提供，直接使用）
     * 弹跳高度 = {bounce_height:.4f} m （已提供，直接使用）
     * 通过时间 = {t_pass:.3f} s （已提供，直接使用）
   - **基于这些实际数值**，分析系统特性
   - 分析车辆参数对系统的影响（基于前端数据推断）
   - 分析减速带参数（作用力幅值F₀、频率ω）的影响
   - **重要：这些数据已经全部提供，不能再说"没有提供"或"无法计算"，必须使用上述实际数值，即使为0也要使用并说明原因**
   - **分析天气因素对系统的影响**：
     * 晴天：路面干燥，摩擦系数μ正常（约0.7-0.9），制动距离正常
     * 多云：路面条件良好，摩擦系数略低于晴天（约0.6-0.8）
     * 阴天：路面可能略有湿滑，摩擦系数降低（约0.5-0.7）
     * 雨天：路面湿滑，摩擦系数显著降低（约0.3-0.5），制动距离增加，车辆稳定性下降
     * 雪天：路面非常湿滑，摩擦系数极低（约0.1-0.3），制动距离大幅增加，车辆极易失控
   - 说明天气如何影响轮胎与路面的摩擦系数，进而影响车辆的制动性能、转向稳定性和整体安全性
   - 说明这些参数如何影响最终结果

3. **公式推导与计算**
   - **必须使用前端提供的物理数据进行计算和分析（数据已全部提供）**，即使某些数据为0也要使用并说明原因
   - 详细推导关键物理量的计算公式
   - 展示每一步计算过程，包括：
     * 自然频率：ω_n = √(k/m) = {omega_n:.2f} rad/s （已提供，直接使用）
     * 阻尼比：ζ = c/(2√(km)) = {zeta:.3f} （已提供，直接使用）
     * 最大位移：x_max = (F₀/k) × [1 + exp(-ζω_n t_pass)] = {max_displacement:.4f} m （已提供，直接使用）
     * 最大加速度：a_max = (F₀/m) + (ω_n² × x_max) = {max_acceleration:.2f} m/s² （已提供，直接使用）
     * 弹跳高度：h = max(0, (x_max - H) × 0.5) = {bounce_height:.4f} m （已提供，直接使用）
   - **使用前端提供的具体数值进行计算（已全部提供）**：
     * 最大加速度 = {max_acceleration:.2f} m/s² （已提供）
     * 最大位移 = {max_displacement:.4f} m （已提供）
     * 速度变化 = {velocity_change:.2f} m/s （已提供）
     * 弹跳高度 = {bounce_height:.4f} m （已提供）
     * 通过时间 = {t_pass:.3f} s （已提供）
     * 自然频率 = {omega_n:.2f} rad/s （已提供）
     * 阻尼比 = {zeta:.3f} （已提供）
   - **重要：这些数据已经全部提供，不要再说"没有提供"或"无法计算"。如果数据为0，请说明物理原因（例如：速度太低、车辆参数不合适等），但必须使用这个0值进行分析**
   - 说明每个公式的物理意义

4. **结果验证**
   - **必须使用前端提供的物理数据进行验证（数据已全部提供）**，前端数据如下：
     * 最大加速度：{max_acceleration:.2f} m/s² （已提供）
     * 最大位移：{max_displacement:.4f} m （已提供）
     * 速度变化：{velocity_change:.2f} m/s （已提供）
     * 弹跳高度：{bounce_height:.4f} m ({bounce_height*100:.2f} cm) （已提供）
     * 通过时间：{t_pass:.3f} s （已提供）
     * 自然频率：{omega_n:.2f} rad/s （已提供）
     * 阻尼比：{zeta:.3f} （已提供）
   - **重要：这些数据已经全部提供，不要再说"没有提供"或"无法计算"**
   - 根据上述前端数据，使用物理公式重新计算这些值，并与前端数据进行对比
   - 如果计算值与前端数据一致，说明验证通过；如果有差异，分析差异原因
   - 评估结果的合理性和准确性
   - **注意：即使某些数据为0，也要使用这个0值进行验证并说明原因（例如：速度太低导致没有明显位移等），但不要再说"没有提供"**

5. **物理意义解释**
   - 解释每个物理量的实际意义
   - 说明为什么这个速度/参数组合会导致这样的结果
   - 分析系统的动态响应特性

6. **安全评估**
   - 基于物理计算评估安全性
   - 指出关键风险点
   - 给出物理层面的安全建议

7. **模型局限性**
   - 说明简化模型的局限性
   - 指出哪些因素被忽略（如空气阻力、非线性效应等）
   - 说明在什么情况下模型可能不准确

请用清晰的结构、完整的公式、详细的推导过程来展示你的分析。使用LaTeX格式表示公式（如：$F = ma$），并确保每个步骤都有清晰的说明。
"""
        
        # 调用物理学家角色
        try:
            physicist_personality = get_role_personality('physicist')
            if not physicist_personality:
                raise ValueError("无法获取物理学家角色设定")
            
            messages = [
                {"role": "system", "content": physicist_personality},
                {"role": "user", "content": query}
            ]
            
            # 检查是否请求流式输出
            stream = request.json.get('stream', False)
            
            if stream:
                # 流式输出模式
                def generate():
                    try:
                        response = call_role_api('physicist', messages)
                        if not response or 'choices' not in response or len(response['choices']) == 0:
                            yield f"data: {json.dumps({'error': 'API返回数据格式错误'})}\n\n"
                            return
                        
                        physics_analysis = response['choices'][0]['message']['content']
                        if not physics_analysis:
                            yield f"data: {json.dumps({'error': 'API返回的分析内容为空'})}\n\n"
                            return
                        
                        # 将分析文本分块发送（模拟流式输出）
                        chunk_size = 40  # 每次发送40个字符（减少块大小，让显示更平滑）
                        total_length = len(physics_analysis)
                        sent_length = 0
                        
                        # 发送开始信号
                        yield f"data: {json.dumps({'type': 'start', 'total': total_length})}\n\n"
                        time.sleep(0.5)
                        
                        # 分块发送内容
                        while sent_length < total_length:
                            chunk = physics_analysis[sent_length:sent_length + chunk_size]
                            sent_length += len(chunk)
                            
                            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'progress': min(100, int(sent_length * 100 / total_length))})}\n\n"
                            
                            # 大幅增加延迟，让用户明显看到逐步显示
                            time.sleep(0.3)  # 300ms延迟，让用户明显看到逐步显示的效果
                        
                        # 发送完成信号
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
                
                response_obj = Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Methods': '*'
                    }
                )
                return response_obj
            else:
                # 非流式输出模式（原有逻辑）
                response = call_role_api('physicist', messages)
                if not response or 'choices' not in response or len(response['choices']) == 0:
                    raise ValueError("API返回数据格式错误")
                
                physics_analysis = response['choices'][0]['message']['content']
                if not physics_analysis:
                    raise ValueError("API返回的分析内容为空")
        except Exception as api_error:
            # 如果API调用失败，返回友好的错误信息
            return jsonify({
                'success': False,
                'error': f'物理学家分析API调用失败: {str(api_error)}',
                'traceback': traceback.format_exc()
            }), 500
        
        # 保存分析结果（如果失败不影响返回结果）
        try:
            session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
            conn = sqlite3.connect('simulation_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, 'physicist_detailed', physics_analysis, json.dumps({
                'type': 'physics_analysis',
                'vehicle': vehicle,
                'bump': bump,
                'speed': speed,
                'survival_rate': survival_rate
            })))
            conn.commit()
            conn.close()
        except Exception as db_error:
            # 数据库保存失败不影响API返回，只记录错误
            print(f"警告：保存分析结果到数据库失败: {db_error}")
        
        return jsonify({
            'success': True,
            'analysis': physics_analysis,
            'role': '物理学家',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/design/chart', methods=['POST', 'OPTIONS'])
def design_chart():
    """可视化设计师设计图表 - 基于用户数据和物理学家分析生成美观的D3.js图表代码"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        chart_type = data.get('chart_type')  # 'heatmap', 'impact', 'speed-time'
        if not chart_type:
            return jsonify({
                'success': False,
                'error': '缺少 chart_type 参数'
            }), 400
        
        user_data = data.get('user_data', {})  # 用户选择：vehicle, bump, location, speed
        physics_data = data.get('physics_data', {})  # 物理学家计算结果
        simulation_result = data.get('simulation_result', {})  # 模拟结果
        
        # 根据图表类型确定函数名和容器ID
        chart_type_map = {
            'heatmap': {'func': 'Heatmap', 'container': 'heatmap'},
            'impact': {'func': 'ImpactChart', 'container': 'impact'},
            'speed-time': {'func': 'SpeedTimeChart', 'container': 'speed-time'}
        }
        chart_info = chart_type_map.get(chart_type, {'func': 'Chart', 'container': 'chart'})
        chart_function_name = chart_info['func']
        chart_container_id = chart_info['container']
        
        # 构建设计查询
        query = f"""
请作为精通 D3.js 的可视化设计师，为《飞跃减速带》项目设计一个专业、美观、交互性强的 {chart_type} 图表。

【图表类型】
{chart_type} 图表

【用户选择数据】
- 车辆类型：{user_data.get('vehicle', '未知')}
- 减速带类型：{user_data.get('bump', '未知')}
- 地点：{user_data.get('location', '未知')}
- 速度：{user_data.get('speed', 0)} km/h

【物理学家计算结果】
{json.dumps(physics_data, ensure_ascii=False, indent=2)}

【模拟结果】
{json.dumps(simulation_result, ensure_ascii=False, indent=2)}

【设计要求】
1. 提供完整的、可直接运行的 D3.js v7 代码
2. 代码必须美观、专业、有创意，符合现代数据可视化设计标准
3. 包含丰富的交互功能（鼠标悬停、缩放、筛选等）
4. 使用优雅的颜色方案和动画过渡效果
5. 确保代码可以直接替换前端现有的图表函数
6. 函数名必须是 update{chart_function_name}()
7. 容器ID是 #{chart_container_id}-chart
8. 代码中可以使用以下变量：d3, currentVehicle, currentBump, currentLocation, currentSpeed, simulationResult, calculateSurvivalRate, vehicleParams, speedBumpParams, locationFactors

【输出格式】
请严格按照以下格式返回：

```javascript
// 完整的 D3.js 图表代码
function update{chart_function_name}() {{
    const container = d3.select('#{chart_container_id}-chart');
    container.selectAll('*').remove();
    
    // 你的代码
}}
```

请确保：
- 代码完整、可运行、无错误
- 使用 D3.js v7 语法
- 包含所有必要的样式和交互
- 代码美观、专业、有创意
- 可以直接替换前端现有的图表函数
- 函数名必须是 update{chart_function_name}()

请提供专业、美观、交互性强的图表代码。
"""
        
        # 调用可视化设计师角色
        try:
            designer_personality = get_role_personality('designer')
            if not designer_personality:
                raise ValueError("无法获取可视化设计师角色设定")
            
            messages = [
                {"role": "system", "content": designer_personality},
                {"role": "user", "content": query}
            ]
            
            response = call_role_api('designer', messages)
            if not response or 'choices' not in response or len(response['choices']) == 0:
                raise ValueError("API返回数据格式错误")
            
            design_code = response['choices'][0]['message']['content']
            if not design_code:
                raise ValueError("API返回的图表代码为空")
            
            # 尝试提取代码块
            import re
            code_match = re.search(r'```(?:javascript|js)?\s*\n(.*?)\n```', design_code, re.DOTALL)
            if code_match:
                chart_code = code_match.group(1).strip()
            else:
                # 如果没有代码块，尝试提取函数定义
                func_match = re.search(r'function\s+update\w+.*?\{.*?\}', design_code, re.DOTALL)
                if func_match:
                    chart_code = func_match.group(0)
                else:
                    chart_code = design_code
            
        except Exception as api_error:
            error_traceback = traceback.format_exc()
            print(f"可视化设计师API调用失败: {str(api_error)}")
            print(f"错误详情: {error_traceback}")
            return jsonify({
                'success': False,
                'error': f'可视化设计师API调用失败: {str(api_error)}',
                'traceback': error_traceback
            }), 500
        
        # 保存设计方案
        try:
            session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
            conn = sqlite3.connect('simulation_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO role_analyses (session_id, role_name, analysis_text, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, 'designer_chart', design_code, json.dumps({
                'type': 'chart_design',
                'chart_type': chart_type,
                'user_data': user_data,
                'physics_data': physics_data
            })))
            conn.commit()
            conn.close()
        except Exception as db_error:
            print(f"警告：保存设计方案到数据库失败: {db_error}")
        
        return jsonify({
            'success': True,
            'chart_code': chart_code,
            'full_response': design_code,
            'chart_type': chart_type,
            'role': '可视化设计师',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"设计图表API错误: {str(e)}")
        print(f"错误详情: {error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500

# ========== 个性化功能 API ==========

@app.route('/api/profile/<session_id>', methods=['GET', 'OPTIONS'])
def get_user_profile(session_id):
    """获取用户画像"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '个性化功能未启用'}), 503
    
    try:
        profile_manager = get_profile_manager()
        profile = profile_manager.get_user_profile(session_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'message': '用户画像不存在，请先进行分析'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': profile
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/profile/analyze', methods=['POST', 'OPTIONS'])
def analyze_user_profile():
    """分析用户画像"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '个性化功能未启用'}), 503
    
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': '缺少session_id'}), 400
        
        profile_manager = get_profile_manager()
        profile = profile_manager.analyze_user_profile(session_id)
        
        return jsonify({
            'success': True,
            'profile': profile
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ========== 社交功能 API ==========

@app.route('/api/comments', methods=['POST', 'OPTIONS'])
def add_comment():
    """添加评论"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        data = request.json
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'anonymous')
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not session_id or not content:
            return jsonify({'error': '缺少必需参数'}), 400
        
        social_manager = get_social_manager()
        comment = social_manager.add_comment(session_id, user_id, content, parent_id)
        
        return jsonify({
            'success': True,
            'comment': comment
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/comments/<session_id>', methods=['GET', 'OPTIONS'])
def get_comments(session_id):
    """获取评论列表"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        limit = int(request.args.get('limit', 50))
        social_manager = get_social_manager()
        comments = social_manager.get_comments(session_id, limit=limit)
        
        return jsonify({
            'success': True,
            'comments': comments,
            'count': len(comments)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/comments/<int:comment_id>/like', methods=['POST', 'OPTIONS'])
def like_comment(comment_id):
    """点赞评论"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        social_manager = get_social_manager()
        success = social_manager.like_comment(comment_id)
        
        return jsonify({
            'success': success,
            'message': '点赞成功' if success else '点赞失败'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/share', methods=['POST', 'OPTIONS'])
def create_share():
    """创建分享"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        data = request.json
        session_id = data.get('session_id')
        share_type = data.get('share_type', 'report')
        share_data = data.get('share_data', {})
        
        if not session_id:
            return jsonify({'error': '缺少session_id'}), 400
        
        social_manager = get_social_manager()
        share = social_manager.create_share(session_id, share_type, share_data)
        
        return jsonify({
            'success': True,
            'share': share
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/share/<share_code>', methods=['GET', 'OPTIONS'])
def get_share(share_code):
    """获取分享内容"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        social_manager = get_social_manager()
        share = social_manager.get_share(share_code)
        
        if not share:
            return jsonify({
                'success': False,
                'error': '分享不存在或已过期'
            }), 404
        
        return jsonify({
            'success': True,
            'share': share
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/collaborate', methods=['POST', 'OPTIONS'])
def create_collaboration():
    """创建协作学习记录"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        data = request.json
        session_id = data.get('session_id')
        collaborator_id = data.get('collaborator_id', 'anonymous')
        collaboration_type = data.get('collaboration_type', 'discussion')
        content = data.get('content', '')
        
        if not session_id:
            return jsonify({'error': '缺少session_id'}), 400
        
        social_manager = get_social_manager()
        collaboration = social_manager.create_collaboration(
            session_id, collaborator_id, collaboration_type, content
        )
        
        return jsonify({
            'success': True,
            'collaboration': collaboration
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/collaborate/<session_id>', methods=['GET', 'OPTIONS'])
def get_collaborations(session_id):
    """获取协作学习记录"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        social_manager = get_social_manager()
        collaborations = social_manager.get_collaborations(session_id)
        
        return jsonify({
            'success': True,
            'collaborations': collaborations,
            'count': len(collaborations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/collaborate/compare', methods=['POST', 'OPTIONS'])
def compare_sessions():
    """比较两个会话的结果"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response, 200
    
    if not NEW_FEATURES_ENABLED:
        return jsonify({'error': '社交功能未启用'}), 503
    
    try:
        data = request.json
        session_id1 = data.get('session_id1')
        session_id2 = data.get('session_id2')
        
        if not session_id1 or not session_id2:
            return jsonify({'error': '缺少session_id1或session_id2'}), 400
        
        social_manager = get_social_manager()
        comparison = social_manager.compare_sessions(session_id1, session_id2)
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# 初始化数据库
init_db()

if __name__ == '__main__':
    print("=" * 50)
    print("飞跃减速带实验系统 - 后端服务器")
    print("=" * 50)
    print("服务器启动在: http://localhost:5001")
    print("API文档:")
    print("  POST /api/analyze - 分析用户选择")
    print("  POST /api/chat - 与角色对话")
    print("  POST /api/simulation/advanced - 高级物理模拟")
    print("  POST /api/report/generate - 生成报告")
    print("  GET  /api/statistics - 获取统计数据")
    print("  GET  /api/history/<session_id> - 获取会话历史")
    print("  POST /api/recommend - 智能参数推荐")
    print("  POST /api/risk/assess - 实时风险评估")
    print("  POST /api/learning/path - 个性化学习路径")
    print("  POST /api/report/title - 智能报告标题生成")
    print("  POST /api/debate - 多角色辩论生成（增强版）")
    print("  POST /api/questions/generate - 智能问题生成")
    print("  GET  /api/profile/<session_id> - 获取用户画像")
    print("  POST /api/profile/analyze - 分析用户画像")
    print("  POST /api/comments - 添加评论")
    print("  GET  /api/comments/<session_id> - 获取评论列表")
    print("  POST /api/comments/<comment_id>/like - 点赞评论")
    print("  POST /api/share - 创建分享")
    print("  GET  /api/share/<share_code> - 获取分享内容")
    print("  POST /api/collaborate - 创建协作学习记录")
    print("  GET  /api/collaborate/<session_id> - 获取协作记录")
    print("  POST /api/collaborate/compare - 比较两个会话")
    print("  POST /api/physics/calculate - 物理学家计算模拟结果")
    print("  POST /api/physics/analyze - 物理学家公式分析（支持流式输出）")
    print("  POST /api/design/chart - 可视化设计师设计图表")
    print("  POST /api/charts/data - 获取图表数据（支持缓存）")
    print("  POST /api/charts/batch-analysis - 批量分析图表数据点")
    print("  POST /api/charts/export - 导出图表数据（CSV/JSON）")
    print("=" * 50)
    app.run(debug=True, port=5001, host='0.0.0.0', threaded=True)
