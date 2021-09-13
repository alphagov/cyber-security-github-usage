module "codebuild-apply-teraform-staging" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_apply_terraform"
  codebuild_service_role_name = var.codebuild_service_role_name
  deployment_account_id       = var.staging_account_id
  deployment_role_name        = "CodePipelineDeployerRole_${var.staging_account_id}"
  terraform_directory         = "terraform/deployments/${var.staging_account_id}"
  codebuild_image             = var.codebuild_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "TerraformApplyStaging"
  action_name                 = "TerraformApply"
  environment                 = var.environment
  docker_hub_credentials      = var.docker_hub_credentials
  tags                        = local.tags
  copy_artifacts              = [
    { 
      artifact = "ssh_config", 
      source = ".ssh", 
      target = "/root/.ssh"
    }, 
    { 
      artifact = "lambda_zip", 
      source = "github_usage_lambda.zip", 
      target = "lambda"
    }
  ]
}
