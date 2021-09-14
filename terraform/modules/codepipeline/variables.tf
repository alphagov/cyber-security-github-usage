variable "codestar_connection_id" {
  type = string
}

variable "codebuild_service_role_name" {
  description = "the role code build uses to access other AWS services"
  type        = string
}

variable "docker_hub_credentials" {
  description = "Name of the secret in SSM that stores the Docker Hub credentials"
  type        = string
}

variable "environment" {
  type    = string
  default = "test"
}

variable "pipeline_name" {
  type    = string
  default = "github-usage"
}

variable "codebuild_image" {
  type    = string
  default = "gdscyber/cyber-security-cd-base-image:latest"
}

variable "staging_account_id" {
  type    = string
  default = "103495720024"
}

variable "prod_account_id" {
  type    = string
  default = "779799343306"
}

variable "deploy_key" {
  type  = string
}