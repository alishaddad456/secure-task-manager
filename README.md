# Secure Task Manager API

A portfolio project demonstrating secure API development and a practical AWS DevSecOps delivery workflow.

## Project goals

- Python REST API development with FastAPI and SQLAlchemy.
- PostgreSQL support with versioned Alembic migrations; SQLite remains available locally.
- Non-root Docker containerization and runtime health checks.
- Automated tests, coverage enforcement, static analysis, dependency auditing, and container scanning.
- AWS infrastructure as code with Terraform.
- Amazon ECR and Amazon ECS Fargate deployment.
- Amazon RDS for PostgreSQL, Secrets Manager, IAM least privilege, and GitHub OIDC.
- CloudWatch logging and health-based deployment verification.

## AWS architecture

The target environment provisions a public Application Load Balancer, ECS Fargate tasks in public subnets with inbound access restricted to the ALB security group, and a private RDS PostgreSQL database. This initial design avoids a NAT Gateway to reduce recurring costs. Review [docs/architecture.md](docs/architecture.md) and [terraform/README.md](terraform/README.md) for trade-offs and setup instructions.

## Run locally

Requirements: Python 3.13+, pip.

```bash
git clone https://github.com/alishaddad456/secure-task-manager.git
cd secure-task-manager

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements-dev.txt

cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

The local default uses SQLite. API endpoints:

- Health: http://127.0.0.1:8000/health
- Readiness (includes database connectivity): http://127.0.0.1:8000/ready
- Interactive API docs: http://127.0.0.1:8000/docs
- Tasks: http://127.0.0.1:8000/tasks/

Run with Docker Compose:

```bash
docker compose up --build
```

## Tests and security checks

```bash
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=85
bandit -r app -ll
pip-audit -r requirements.txt
```

GitHub Actions additionally runs Trivy container scanning and Terraform validation/Checkov scanning.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/ready` | Database readiness check |
| GET | `/tasks/` | List tasks (paginated) |
| GET | `/tasks/{task_id}` | Retrieve a task |
| POST | `/tasks/` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## CI/CD workflow

The CI workflow runs tests, coverage enforcement, Bandit, pip-audit, Docker build/runtime smoke tests, Trivy image scanning, Terraform formatting/validation, and Checkov scanning.

The AWS deployment workflow uses GitHub OIDC (no long-lived AWS access keys), pushes an immutable commit-tagged image to ECR, runs Alembic migrations as a one-off ECS task, updates the ECS service, waits for stability, and checks the readiness endpoint. See [terraform/README.md](terraform/README.md) for required GitHub Environment variables.

## Security controls

- Pydantic request validation and SQLAlchemy parameterized queries.
- Non-root container user and read-only container root filesystem.
- Separate liveness and database readiness endpoints.
- PostgreSQL TLS required by the application connection.
- RDS private subnets and security-group-limited database ingress.
- Secrets Manager for the database password.
- Separate ECS task and execution roles.
- GitHub OIDC trust restricted to this repository and deployment branch.
- CI test, dependency, static-analysis, image, and IaC scanning.

## Cost and safety

Terraform creates billable resources only when an operator explicitly runs `terraform apply`. An ALB, Fargate, RDS, logs, and secrets can incur recurring charges. Review the plan and current regional pricing before applying. Do not commit credentials or Terraform state. No live AWS deployment is claimed until it has been performed and verified.

## Repository structure

```text
app/                  FastAPI application
tests/                Automated API and database configuration tests
migrations/           Alembic schema migrations
.github/workflows/    CI and AWS deployment workflows
docs/                 Architecture documentation
terraform/            AWS infrastructure as code
Dockerfile            Non-root application image
compose.yaml          Local container workflow
```
