module "log_subscription" {
  source = "git::ssh://git@github.com/alphagov/cyber-security-terraform//modules/csls_cloudwatch_log_group_subscription?ref=d4e012260bb8d8a42ccdc6dbc1691eeaf8933a99"
  log_groups = {
    "/aws/lambda/github_usage_lambda": "INFO"
  }
}
