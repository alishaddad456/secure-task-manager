# Residual Risk Register

| ID | Risk | Severity | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R-01 | HTTP instead of HTTPS | Medium | Traffic is not encrypted in transit | Configure ACM and HTTPS | Open |
| R-02 | Secret rotation not configured | Medium | Long-lived credentials | Implement tested rotation | Open |
| R-03 | Remaining Checkov findings | Review required | Depends on individual findings | Remediate or justify | Open |
| R-04 | ALB access logging | Review required | Reduced request audit visibility | Configure S3 access logs | Open |

| CKV_AWS_18 / CKV2_AWS_39 | ALB serves HTTP only | No domain available for ACM cert | Fix: supply acm_certificate_arn (listener code already supports it) |
