"""
MCP 时间服务集成模块
提供时间和时区转换功能
"""

import subprocess
import json
from datetime import datetime
import pytz

def get_current_time(timezone=None):
    """
    获取特定时区或系统时区的当前时间
    
    Args:
        timezone (str): IANA时区名称（例如：'Asia/Shanghai', 'America/New_York'）
                       如果为None，使用系统时区
    
    Returns:
        dict: 包含时区、日期时间和是否夏令时的信息
    """
    try:
        # 如果指定了时区，使用该时区
        if timezone:
            tz = pytz.timezone(timezone)
        else:
            # 使用系统时区
            tz = pytz.timezone('Asia/Shanghai')  # 默认使用中国时区
        
        now = datetime.now(tz)
        
        # 检查是否在夏令时
        is_dst = bool(now.dst())
        
        return {
            'timezone': str(tz),
            'datetime': now.isoformat(),
            'is_dst': is_dst,
            'formatted': now.strftime('%Y-%m-%d %H:%M:%S %Z')
        }
    except Exception as e:
        return {
            'error': str(e),
            'timezone': timezone or 'system',
            'datetime': datetime.now().isoformat()
        }

def convert_time(source_timezone, time_str, target_timezone):
    """
    在时区之间转换时间
    
    Args:
        source_timezone (str): 源IANA时区名称
        time_str (str): 24小时格式的时间（HH:MM）或完整日期时间
        target_timezone (str): 目标IANA时区名称
    
    Returns:
        dict: 包含源时区、目标时区、转换后的时间和时差的信息
    """
    try:
        source_tz = pytz.timezone(source_timezone)
        target_tz = pytz.timezone(target_timezone)
        
        # 解析时间字符串
        if ':' in time_str and len(time_str) <= 5:
            # 只有时间（HH:MM），使用今天的日期
            hour, minute = map(int, time_str.split(':'))
            today = datetime.now(source_tz).date()
            source_dt = source_tz.localize(datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)))
        else:
            # 完整的日期时间字符串
            source_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            if source_dt.tzinfo is None:
                source_dt = source_tz.localize(source_dt)
            else:
                source_dt = source_dt.astimezone(source_tz)
        
        # 转换到目标时区
        target_dt = source_dt.astimezone(target_tz)
        
        # 计算时差
        source_offset = source_dt.utcoffset().total_seconds() / 3600
        target_offset = target_dt.utcoffset().total_seconds() / 3600
        time_difference = target_offset - source_offset
        
        return {
            'source': {
                'timezone': source_timezone,
                'datetime': source_dt.isoformat(),
                'is_dst': bool(source_dt.dst()),
                'formatted': source_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            },
            'target': {
                'timezone': target_timezone,
                'datetime': target_dt.isoformat(),
                'is_dst': bool(target_dt.dst()),
                'formatted': target_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            },
            'time_difference': f"{'+' if time_difference >= 0 else ''}{time_difference:.1f}h"
        }
    except Exception as e:
        return {
            'error': str(e),
            'source_timezone': source_timezone,
            'target_timezone': target_timezone,
            'time': time_str
        }

def get_available_timezones():
    """
    获取常用的时区列表
    
    Returns:
        list: 常用时区列表
    """
    return [
        {'name': 'Asia/Shanghai', 'label': '中国标准时间 (CST)'},
        {'name': 'Asia/Tokyo', 'label': '日本标准时间 (JST)'},
        {'name': 'America/New_York', 'label': '美国东部时间 (EST/EDT)'},
        {'name': 'America/Los_Angeles', 'label': '美国西部时间 (PST/PDT)'},
        {'name': 'Europe/London', 'label': '英国时间 (GMT/BST)'},
        {'name': 'Europe/Paris', 'label': '中欧时间 (CET/CEST)'},
        {'name': 'Australia/Sydney', 'label': '澳大利亚东部时间 (AEST/AEDT)'},
        {'name': 'UTC', 'label': '协调世界时 (UTC)'}
    ]

