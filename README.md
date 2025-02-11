# CI/CD Pipeline

Full CI/CD pipeline: parallel tests → Docker build+push → SSH deploy to EC2 with health-check verification → Slack notification.

[![CI/CD](https://github.com/yadavar333/ci-cd-pipeline/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yadavar333/ci-cd-pipeline/actions/workflows/ci-cd.yml)

## Services

| Service | Language | Port | Description |
|---------|----------|------|-------------|
| service-a | Python / Flask | 5000 | User management API |
| service-b | Node.js / Express | 4000 | Posts API |

## Stack
GitHub Actions · Docker · Docker Hub · AWS EC2 · pytest · Jest · Bash

## Pipeline Architecture

```
Push to main
     │
     ▼
┌────────────────────────────────────┐
│         Test (parallel)            │
│  ┌─────────────┐ ┌──────────────┐  │
│  │  pytest ×5  │ │  Jest  ×5   │  │
│  │  service-a  │ │  service-b  │  │
│  └─────────────┘ └──────────────┘  │
└────────────────────────────────────┘
     │ both pass
     ▼
┌────────────────────────────────────┐
│         Build & Push               │
│  docker build service-a            │
│  docker push → :sha + :latest      │
│  docker build service-b            │
│  docker push → :sha + :latest      │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│         Deploy (SSH → EC2)         │
│  appleboy/ssh-action               │
│  bash ~/deploy.sh                  │
│  health-check retry (10× / 5s)     │
│  auto-rollback on failure          │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│      Slack Notification            │
│  ✅ success  /  ❌ failure          │
└────────────────────────────────────┘
```

## Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token |
| `EC2_HOST` | EC2 public IP or hostname |
| `EC2_USER` | SSH user (e.g. `ec2-user`) |
| `EC2_SSH_KEY` | Private SSH key (PEM) |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL |

## Local Development

```bash
# Run both services with Docker Compose
docker compose up --build

# service-a: http://localhost:5000/health
# service-b: http://localhost:4000/health
```

## Running Tests Locally

```bash
# service-a
cd services/service-a
pip install -r requirements.txt
pytest tests/ -v

# service-b
cd services/service-b
npm install
npm test
```

## Rollback

To roll back to a previous deployment, SSH into EC2 and run:

```bash
export DOCKER_USERNAME=your_dockerhub_username
export IMAGE_TAG=<previous-git-sha>   # e.g. a1b2c3d
bash ~/deploy.sh
```

The `deploy.sh` script always pulls the specified tag, stops the running containers, starts fresh ones, and verifies health before completing. If health checks fail it automatically stops the new containers.
