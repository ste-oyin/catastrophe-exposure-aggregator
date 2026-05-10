# Catastrophe Exposure Aggregator — Infrastructure

AWS CDK (Python) infrastructure for the Catastrophe Exposure Aggregator application.

## Architecture

```
                    ┌─────────────────────────────┐
                    │        CloudFront            │
                    │   (CDN + SPA routing)        │
                    └──────┬───────────┬──────────┘
                           │           │
                  /static  │           │  /api/*
                           ▼           ▼
                    ┌────────┐   ┌───────────┐
                    │   S3   │   │    ALB     │
                    │ Bucket │   │  (public)  │
                    └────────┘   └─────┬─────┘
                                       │
                              ┌────────▼────────┐
                              │  ECS Fargate     │
                              │  (FastAPI)       │
                              └───┬─────────┬───┘
                                  │         │
                         ┌────────▼──┐  ┌───▼──────────┐
                         │  Aurora    │  │ ElastiCache  │
                         │ Serverless│  │   (Redis)    │
                         │  (PG 16)  │  │              │
                         └───────────┘  └──────────────┘
```

## Stacks

| Stack | Resources |
|---|---|
| `CatExposure-Networking` | VPC, subnets (public / private / isolated), NAT Gateway, security groups |
| `CatExposure-Database` | Aurora Serverless v2 (PostgreSQL 16.6), encrypted, auto-scaling 0.5–4 ACU |
| `CatExposure-Cache` | ElastiCache Redis 7.1 (cache.t4g.micro), encrypted at rest + in transit |
| `CatExposure-Backend` | ECR repo, ECS Fargate service (0.5 vCPU / 1 GB), ALB, auto-scaling 1–6 tasks |
| `CatExposure-Frontend` | S3 bucket (OAC), CloudFront distribution with `/api/*` pass-through to ALB |

## Prerequisites

- Python 3.11+
- Node.js 20+ (for the CDK CLI)
- AWS CDK CLI: `npm install -g aws-cdk`
- AWS credentials configured

## Getting Started

```bash
cd infrastructure

# Create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Synthesize CloudFormation templates
cdk synth

# View a diff against currently deployed stacks
cdk diff

# Deploy all stacks
cdk deploy --all
```

## CI/CD

GitHub Actions workflows live in `.github/workflows/`:

- **deploy-infrastructure.yml** — runs `cdk diff` on PRs and `cdk deploy --all` on pushes to `main` that touch `infrastructure/`.
- **deploy-backend.yml** — builds the FastAPI Docker image, pushes to ECR, and rolls out a new ECS deployment on pushes to `main` that touch `backend/`.

Both workflows authenticate via OIDC (`aws-actions/configure-aws-credentials`) using the `AWS_DEPLOY_ROLE_ARN` secret.

## Configuration

Key environment variables expected by the Fargate task:

| Variable | Source |
|---|---|
| `DB_SECRET` / `DB_SECRET_ARN` | Aurora cluster secret (auto-injected via Secrets Manager) |
| `REDIS_HOST` | ElastiCache primary endpoint |
| `REDIS_PORT` | ElastiCache port (6379) |
