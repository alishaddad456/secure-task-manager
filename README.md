# Secure Task Manager — AWS DevSecOps Portfolio

A containerized FastAPI task-management API deployed to AWS with Terraform, GitHub Actions CI/CD, and layered security checks. This repository demonstrates application engineering, infrastructure as code, cloud operations, and a repeatable software delivery pipeline.

## Live deployment

- **Application:** http://secure-task-manager-portfolio-al-867587441.eu-north-1.elb.amazonaws.com
- **Health:** append `/health`
- **Readiness:** append `/ready`
- **API documentation:** append `/docs`
- **CI pipeline:** [GitHub Actions](https://github.com/alishaddad456/secure-task-manager/actions)
- **Latest verified CI run:** [Run #117 — successful](https://github.com/alishaddad456/secure-task-manager/actions/runs/45266257703)

> **Transport security notice:** The current demo endpoint is HTTP because no ACM certificate/custom domain is configured. Do not send real credentials or sensitive information to this demo endpoint. Terraform supports HTTPS when a validated ACM certificate ARN is supplied.

## What this project demonstrates

- FastAPI REST API with task CRUD, Pydantic validation, SQLAlchemy, and PostgreSQL.
- Alembic database migrations and SQLite support for local development.
- Non-root Docker image, health check, and runtime smoke test.
- AWS VPC, public Application Load Balancer, ECS Fargate, ECR, and private RDS PostgreSQL provisioned with Terraform.
- GitHub Actions authentication to AWS using OIDC instead of long-lived AWS access keys.
- Secrets Manager, KMS encryption, scoped IAM roles, CloudWatch logging/alarms/dashboard, VPC Flow Logs, and ALB access logs.
- CI checks for tests/coverage, Bandit, pip-audit, Docker build/runtime, Trivy, Terraform formatting/validation, and Checkov.

## Architecture

See [Architecture and data flow](docs/architecture.md) for the Mermaid diagram, network boundaries, request flow, and design trade-offs.

At a glance: clients reach the public ALB; the ALB forwards to ECS Fargate tasks whose inbound security-group rule allows traffic only from the ALB security group. Tasks access PostgreSQL in private subnets. Secrets are retrieved from Secrets Manager through the ECS execution role. GitHub Actions assumes a branch-restricted AWS role through OIDC and deploys immutable commit-tagged images from ECR.

## Application API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe including database connectivity |
| GET | `/tasks/` | List tasks (paginated) |
| GET | `/tasks/{task_id}` | Retrieve one task |
| POST | `/tasks/` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

Interactive OpenAPI documentation is available at `/docs`.

## Run locally

Requirements: Python 3.13+, pip.

```bash
git clone https://github.com/alishaddad456/secure-task-manager.git
cd secure-task-manager

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt

cp .env.example .env
set -a && source .env && set +a
alembic upgrade head
uvicorn app.main:app --reload
```

The default local configuration uses SQLite. Open http://127.0.0.1:8000/docs.

Or use Docker Compose:

```bash
docker compose up --build
```

## Quality and security checks

Run locally:

```bash
python -m pytest -v --cov=app --cov-report=term-missing --cov-fail-under=85
bandit -r app -ll
pip-audit -r requirements.txt
docker build -t secure-task-manager:local .
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
```

### Latest verified results

The latest CI run for commit `cd33adb` completed successfully:

| Check | Result |
|---|---|
| GitHub Actions jobs | 2 of 2 passed |
| Tests | 22 passed |
| Test coverage | 94.37% (85% minimum) |
| Bandit | No issues identified |
| pip-audit | No known vulnerabilities |
| Docker build and runtime smoke test | Passed |
| Trivy | Passed configured CRITICAL / ignore-unfixed gate |
| Terraform fmt and validate | Passed |
| Checkov | 128 passed, 20 failed findings reported |

**Important:** Checkov runs with `--soft-fail`; therefore the workflow can pass while findings remain. The 20 findings from run #117 are documented with context and remediation guidance in the [residual-risk register](docs/security/residual-risk-register.md). A successful CI status is not a claim that every Checkov policy passes.

## AWS infrastructure and deployment

Terraform provisions the AWS environment. Review [terraform/README.md](terraform/README.md) before changing or creating resources. The deployment workflow is manually dispatched and:

1. Authenticates to AWS through GitHub OIDC.
2. Builds and pushes an immutable image tagged with the commit SHA to ECR.
3. Registers a new ECS task definition.
4. Runs Alembic migrations as a one-off Fargate task.
5. Updates the ECS service and waits for stability.
6. Verifies the application readiness endpoint.

Required GitHub Actions variables and the bootstrap sequence are documented in [terraform/README.md](terraform/README.md).

## Security posture and known limitations

- RDS is private, encrypted at rest, protected from accidental deletion, and configured with a one-day backup retention period.
- Database ingress is restricted to the application security group.
- ECS task and execution roles are separate; GitHub deployment uses OIDC with a branch-restricted trust relationship.
- The ALB has deletion protection, drops invalid headers, and sends access logs to a private S3 bucket.
- VPC Flow Logs capture all traffic; application and VPC logs are sent to CloudWatch.
- The current demo is HTTP-only; use ACM and HTTPS before handling sensitive traffic.
- The deployment is a cost-conscious portfolio environment, not a high-availability production reference: RDS is single-AZ and ECS tasks use public subnets with inbound access restricted to the ALB security group.
- Remaining Checkov findings and accepted trade-offs are listed in the residual-risk register.

## Repository layout

```text
app/                         FastAPI application and task routes
tests/                       Automated tests
migrations/                  Alembic schema migrations
.github/workflows/           CI and manual AWS deployment workflows
docs/architecture.md         System architecture and Mermaid diagram
docs/security/               Security architecture and residual-risk register
terraform/                   AWS infrastructure as code
Dockerfile                   Non-root application image
compose.yaml                 Local container workflow
requirements*.txt            Runtime and development dependencies
```

## Cost and safety

This deployment incurs AWS costs (including ALB, Fargate, RDS, logs, ECR storage, and Secrets Manager). Review current regional pricing and every Terraform plan before applying changes. Do not commit credentials, `.env` files, personal `terraform.tfvars`, or Terraform state. Destroy temporary resources when no longer needed, after reviewing database snapshot and deletion-protection settings.
