# AWS infrastructure

Terraform provisions a portfolio environment containing:

- VPC with two public application/ALB subnets and two private database subnets.
- Internet Gateway and public routing.
- Security groups: internet to ALB; ALB to ECS; ECS to PostgreSQL only.
- Application Load Balancer and health-checked target group.
- ECR repository with immutable tags, image scanning on push, and lifecycle cleanup.
- ECS Fargate cluster, service, task definition, task/execution roles, and CloudWatch log group.
- Private, encrypted, single-AZ RDS PostgreSQL instance.
- Secrets Manager database password.
- CloudWatch log group, ECS CPU/memory alarms, ALB 5xx alarm, RDS CPU alarm, and an operations dashboard.
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

Terraform state contains the generated database password and infrastructure metadata. Protect state as a secret, use encrypted storage with restricted access, and never commit it. Configure a protected remote state backend before using this as a team environment.

The optional ACM certificate enables HTTPS. Without one, the ALB exposes HTTP for a disposable demonstration only; do not send sensitive data over that endpoint.

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

The workflow uses GitHub OIDC and does not require stored AWS access keys. Its IAM trust policy permits only the configured repository branch. The workflow builds an immutable commit-tagged image, runs Alembic migrations as a one-off Fargate task, updates ECS, waits for service stability, and checks `/ready`.

## Bootstrap sequence

The initial ECS task definition references a placeholder `bootstrap` image. Terraform creates the registry and service, but the service cannot become healthy until a real image is pushed. Run the deployment workflow after infrastructure creation and after adding the GitHub Environment variables.

## Cost and teardown

This is not a zero-cost deployment. ALB and RDS may accrue charges while idle. Review current regional prices before applying. Destroy temporary resources with `terraform destroy` when finished; review RDS deletion and snapshot settings first.
