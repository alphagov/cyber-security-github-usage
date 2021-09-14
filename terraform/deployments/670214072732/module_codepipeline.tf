module "codepipeline" {
  source                      = "../../modules/codepipeline"
  codestar_connection_id      = "51c5be90-8c8f-4d32-8be4-18b8f05c802c"
  codebuild_service_role_name = "CodePipelineExecutionRole"
  environment                 = "prod"
  docker_hub_credentials      = "docker_hub_credentials"
  deploy_key                  = "/github/deploy-keys/cyber-security-terraform"
}
