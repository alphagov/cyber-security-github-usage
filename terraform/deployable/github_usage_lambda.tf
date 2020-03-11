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
      GITHUB_ORG    = var.GITHUB_ORG
      GITHUB_TOKEN  = var.GITHUB_TOKEN
      LOG_LEVEL     = var.LOG_LEVEL
    }
  }
}

resource "aws_cloudwatch_event_rule" "run_schedule" {
  name                = "github_usage_run_schedule"
  description         = "Run on cron schedule"
  schedule_expression = var.cron_schedule
}

resource "aws_cloudwatch_event_target" "run_every_x_minutes" {
  rule      = aws_cloudwatch_event_rule.run_schedule.name
  target_id = aws_lambda_function.github_usage_lambda.function_name
  arn       = aws_lambda_function.github_usage_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_usage_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.run_schedule.arn
}

