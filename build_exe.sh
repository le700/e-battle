#!/bin/bash

set -e

echo "================================"
echo "FriendBattle - 打包脚本"
echo "================================"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "📦 步骤 1: 检查环境..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

if ! pip3 list | grep -q pyinstaller; then
    echo "📦 安装 PyInstaller..."
    pip3 install pyinstaller
fi

echo "✅ 环境检查完成"

echo ""
echo "📦 步骤 2: 创建必要目录..."
mkdir -p assets build dist
touch assets/.gitkeep

echo "✅ 目录创建完成"

echo ""
echo "📦 步骤 3: 打包为 EXE..."

# 使用 PyInstaller 打包
pyinstaller pyinstaller.spec --clean

echo ""
echo "✅ 打包完成！"
echo ""
echo "📁 输出位置: $PROJECT_DIR/dist/FriendBattle.exe"
echo ""
echo "💡 使用方法:"
echo "  1. 运行 dist/FriendBattle.exe"
echo "  2. 访问 http://localhost:3000"
echo "  3. 开始你的 FriendBattle！"
echo ""
echo "🛠️ 构建完整安装包 (可选):"
echo "  NSIS 或 Inno Setup 可以创建安装程序"
echo ""
