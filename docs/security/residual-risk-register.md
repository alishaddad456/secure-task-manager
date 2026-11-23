# Residual security risk register

This register records the policy findings and intentional design trade-offs observed in GitHub Actions CI run [#117](https://github.com/alishaddad456/secure-task-manager/actions/runs/45266257703) on 2026-11-23.

## Scan result and interpretation

Checkov reported **128 passed, 20 failed, and 0 skipped**. The workflow uses `--soft-fail`, so the Terraform security job completed successfully despite these findings. This is a transparent record of accepted or outstanding risks, not a claim that all policy checks pass.

## Findings

| Checkov ID | Affected area | Current condition / reason | Recommended next action | Status |
|---|---|---|---|---|
| CKV_AWS_2, CKV_AWS_103, CKV2_AWS_20 | ALB listener | Public demo endpoint is HTTP-only; no ACM certificate/custom domain is configured | Attach a validated ACM certificate, enable HTTPS listener, redirect HTTP to HTTPS | Open — priority |
| CKV2_AWS_28 | ALB | No AWS WAF web ACL association | Evaluate AWS WAF managed rules and recurring cost; associate a web ACL | Open |
| CKV_AWS_136 | ECR | Repository uses AES-256 encryption rather than KMS CMK | Consider KMS only with a migration plan; changing encryption can require repository replacement | Accepted trade-off |
| CKV_AWS_118 | RDS | Enhanced Monitoring is disabled | Enable if deeper OS-level DB monitoring is needed and cost is acceptable | Accepted cost trade-off |
| CKV_AWS_157 | RDS | Multi-AZ is disabled | Enable for production availability after cost and failover testing | Accepted cost trade-off |
| CKV_AWS_161 | RDS | IAM database authentication is disabled; app uses Secrets Manager credentials | Evaluate IAM auth and update application connection flow before enabling | Open |
| CKV_AWS_353 | RDS | Performance Insights is disabled | Evaluate current Performance Insights/Database Insights pricing and retention | Accepted cost trade-off |
| CKV_AWS_333 | ECS | Fargate tasks receive public IPs in public subnets to avoid NAT Gateway cost; inbound app traffic is restricted to ALB security group | Move tasks to private subnets and add NAT or VPC endpoints | Accepted network trade-off |
| CKV2_AWS_69 | RDS | Checkov did not verify encryption in transit | Verify PostgreSQL SSL enforcement and configure the RDS parameter group/client policy to require TLS | Open — verify |
| CKV2_AWS_57 | Secrets Manager | Automatic secret rotation is not configured | Implement and test a rotation function and application credential refresh before enabling | Open |
| CKV_AWS_144 | ALB log S3 bucket | Cross-region replication is not configured | Add only if off-region log resilience is a requirement; account for storage/transfer cost | Accepted scope trade-off |
| CKV2_AWS_61 | ALB log S3 bucket | Lifecycle configuration is absent | Add lifecycle expiration/transition rules that match the audit-retention requirement | Open |
| CKV2_AWS_62 | ALB log S3 bucket | Event notifications are not configured | Add notifications only if a downstream log-processing workflow is required | Accepted scope trade-off |
| CKV_AWS_18 | ALB log S3 bucket | Server access logging is not configured | Add a separate destination bucket if bucket-level access audit is required; avoid recursive logging | Open |
| CKV_AWS_145 | ALB log S3 bucket | Bucket default encryption uses AES-256 rather than KMS | Evaluate CMK requirements and update without disrupting existing ALB log delivery | Accepted trade-off |
| CKV_AWS_21 | ALB log S3 bucket | Versioning is not enabled | Enable if recovery from accidental overwrite/deletion is required; account for retained object cost | Open |
| CKV_AWS_338 | VPC Flow Logs CloudWatch group | Retention is 7 days, below the policy's one-year threshold | Set retention based on compliance/audit needs and budget | Accepted cost trade-off |
| CKV_AWS_378 | ALB target group | ALB-to-task target traffic uses HTTP inside the VPC | Evaluate end-to-end TLS/mTLS requirements; document the trusted VPC boundary if retaining HTTP | Open |
| CKV_AWS_260 | ALB security group | Port 80 is open to the internet for the HTTP demo listener | Close HTTP ingress after HTTPS is configured; keep only required HTTPS ingress | Open |

## Prioritization

### Address before handling real users or sensitive data

1. Configure a domain and ACM certificate; serve HTTPS and redirect HTTP to HTTPS.
2. Verify RDS TLS enforcement end-to-end (server parameter group and client `sslmode`).
3. Decide whether the public ALB needs AWS WAF protection.
4. Review public-subnet task placement against the intended threat model; prefer private subnets for production.

### Address when the service's operational requirements justify it

- Secret rotation with a tested application credential refresh path.
- S3 log bucket versioning, lifecycle, and optional access logging.
- Longer VPC Flow Logs retention.
- Multi-AZ RDS, Enhanced Monitoring, Performance Insights, and cross-region log replication.

### Explicitly accepted portfolio trade-offs

- Single-AZ RDS and disabled optional DB monitoring keep the demonstration cost-conscious.
- ECR and ALB-log S3 use AES-256 encryption; KMS migration must be planned to avoid replacing a live ECR repository.
- Event notifications and cross-region replication are not required by the current application workflow.

## Review discipline

Re-run Checkov after each infrastructure change, review the Terraform plan before applying, and update this register with the new run ID, finding count, rationale, owner, and remediation status. Do not suppress findings merely to obtain a green CI badge.
