module "codebuild-validate-terraform-prod" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_validate_terraform"
  codebuild_service_role_name = var.codebuild_service_role_name
  deployment_account_id       = var.prod_account_id
  deployment_role_name        = "CodePipelineDeployerRole_${var.prod_account_id}"
  terraform_directory         = "terraform/deployments/${var.prod_account_id}"
  codebuild_image             = var.codebuild_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "TerraformApplyProd"
  action_name                 = "Validate"
  environment                 = var.environment
  docker_hub_credentials      = var.docker_hub_credentials
  tags                        = local.tags
  sts_assume_role_duration    = 900
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
