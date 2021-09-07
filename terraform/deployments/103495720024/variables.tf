variable "ENVIRONMENT" {
    default = "test"
}

variable "GITHUB_ORG" {
    default = "alphagov"
}

variable "GITHUB_TOKEN" {
    default = "/github/usage/pat"
}

variable "LOG_LEVEL" {
    default = "DEBUG"
}

variable "usage_cron_schedule" {
    default     = ""
}

variable "audit_cron_schedule" {
    default     = ""
}