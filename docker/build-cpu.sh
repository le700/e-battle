#!/bin/bash

set -e

echo "Building FriendDebate CPU image..."

docker build -t friend-debate:cpu -f docker/Dockerfile.cpu .

echo "Build completed!"
echo ""
echo "To run FriendDebate (CPU version):"
echo "  docker run -p 3000:3000 -v \$(pwd)/data:/app/data friend-debate:cpu"
