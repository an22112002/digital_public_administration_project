#!/bin/bash
# Quick Docker debugging script

echo "=========================================="
echo "HUB Docker Debug Information"
echo "=========================================="
echo ""

echo "1. Docker Services Status:"
echo "---"
docker-compose ps
echo ""

echo "2. Backend Logs (last 50 lines):"
echo "---"
docker logs HUB-backend --tail=50 2>/dev/null || echo "Backend container not found"
echo ""

echo "3. MySQL Logs (last 20 lines):"
echo "---"
docker logs HUB-mysql-db --tail=20 2>/dev/null || echo "MySQL container not found"
echo ""

echo "4. Redis Logs (last 20 lines):"
echo "---"
docker logs HUB-redis-db --tail=20 2>/dev/null || echo "Redis container not found"
echo ""

echo "5. Network Status:"
echo "---"
docker network inspect hub-network 2>/dev/null | grep -A 20 "Containers" || echo "Network not found"
echo ""

echo "6. Backend Health Check:"
echo "---"
curl -s http://localhost:8000/health || echo "Backend not responding"
echo ""

echo "7. Backend Ping:"
echo "---"
curl -s http://localhost:8000/ping || echo "Backend ping failed"
echo ""

echo "=========================================="
