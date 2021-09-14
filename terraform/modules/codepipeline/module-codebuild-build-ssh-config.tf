module "codebuild-build-ssh-config" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_build_ssh_config"
  codebuild_service_role_name = var.codebuild_service_role_name
  codebuild_image             = var.codebuild_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "BuildSshConfig"
  action_name                 = "CreateConfig"
  environment                 = var.environment
  deploy_key                  = var.deploy_key
  tags                        = local.tags
}
