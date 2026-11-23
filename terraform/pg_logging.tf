# --------------------------------------------------
# POSTGRESQL QUERY LOGGING (RDS hardening)
# --------------------------------------------------
# Slow-query logging: statements taking longer than 1 second. The postgresql
# log stream is already exported to CloudWatch by enabled_cloudwatch_logs_exports
# on the DB instance, so these entries land in /ecs-adjacent log group automatically.
# For full statement logging instead, add: log_statement = "all".

resource "aws_db_parameter_group" "app" {
  name   = "${local.name}-pg-query-logging"
  family = "postgres18"

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "log_lock_waits"
    value = "1"
  }

  tags = {
    Name = "${local.name}-pg-query-logging"
  }
}
