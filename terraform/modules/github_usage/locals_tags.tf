locals {
  tags = {
    Service       = "github-usage"
    Environment   = var.ENVIRONMENT
    SvcOwner      = "Cyber"
    DeployedUsing = "Terraform"
    SvcCodeURL    = "https://github.com/alphagov/cyber-security-github-usage"
  }
}
