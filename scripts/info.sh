#!/bin/bash

echo "FriendDebate - AI好友辩论系统"
echo "=============================="
echo ""

cd "$(dirname "$0")"

echo "使用方法:"
echo "  bash quickstart.sh          # 快速开始"
echo "  bash scripts/demo.sh        # 运行演示"
echo "  python src/web/app.py        # 直接运行 Web 应用"
echo ""

echo "项目结构:"
tree -L 2 -I '__pycache__|*.pyc' || find . -maxdepth 2 -type f -name "*.py" | head -20

echo ""
echo "更多帮助请查看 README.md"
