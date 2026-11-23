# --------------------------------------------------
# RDS ENHANCED MONITORING ROLE (closes the monitoring finding)
# --------------------------------------------------
# The Enhanced Monitoring agent pushes OS-level metrics to CloudWatch every
# monitoring_interval seconds; it assumes this role to publish them.

resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "${local.name}-rds-enhanced-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
