#!/bin/bash

# 飞跃减速带实验系统 - 服务器启动脚本

echo "=========================================="
echo "飞跃减速带实验系统 - 后端服务器"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 项目目录: $SCRIPT_DIR"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 检查依赖是否安装
echo "📦 检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask未安装，正在安装依赖..."
    pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

echo ""

# 检查端口是否被占用
echo "🔍 检查端口5001..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  端口5001已被占用"
    echo "   正在尝试关闭占用端口的进程..."
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    sleep 2
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "❌ 无法关闭占用端口的进程，请手动关闭"
        echo "   运行: lsof -i :5001 查看占用进程"
        exit 1
    else
        echo "✅ 端口已释放"
    fi
else
    echo "✅ 端口5001可用"
fi

echo ""
echo "=========================================="
echo "🚀 启动服务器..."
echo "=========================================="
echo "📍 服务器地址: http://localhost:5001"
echo "📍 前端页面: http://localhost:5001/"
echo "📍 API健康检查: http://localhost:5001/api/health"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

# 启动服务器
python3 app.py

