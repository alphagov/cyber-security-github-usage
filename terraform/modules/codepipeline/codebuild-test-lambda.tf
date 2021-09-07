resource "aws_codebuild_project" "codepipeline_test_lambda" {
  name           = "codepipeline-test-lambda"
  description    = "Run tests against the lambda"

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
    image                       = "gdscyber/cyber-security-concourse-base-image:latest"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    privileged_mode             = false

    registry_credential {
      credential          = data.aws_secretsmanager_secret.dockerhub_creds.arn
      credential_provider = "SECRETS_MANAGER"
    }
  }

  source {
    type            = "CODEPIPELINE"
    buildspec       = file("${path.module}/code-build-test-lambda.yml")
  }

}