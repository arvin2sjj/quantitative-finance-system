#!/bin/bash

# 上传到GitHub的脚本
# 使用方法: ./upload_to_github.sh <your-github-username>

if [ $# -eq 0 ]; then
    echo "使用方法: $0 <your-github-username>"
    echo "例如: $0 yourusername"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="quantitative-finance-system"

echo "🚀 准备上传到GitHub..."
echo "仓库名称: $REPO_NAME"
echo "GitHub用户名: $GITHUB_USERNAME"

# 添加远程仓库
echo "📡 添加远程仓库..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# 推送代码到GitHub
echo "⬆️  推送代码到GitHub..."
git branch -M main
git push -u origin main

echo "✅ 上传完成！"
echo "🌐 您的仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
