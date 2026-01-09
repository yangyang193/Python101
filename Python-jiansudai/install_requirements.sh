#!/bin/bash

# 安装依赖（跳过SSL验证）

echo "正在安装Python依赖..."
echo "使用--trusted-host跳过SSL验证..."

pip3 install --trusted-host pypi.org \
             --trusted-host pypi.python.org \
             --trusted-host files.pythonhosted.org \
             -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖安装成功！"
    echo ""
    echo "现在可以启动服务器："
    echo "  python3 app.py"
    echo "或者："
    echo "  ./start.sh"
else
    echo ""
    echo "❌ 安装失败"
    exit 1
fi

