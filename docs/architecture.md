# Architecture and engineering decisions

## Objective

Deliver a production-oriented learning deployment for a small FastAPI service while keeping the local developer workflow inexpensive and simple.

## Target request flow

1. A client sends HTTPS traffic to an Application Load Balancer.
2. The load balancer forwards requests to healthy ECS Fargate tasks.
3. The API reads and writes task records in Amazon RDS for PostgreSQL.
4. ECS sends container logs to CloudWatch Logs.
5. GitHub Actions tests and scans changes, builds the Docker image, publishes it to ECR, and deploys a new ECS task definition through GitHub OIDC.

## Selected services

| Concern | Choice | Reason |
|---|---|---|
| Compute | ECS Fargate | Demonstrates containers, task definitions, IAM roles, health checks, and deployment operations without managing EC2 hosts. |
| Registry | ECR | Native private registry for ECS images. |
| Database | RDS PostgreSQL | Persistent managed database; container filesystems are ephemeral. |
| Entry point | Application Load Balancer | Health-based routing and HTTPS termination. |
| Secrets | Secrets Manager | Keep database credentials out of source code and image layers. |
| Observability | CloudWatch Logs and metrics | Centralized runtime troubleshooting. |
| IaC | Terraform | Reproducible, reviewable infrastructure changes. |
| CI/CD identity | GitHub OIDC | Short-lived AWS role sessions instead of long-lived access keys. |

## Network and cost trade-off

The preferred production design places the database in private subnets and restricts its security group to the application tasks. The load balancer is public; application tasks should not accept unsolicited public ingress.

A NAT Gateway can create significant recurring cost. The initial portfolio deployment should evaluate a no-NAT design (for example, tasks with public IPs in public subnets but ingress restricted to the load balancer security group) against a more isolated private-subnet design with VPC endpoints/NAT. The chosen topology must be explicit in Terraform and documented; do not silently trade away network controls.

## Database strategy

- SQLite remains the default for local development and automated tests.
- AWS runtime uses PostgreSQL through the `DATABASE_URL` environment variable.
- The application already uses SQLAlchemy and selects SQLite-specific connection options only for SQLite URLs.
- A PostgreSQL driver and versioned schema migrations will be added before production deployment.
- Database schema changes should be performed by a controlled migration step, not by every application replica running `create_all` at startup.

## Security principles

- No credentials in Git, Docker build arguments, or committed Terraform variable files.
- GitHub Actions receives AWS access through a narrowly scoped OIDC role.
- ECS task execution role and application task role are separate.
- The task role receives only permissions required by the running application.
- Database access is limited by security groups; RDS is not publicly accessible.
- Encrypt data at rest and use TLS for external traffic and database connections.
- Pin and review third-party GitHub Actions; use minimal workflow permissions.
- Run tests, dependency auditing, static analysis, container scanning, and Terraform scanning before deployment.

## Deployment lifecycle

1. Pull request: tests, coverage gate, static analysis, dependency audit, Docker build, and Terraform validation/scanning.
2. Merge to the deployment branch: build and tag an immutable image with the commit SHA.
3. Authenticate to AWS with GitHub OIDC.
4. Push the image to ECR.
5. Register a new ECS task definition revision and update the ECS service.
6. Wait for service stability and verify the health endpoint.
7. Preserve the previous task definition revision for rollback.

## Cost guardrails

Infrastructure is not deployed automatically by CI. Terraform plan is reviewable before apply. Avoid NAT Gateways and always-on resources unless the expected learning value justifies their cost. Use the smallest practical database and compute sizes, set log retention, and destroy temporary environments when finished.
