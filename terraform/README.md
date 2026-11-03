# AWS infrastructure

Terraform provisions the portfolio environment:

- VPC with two public application/ALB subnets and two private database subnets.
- Internet Gateway and public routing.
- Security groups: internet to ALB; ALB to ECS; ECS to PostgreSQL only.
- Application Load Balancer and health-checked target group.
- ECR repository with immutable tags, image scanning on push, and lifecycle cleanup.
- ECS Fargate cluster, service, task definition, task/execution roles, and CloudWatch log group.
- Private, encrypted, single-AZ RDS PostgreSQL instance.
- Secrets Manager database password.
- GitHub Actions OIDC provider and branch-restricted deployment role.

## Important network trade-off

To avoid a NAT Gateway's recurring cost, the initial learning environment runs Fargate tasks in public subnets with public IP assignment. Their security group accepts inbound application traffic only from the ALB security group; the tasks are not open to unsolicited internet ingress. The RDS database is in private subnets and accepts PostgreSQL only from the application security group.

For a stricter production topology, move tasks to private subnets and add VPC endpoints or NAT egress as required. This has additional cost and is intentionally not provisioned by this starter configuration.

## Before applying

1. Install Terraform >= 1.6 and configure AWS CLI credentials locally.
2. Review AWS pricing for the selected region. An ALB, Fargate tasks, RDS, ECR storage, Secrets Manager, and CloudWatch can incur charges.
3. Copy `example.tfvars` to `terraform.tfvars`; do not commit personal values.
4. Run `terraform init`, `terraform fmt -check -recursive`, `terraform validate`, and `terraform plan`.
5. Review every resource and cost before running `terraform apply`.

Terraform state contains the generated database password and other infrastructure metadata. Protect state as a secret, use encrypted storage with restricted access, and never commit it. For a team environment, configure a protected remote state backend before applying.

The optional ACM certificate enables HTTPS. Without one, the ALB exposes HTTP for a disposable demonstration only; do not send sensitive data over that endpoint.

## Bootstrap note

ECS initially references an image tag named `bootstrap`. The first deployment workflow builds and pushes the initial image before replacing the task definition image with the commit-specific immutable tag. Run the first deployment after Terraform has created the infrastructure. If the initial service cannot start before the first image push, deploy the first image and then force a new ECS deployment.

Destroy temporary resources with `terraform destroy` when finished. Check RDS deletion and snapshot settings before doing so.
