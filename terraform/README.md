# AWS infrastructure

Terraform provisions a portfolio environment containing:

- VPC with two explicitly selected public application/ALB subnets and two private database subnets.
- Internet Gateway, public routing, VPC Flow Logs, and a locked-down default security group.
- Security groups with ALB-to-ECS, ECS-to-RDS, and HTTPS-only AWS API egress rules.
- Public Application Load Balancer with invalid-header dropping, deletion protection, access logs, and a health-checked target group.
- Private S3 ALB log bucket with public-access blocking, encryption, versioning, and 90-day lifecycle expiration.
- Customer-managed KMS key for ECR and CloudWatch log encryption.
- ECR repository with immutable tags, image scanning on push, and lifecycle cleanup.
- ECS Fargate cluster, service, task definition, task/execution roles, and CloudWatch log group.
- Private, encrypted, single-AZ RDS PostgreSQL instance with IAM database authentication, forced TLS, PostgreSQL query logging, Performance Insights, and enhanced monitoring.
- RDS-managed master password in Secrets Manager (not generated into Terraform state).
- Encrypted CloudWatch log groups, ECS Container Insights, ECS CPU/memory alarms, ALB 5xx alarm, RDS CPU alarm, and an operations dashboard.
- GitHub Actions OIDC provider and branch-restricted deployment role.

## Network and cost trade-off

To avoid a NAT Gateway's recurring cost, the initial learning environment runs Fargate tasks in public subnets with public IP assignment. Their security group accepts inbound application traffic only from the ALB security group; tasks are not open to unsolicited internet ingress. RDS is in private subnets and accepts PostgreSQL only from the application security group.

For a stricter production topology, move tasks to private subnets and add VPC endpoints or NAT egress as required. This has additional cost and is intentionally not provisioned by this starter configuration.

## Before applying

1. Install Terraform >= 1.6 and configure AWS CLI credentials locally.
2. Review AWS pricing for the selected region. An ALB, Fargate tasks, RDS, ECR storage, Secrets Manager, and CloudWatch can incur charges.
3. Copy `example.tfvars` to `terraform.tfvars`; do not commit personal values.
4. Run `terraform init`, `terraform fmt -check -recursive`, `terraform validate`, and `terraform plan`.
5. Review every resource and cost before running `terraform apply`.

RDS manages the database master password in Secrets Manager, so Terraform does not generate the password value. Terraform state still contains sensitive infrastructure metadata. Protect state with encryption and restricted access, and never commit state files. Configure a protected remote state backend before using this as a team environment.

The optional ACM certificate enables HTTPS. Without one, the ALB exposes HTTP for a disposable demonstration only; do not send sensitive data over that endpoint. The explicit Checkov exceptions and their production boundaries are listed in `docs/security-exceptions.md`.

## GitHub Actions deployment configuration

After Terraform has been applied, add these **repository-level Actions variables** under Settings → Secrets and variables → Actions → Variables:

| Variable | Value |
|---|---|
| `AWS_REGION` | Terraform `aws_region` output |
| `AWS_DEPLOY_ROLE_ARN` | Terraform `github_deploy_role_arn` output |
| `ECR_REPOSITORY` | ECR repository name, e.g. `secure-task-manager-portfolio` |
| `ECS_CLUSTER` | Terraform `ecs_cluster_name` output |
| `ECS_SERVICE` | Terraform `ecs_service_name` output |
| `ECS_TASK_FAMILY` | Terraform `ecs_task_definition_family` output |
| `ECS_CONTAINER_NAME` | Terraform `ecs_container_name` output |
| `ECS_SUBNET_IDS` | Two Terraform `ecs_public_subnet_ids` values, comma-separated |
| `ECS_SECURITY_GROUP_ID` | Terraform `ecs_security_group_id` output |
| `APP_BASE_URL` | Terraform `application_url` output |

The workflow uses GitHub OIDC and does not require stored AWS access keys. Its IAM trust policy permits only the configured repository and `phase-3-integration` branch. The workflow builds an immutable commit-tagged image, runs Alembic migrations as a one-off Fargate task, updates ECS, waits for service stability, and checks `/ready`.

## Bootstrap sequence

The initial ECS task definition references a placeholder `bootstrap` image. The ECS service defaults to `desired_count = 0`, so Terraform can create infrastructure without launching a task from a nonexistent image. After infrastructure creation and adding the repository-level Actions variables, run the deployment workflow; it builds and pushes a real image, registers a new task definition, and scales the service to one task.

## Cost and teardown

This is not a zero-cost deployment. ALB, RDS, the customer-managed KMS key, Performance Insights, enhanced monitoring, CloudWatch retention, and log storage may accrue charges while idle. Review current regional prices before applying. Destroy temporary resources with `terraform destroy` when finished; review RDS deletion and snapshot settings first.
