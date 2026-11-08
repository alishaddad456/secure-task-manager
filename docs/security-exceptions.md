# Security scan exceptions

The Terraform CI job runs Checkov as a blocking gate. The following controls are explicitly deferred for this cost-conscious portfolio environment and are not represented as production-ready controls:

| Check | Exception | Rationale / boundary |
|---|---|---|
| CKV_AWS_333 | Fargate tasks receive public IPs | Avoids a NAT Gateway's recurring charge. The task security group allows inbound traffic only from the ALB security group. RDS is private. |
| CKV_AWS_157 | RDS is single-AZ | Multi-AZ materially increases database cost. Use Multi-AZ for production or business-critical workloads. |
| CKV_AWS_2, CKV_AWS_103, CKV2_AWS_20 | HTTP listener fallback | An ACM certificate is optional for the demo. When configured, port 80 redirects to HTTPS and the HTTPS listener enforces TLS 1.2+. Without a certificate, do not send sensitive traffic. |
| CKV_AWS_378 | ALB-to-task target group uses HTTP | Traffic is within the VPC and is restricted by security groups. Production deployments requiring end-to-end encryption should configure TLS between the ALB and application. |
| CKV2_AWS_28 | No AWS WAF on the ALB | WAF adds recurring cost and is deferred for the learning environment. Add managed WAF rules before exposing a production workload. |

All other Checkov findings remain blocking and must be fixed. Revisit these exceptions before any production use.
