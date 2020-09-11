variable "ENVIRONMENT" {
  type    = string
  default = "Test"
}

variable "GITHUB_ORG" {
  description = "Shortname of GitHub organisation"
  type        = string
}

variable "GITHUB_TOKEN" {
  description = "SSM path for a personal access token with read:user and read:org permissions"
  type        = string
}

variable "LOG_LEVEL" {
  description = "Set the lambda log level"
  type        = string
  default     = "INFO"
}

variable "usage_cron_schedule" {
  description = "Report usage to splunk on a regular basis"
  type        = string
  default     = ""
}

variable "audit_cron_schedule" {
  description = "Report membership audit to splunk on a regular basis"
  type        = string
  default     = ""
}