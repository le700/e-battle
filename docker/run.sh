#!/bin/bash

set -e

echo "Pulling latest FriendDebate image..."
docker pull friend-debate:latest

echo "Stopping existing containers..."
docker-compose -f docker/docker-compose.yml down

echo "Starting FriendDebate..."
docker-compose -f docker/docker-compose.yml up -d

echo ""
echo "FriendDebate is running!"
echo "  Web UI: http://localhost:3000"
echo "  API: http://localhost:8000"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker/docker-compose.yml logs -f"
