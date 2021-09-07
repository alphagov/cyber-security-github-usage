resource "aws_codebuild_project" "codebuild_zip_lambda" {
  name           = "codepipeline-zip-lambda"
  description    = "Zips the lambda"

  service_role = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"

  }

  secondary_artifacts {
    type                = "S3"
    # name                = "github_usage_lambda"
    packaging           = "ZIP"
    artifact_identifier = "lambda_zip"
    location            = data.aws_s3_bucket.artifact_store.bucket
    path                = var.output_artifact_path
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
    buildspec       = file("${path.module}/codebuild-zip-lambda.yml")
  }

}