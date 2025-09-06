#!/bin/bash

# 量化金融系统启动脚本

echo "=== 量化金融系统 ==="
echo "正在启动系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到配置文件 .env"
    echo "请复制 config.env.example 为 .env 并配置数据库信息"
    echo "cp config.env.example .env"
    exit 1
fi

# 初始化数据库
echo "初始化数据库..."
python main.py --init

if [ $? -eq 0 ]; then
    echo "数据库初始化成功"
else
    echo "数据库初始化失败，请检查配置"
    exit 1
fi

# 启动调度器
echo "启动定时调度器..."
echo "按 Ctrl+C 停止系统"
python main.py --scheduler
