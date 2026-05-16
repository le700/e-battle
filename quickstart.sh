#!/bin/bash

set -e

echo "================================"
echo "e-battle - AI好友辩论 Battle"
echo "================================"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "   访问 https://docs.docker.com/get-docker/"
    exit 1
fi

echo "📦 创建目录..."
mkdir -p data/chatlogs data/avatars data/debates data/shares data/wechat_decrypted models
touch data/chatlogs/.gitkeep data/avatars/.gitkeep data/debates/.gitkeep data/shares/.gitkeep
echo "✅ 完成"

echo ""
echo "🐳 构建 Docker 镜像..."
docker build -t le700/friend-battle:latest -f docker/Dockerfile .
echo "✅ 构建完成"

echo ""
echo "🚀 启动 e-battle..."
docker run -d \
  --name friend-battle \
  -p 3000:3000 \
  -v "$(pwd)/data:/app/data" \
  le700/friend-battle:latest

echo ""
echo "================================"
echo "🎉 e-battle 已启动！"
echo "================================"
echo ""
echo "📍 访问：http://localhost:3000"
echo ""
echo "🛑 停止服务：docker stop friend-battle"
echo "🔄 重启服务：docker restart friend-battle"
echo "❌ 删除容器：docker rm friend-battle"
echo ""
