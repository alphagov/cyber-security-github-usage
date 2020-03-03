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