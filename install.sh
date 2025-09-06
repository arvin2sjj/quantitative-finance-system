#!/bin/bash

# 量化金融系统安装脚本

echo "=== 量化金融系统安装脚本 ==="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖包安装成功"
else
    echo "❌ 依赖包安装失败"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "创建配置文件..."
    cp config.env.example .env
    echo "✅ 配置文件已创建，请编辑 .env 文件配置数据库信息"
else
    echo "✅ 配置文件已存在"
fi

echo ""
echo "=== 安装完成 ==="
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件配置数据库信息"
echo "2. 创建MySQL数据库: CREATE DATABASE quantitative_finance;"
echo "3. 初始化数据库: python main.py --init"
echo "4. 测试系统: python test_system.py"
echo "5. 启动系统: python main.py --scheduler"
echo ""
echo "或使用启动脚本: ./start.sh"
