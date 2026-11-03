# Secure Task Manager API

A portfolio project demonstrating secure API development and a practical AWS DevSecOps delivery workflow.

> **Project status:** Application and baseline CI are implemented. AWS infrastructure and deployment are being built on the `aws-infrastructure` branch. No AWS resources are created by this repository automatically.

## Project goals

This project is designed to demonstrate skills expected in junior Cloud / DevSecOps roles:

- Build and test a Python REST API with FastAPI and SQLAlchemy.
- Package the application as a non-root Docker container.
- Run automated tests and security checks in GitHub Actions.
- Provision AWS infrastructure as code with Terraform.
- Publish container images to Amazon ECR and deploy to Amazon ECS Fargate.
- Use Amazon RDS for PostgreSQL, AWS Secrets Manager for database credentials, and CloudWatch for logs and monitoring.

## Architecture target

The planned AWS deployment uses:

- **Amazon ECR** — private container image registry.
- **Amazon ECS on Fargate** — managed container runtime.
- **Application Load Balancer** — HTTPS entry point and traffic routing.
- **Amazon RDS for PostgreSQL** — persistent application data.
- **AWS Secrets Manager** — database credentials injected at runtime.
- **Amazon CloudWatch** — application logs, metrics, and alarms.
- **Terraform** — repeatable infrastructure provisioning.
- **GitHub Actions + GitHub OIDC** — CI/CD without long-lived AWS access keys.

See [docs/architecture.md](docs/architecture.md) for the design and security decisions. This is a target design; components will be marked complete only after they are implemented and verified.

## Run locally

Requirements: Python 3.13+, pip, and (optionally) Docker.

```bash
git clone https://github.com/alishaddad456/secure-task-manager.git
cd secure-task-manager

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements-dev.txt

cp .env.example .env
uvicorn app.main:app --reload
```

The local default uses SQLite. The API is available at:

- Health: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs
- Tasks: http://127.0.0.1:8000/tasks/

## Run tests and security checks

```bash
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=85
bandit -r app -ll
pip-audit -r requirements.txt
```

Build and run the container:

```bash
docker build -t secure-task-manager:local .
docker run --rm -p 8000:8000 secure-task-manager:local
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health check |
| GET | `/tasks/` | List tasks (paginated) |
| GET | `/tasks/{task_id}` | Retrieve a task |
| POST | `/tasks/` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Security controls

Current baseline:

- Request validation with Pydantic.
- Parameterized database access through SQLAlchemy.
- Non-root Docker runtime user.
- Automated test coverage gate.
- Bandit static analysis.
- Dependency vulnerability auditing with pip-audit.
- GitHub Actions workflow with read-only repository permissions by default.

Planned AWS controls:

- Least-privilege IAM task and deployment roles.
- GitHub OIDC federation instead of stored AWS access keys.
- Private database subnets and security-group-restricted database access.
- Secrets Manager for database credentials.
- Encrypted storage and TLS at the application entry point.
- Terraform security scanning and deployment review gates.

## Repository layout

```text
app/                  FastAPI application, database, models, schemas, routes
tests/                Automated API tests
.github/workflows/    CI/CD workflows
docs/                 Architecture and operational documentation
terraform/            AWS infrastructure as code (being implemented)
Dockerfile            Container image definition
compose.yaml          Local container workflow
```

## Cost and safety

Terraform creates billable cloud resources only when an operator explicitly runs `terraform apply`. Review the plan, region, estimated costs, and AWS account before applying. Do not commit credentials, Terraform state, or generated secret values.

## Portfolio evidence

Before presenting this as a completed AWS deployment, attach evidence of successful CI runs, Terraform validation/security scans, a deployed endpoint, container image publication, and operational logs. The project documentation will distinguish implemented, tested, and planned components honestly.
