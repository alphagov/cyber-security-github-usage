resource "aws_codebuild_project" "codebuild_execute_lambda" {
  name           = "codepipeline-execute-lambda"
  description    = "Executes the lambda"

  service_role = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"

  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE", "LOCAL_SOURCE_CACHE"]
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = var.codebuild_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    privileged_mode             = false

  }

  source {
    type            = "CODEPIPELINE"
    buildspec       = file("${path.module}/codebuild-execute-lambda.yml")
  }

}