module "log_subscription" {
  source = "git::ssh://git@github.com/alphagov/cyber-security-terraform//modules/csls_cloudwatch_log_group_subscription?ref=c1636d1"
  log_groups = {
    "/aws/lambda/github_usage_lambda": "INFO"
  }
  environment = var.ENVIRONMENT
}