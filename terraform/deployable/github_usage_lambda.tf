resource "aws_lambda_function" "github_usage_lambda" {
  filename         = local.zipfile
  source_code_hash = filebase64sha256(local.zipfile)
  function_name    = "github_usage_lambda"
  role             = aws_iam_role.github_usage_role.arn
  handler          = "lambda_handler.lambda_handler"
  timeout          = 60
  runtime          = "python3.7"

  tags             = merge(local.tags, {"Name":"github_usage_lambda"})

  environment {
    variables = {
      ENVIRONMENT   = var.ENVIRONMENT
      LOGLEVEL      = "DEBUG"
      GITHUB_ORG    = var.GITHUB_ORG
      GITHUB_TOKEN  = var.GITHUB_TOKEN
    }
  }
}
