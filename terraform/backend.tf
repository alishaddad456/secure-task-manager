terraform {
  backend "s3" {
    bucket         = "secure-task-manager-tfstate-040331609263-a38f564f"
    key            = "secure-task-manager/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "secure-task-manager-terraform-locks"
  }
}
