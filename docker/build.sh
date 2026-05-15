#!/bin/bash

set -e

echo "Building FriendDebate Docker image..."

docker build -t friend-debate:latest -f docker/Dockerfile .

echo "Build completed!"
echo ""
echo "To run FriendDebate:"
echo "  docker run -p 3000:3000 -v \$(pwd)/data:/app/data friend-debate:latest"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose -f docker/docker-compose.yml up -d"
