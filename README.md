# Catastrophe Exposure Aggregator

Aggregate and analyse catastrophe exposure data across portfolios. Full-stack application with a FastAPI backend, React frontend, backed by Aurora PostgreSQL and ElastiCache Redis on AWS.

## Architecture

```
Browser → CloudFront → S3 (React SPA)
                     → /api/* → ALB → ECS Fargate (FastAPI :8000) → ElastiCache Redis
                                                                  → Aurora PostgreSQL
```

| Layer          | Stack                      | Directory         |
| -------------- | -------------------------- | ----------------- |
| Frontend       | React, Vite, Tailwind, shadcn/ui | `frontend/`  |
| Backend        | FastAPI, Redis, SQLAlchemy  | `backend/`        |
| Infrastructure | AWS CDK (Python)            | `infrastructure/` |

## Prerequisites

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- AWS CLI + CDK CLI (for infrastructure)
- Docker (for backend container builds)

## Getting Started

### Backend

```bash
cd backend
uv sync
cp .env .env.local  # adjust values as needed
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set `PYTHONPATH=src` if your editor needs it for imports.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies `/api/*` to `http://localhost:8000`.

### Running Tests

```bash
# Backend
cd backend && uv run pytest

# Frontend unit tests
cd frontend && npm test

# Frontend E2E tests (requires dev server or will start one)
cd frontend && npm run test:e2e
```

## Environment Variables

### Backend (runtime)

| Variable        | Description                          | Default     |
| --------------- | ------------------------------------ | ----------- |
| `REDIS_HOST`    | ElastiCache Redis hostname           | `localhost` |
| `REDIS_PORT`    | Redis port                           | `6379`      |
| `REDIS_SSL`     | Use TLS for Redis connection         | `true`      |
| `DB_SECRET_ARN` | AWS Secrets Manager ARN for Aurora   | —           |
| `DEBUG`         | Enable debug mode                    | `false`     |

### Frontend (build-time)

| Variable             | Description              | Default |
| -------------------- | ------------------------ | ------- |
| `VITE_API_BASE_URL`  | API base URL for fetch   | `/api`  |

### GitHub Actions Secrets

| Secret                       | Description                                          |
| ---------------------------- | ---------------------------------------------------- |
| `AWS_DEPLOY_ROLE_ARN`        | OIDC role ARN for AWS authentication                 |
| `FRONTEND_BUCKET_NAME`       | S3 bucket from `CatExposure-Frontend` stack output   |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID from stack output         |

## CI/CD

| Workflow                 | Trigger                  | Action                                  |
| ------------------------ | ------------------------ | --------------------------------------- |
| `deploy-backend.yml`     | Push to `main` (backend) | Docker build → ECR → ECS redeploy      |
| `deploy-frontend.yml`    | Push to `main` (frontend)| npm build → S3 sync → CloudFront invalidation |
| `deploy-infrastructure.yml` | Push/PR to `main` (infra) | CDK diff (PR) / CDK deploy (push)    |
