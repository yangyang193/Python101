#!/bin/bash

# 修复SSL证书问题和安装依赖

echo "=========================================="
echo "修复SSL证书和安装依赖"
echo "=========================================="

# 方法1: 使用--trusted-host跳过SSL验证（临时方案）
echo "方法1: 使用--trusted-host安装..."
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 安装成功！"
    exit 0
fi

# 方法2: 安装证书（Mac系统）
echo ""
echo "方法2: 尝试安装SSL证书..."
echo "正在运行Python证书安装脚本..."

python3 << 'EOF'
import ssl
import os
import subprocess
import sys

# 尝试安装证书
try:
    import certifi
    print("✅ certifi已安装")
except ImportError:
    print("正在安装certifi...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", "certifi"])
    import certifi

# 设置SSL证书路径
cert_path = certifi.where()
print(f"证书路径: {cert_path}")

# 设置环境变量
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['REQUESTS_CA_BUNDLE'] = cert_path

print("✅ SSL证书已配置")
EOF

# 再次尝试安装
echo ""
echo "使用配置的证书重新安装..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 安装成功！"
else
    echo "❌ 安装失败，请手动运行："
    echo "pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt"
    exit 1
fi

