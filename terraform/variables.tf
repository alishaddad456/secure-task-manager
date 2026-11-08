variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Short project identifier used in resource names."
  type        = string
  default     = "secure-task-manager"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "portfolio"
}

variable "container_port" {
  description = "Port exposed by the FastAPI container."
  type        = number
  default     = 8000
}

variable "db_name" {
  description = "PostgreSQL database name."
  type        = string
  default     = "taskmanager"
}

variable "db_username" {
  description = "PostgreSQL application username."
  type        = string
  default     = "taskmanager"
}

variable "db_instance_class" {
  description = "RDS instance class. Check regional pricing and free-tier eligibility before applying."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Initial RDS storage in GiB."
  type        = number
  default     = 20
}

variable "app_cpu" {
  description = "Fargate task CPU units."
  type        = number
  default     = 256
}

variable "app_memory" {
  description = "Fargate task memory in MiB."
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of ECS tasks."
  type        = number
  default     = 1
}

variable "github_repository" {
  description = "GitHub repository allowed to assume the deployment role, in owner/repo format."
  type        = string
  default     = "alishaddad456/secure-task-manager"
}

variable "github_branch" {
  description = "Only this Git ref may assume the GitHub deployment role."
  type        = string
  default     = "phase-3-integration"
}

variable "acm_certificate_arn" {
  description = "Optional ACM certificate ARN. Supply a validated certificate to enable HTTPS; otherwise the demo listener uses HTTP."
  type        = string
  default     = null
  nullable    = true
}
