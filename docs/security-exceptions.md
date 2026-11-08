# Security scan exceptions

The Terraform CI job runs Checkov as a blocking gate. The following controls are explicitly deferred for this cost-conscious portfolio environment and are not represented as production-ready controls.

| Check | Exception | Rationale / boundary |
|---|---|---|
| CKV_AWS_333 | Fargate tasks receive public IPs | Avoids a NAT Gateway's recurring charge. The task security group allows inbound traffic only from the ALB security group. RDS is private. |
| CKV_AWS_157 | RDS is single-AZ | Multi-AZ materially increases database cost. Use Multi-AZ for production or business-critical workloads. |
| CKV_AWS_2, CKV_AWS_103, CKV2_AWS_20 | HTTP listener fallback | An ACM certificate is optional for the demo. When configured, port 80 redirects to HTTPS and the HTTPS listener enforces TLS 1.2+. Without a certificate, do not send sensitive traffic. |
| CKV_AWS_378 | ALB-to-task target group uses HTTP | Traffic is within the VPC and is restricted by security groups. Production deployments requiring end-to-end encryption should configure TLS between the ALB and application. |
| CKV2_AWS_28 | No AWS WAF on the ALB | WAF adds recurring cost and is deferred for the learning environment. Add managed WAF rules before exposing a production workload. |
| CKV_AWS_18 | No server-access logging on the ALB log bucket | This bucket stores ALB access logs; logging the log bucket to another bucket creates a second storage/retention system for a disposable demo. Revisit for production audit retention. |
| CKV_AWS_144 | No cross-region replication for ALB logs | The portfolio environment is single-region and the log bucket is not a disaster-recovery archive. Enable replication for regulated or production workloads. |
| CKV_AWS_145 | ALB log bucket uses SSE-S3 rather than SSE-KMS | ALB access-log delivery requires the supported S3-managed encryption configuration; the bucket is private and public access is blocked. |
| CKV2_AWS_62 | No S3 event notifications on the ALB log bucket | There is no downstream event consumer in this project. Notifications would add an unused service integration. |
| CKV_AWS_300 | Checkov false positive for multipart-upload abort | The `aws_s3_bucket_lifecycle_configuration.alb_logs` rule explicitly aborts incomplete multipart uploads after 7 days. The inline skip is scoped to this resource; retain the lifecycle block and recheck when upgrading Checkov. |

All other Checkov findings remain blocking and must be fixed. Revisit these exceptions before any production use.
