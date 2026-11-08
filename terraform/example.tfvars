# Copy to terraform.tfvars and adjust only after reviewing regional pricing.
aws_region       = "eu-west-1"
project_name     = "secure-task-manager"
environment      = "portfolio"
github_repository = "alishaddad456/secure-task-manager"
github_branch     = "phase-3-integration"

# Set this to an ACM certificate ARN in the same region to enable HTTPS.
# Without it, the demo listener is HTTP and must not be used for sensitive production traffic.
acm_certificate_arn = null
