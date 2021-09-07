module github_usage {
  source               = "../../modules/github_usage"
  ENVIRONMENT          = var.ENVIRONMENT
  GITHUB_ORG           = var.GITHUB_ORG
  GITHUB_TOKEN         = var.GITHUB_TOKEN
  usage_cron_schedule  = var.usage_cron_schedule
  audit_cron_schedule  = var.audit_cron_schedule
}