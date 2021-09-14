resource "aws_codepipeline" "github-usage" {
  name     = "${var.pipeline_name}"
  role_arn = data.aws_iam_role.pipeline_role.arn
  tags     = merge(local.tags, { Name = "${var.pipeline_name}" })

  artifact_store {
    type     = "S3"
    location = data.aws_s3_bucket.artifact_store.bucket
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["git_usage"]
      configuration = {
        ConnectionArn    = "arn:aws:codestar-connections:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:connection/${var.codestar_connection_id}"
        FullRepositoryId = "alphagov/cyber-security-github-usage"
        BranchName       = "master"
      }
    }
  }

  stage {
    name = "BuildLambda"

    action {
      name             = "TestLambda"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 1
      input_artifacts  = ["git_usage"]
      output_artifacts = []

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_test_lambda.name
      }
    }

    action {
      name             = "BuildLambdaZip"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 2
      input_artifacts  = ["git_usage"]
      output_artifacts = ["lambda_zip"]

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_zip_lambda.name
      }
    }
  }

  stage {
    name = "BuildSshConfig"

    action {
      name             = "CreateConfig"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["git_usage"]
      output_artifacts = ["ssh_config"]

      configuration = {
        PrimarySource = "git_usage"
        ProjectName = module.codebuild-build-ssh-config.project_name
      }
    }
  }

  stage {
    name = "TerraformApplyStaging"

    action {
      name             = "Validate"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 1
      input_artifacts  = ["git_usage", "lambda_zip", "ssh_config"]
      output_artifacts = []

      configuration = {
        PrimarySource = "git_usage"
        ProjectName = module.codebuild-validate-terraform-staging.project_name
      }
    }

    action {
      name             = "TerraformApply"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 2
      input_artifacts  = ["git_usage", "lambda_zip", "ssh_config"]
      output_artifacts = ["staging_terraform_output"]

      configuration = {
        PrimarySource = "git_usage"
        ProjectName = module.codebuild-apply-terraform-staging.project_name
      }
    }

    action {
      name             = "LambdaInvoke"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 3
      input_artifacts  = ["git_usage", "lambda_zip", "ssh_config"]
      output_artifacts = []

      configuration = {
        PrimarySource        = "git_usage"
        ProjectName          = aws_codebuild_project.codebuild_execute_lambda.name
        EnvironmentVariables = jsonencode([{"name": "ACCOUNT_ID", "value": var.staging_account_id}])
      }
    }
  }

  stage {
    name = "TerraformApplyProd"

    action {
      name             = "Validate"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 1
      input_artifacts  = ["git_usage", "lambda_zip", "ssh_config"]
      output_artifacts = []

      configuration = {
        PrimarySource = "git_usage"
        ProjectName = module.codebuild-validate-terraform-prod.project_name
      }
    }

    action {
      name             = "TerraformApply"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 2
      input_artifacts  = ["git_usage", "lambda_zip", "ssh_config"]
      output_artifacts = ["prod_terraform_output"]

      configuration = {
        PrimarySource = "git_usage"
        ProjectName = module.codebuild-apply-terraform-prod.project_name
      }
    }

    action {
      name             = "LambdaInvoke"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      run_order        = 3
      input_artifacts  = ["git_usage", "lambda_zip", "ssh_config"]
      output_artifacts = []

      configuration = {
        PrimarySource        = "git_usage"
        ProjectName          = aws_codebuild_project.codebuild_execute_lambda.name
        EnvironmentVariables = jsonencode([{"name": "ACCOUNT_ID", "value": var.prod_account_id}])
      }
    }
  }

  stage {
    name = "Update"

    action {
      name             = "UpdatePipeline"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["git_usage"]
      output_artifacts = []

      configuration = {
        ProjectName = module.codebuild-self-update.project_name
      }
    }
  }
}
