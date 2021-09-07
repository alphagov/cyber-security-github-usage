locals {
  tags = {
    Service       = "github-usage"
    Environment   = "prod"
    SvcOwner      = "Cyber"
    DeployedUsing = "Terraform_v12"
    SvcCodeURL    = "https://github.com/alphagov/cyber-security-github-usage"
  }

#   docker_hub_username = jsondecode(data.aws_secretsmanager_secret_version.dockerhub_creds.secret_string)["username"]
#   docker_hub_password = jsondecode(data.aws_secretsmanager_secret_version.dockerhub_creds.secret_string)["password"]
}
