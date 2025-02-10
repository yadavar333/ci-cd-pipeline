#!/bin/bash
set -euo pipefail

IMAGE_A="${DOCKER_USERNAME}/service-a:${IMAGE_TAG:-latest}"
IMAGE_B="${DOCKER_USERNAME}/service-b:${IMAGE_TAG:-latest}"

echo "==> Pulling images"
docker pull "$IMAGE_A"
docker pull "$IMAGE_B"

echo "==> Stopping old containers (if running)"
docker stop service-a service-b 2>/dev/null || true
docker rm   service-a service-b 2>/dev/null || true

echo "==> Starting new containers"
docker run -d --name service-a --restart unless-stopped -p 5000:5000 "$IMAGE_A"
docker run -d --name service-b --restart unless-stopped -p 4000:4000 "$IMAGE_B"

echo "==> Health check (retry up to 10 times)"
for service in "service-a:5000" "service-b:4000"; do
  name="${service%%:*}"
  port="${service##*:}"
  for i in $(seq 1 10); do
    if curl -sf "http://localhost:${port}/health" > /dev/null; then
      echo "  ✓ ${name} is healthy"
      break
    fi
    if [ "$i" -eq 10 ]; then
      echo "  ✗ ${name} failed health check after 10 attempts — rolling back"
      docker stop service-a service-b 2>/dev/null || true
      docker rm   service-a service-b 2>/dev/null || true
      exit 1
    fi
    echo "  waiting for ${name}... (${i}/10)"
    sleep 5
  done
done

echo "==> Deployment complete"
docker ps --filter "name=service-a" --filter "name=service-b" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
