locals {
  tags = {
    Service       = "github-usage"
    Environment   = "prod"
    SvcOwner      = "Cyber"
    DeployedUsing = "Terraform_v12"
    SvcCodeURL    = "https://github.com/alphagov/cyber-security-github-usage"
  }

}
