variable "ENVIRONMENT" {
    default = "prod"
}

variable "GITHUB_ORG" {
    default = "alphagov"
}

variable "GITHUB_TOKEN" {
    default = "/github/usage/pat"
}

variable "usage_cron_schedule" {
    description = "Run usage at 7am every day"
    default     = "cron(0 7 ? * MON-FRI *)"
}

variable "audit_cron_schedule" {
    description = "Run membership audit at 2am every day"
    default     = "cron(0 2 ? * MON-FRI *)"
}