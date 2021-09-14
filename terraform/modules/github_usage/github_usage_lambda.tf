resource "aws_lambda_function" "github_usage_lambda" {
  filename                       = local.zipfile
  source_code_hash               = filebase64sha256(local.zipfile)
  function_name                  = "github_usage_lambda"
  role                           = aws_iam_role.github_usage_role.arn
  handler                        = "lambda_handler.lambda_handler"
  timeout                        = 600
  runtime                        = "python3.7"
  reserved_concurrent_executions = 6

  tags = merge(local.tags, { "Name" : "github_usage_lambda" })

  environment {
    variables = {
      ENVIRONMENT  = var.ENVIRONMENT
      GITHUB_ORG   = var.GITHUB_ORG
      GITHUB_TOKEN = var.GITHUB_TOKEN
      LOG_LEVEL    = var.LOG_LEVEL
      SNS_ARN      = data.aws_sns_topic.github_usage_sub.arn
    }
  }
}

resource "aws_cloudwatch_event_rule" "usage_run_schedule" {
  count               = var.usage_cron_schedule == "" ? 0 : 1
  name                = "github_usage_usage_action_run_schedule"
  description         = "Run on cron schedule"
  schedule_expression = var.usage_cron_schedule
}

# Schedule usage update = action:usage
data "template_file" "usage_event" {
  template = file("${path.module}/json/lambda_event.json")
  vars = {
    action = "usage"
  }
}

resource "aws_cloudwatch_event_target" "run_usage_every_x_minutes" {
  count     = var.usage_cron_schedule == "" ? 0 : 1
  rule      = element(aws_cloudwatch_event_rule.usage_run_schedule.*.name, 0)
  target_id = aws_lambda_function.github_usage_lambda.function_name
  arn       = aws_lambda_function.github_usage_lambda.arn
  input     = data.template_file.usage_event.rendered
}

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_usage_lambda" {
  count         = var.usage_cron_schedule == "" ? 0 : 1
  statement_id  = "AllowUsageExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_usage_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = element(aws_cloudwatch_event_rule.usage_run_schedule.*.arn, 0)
}

# Schedule membership audit = action:audit
resource "aws_cloudwatch_event_rule" "audit_run_schedule" {
  count               = var.audit_cron_schedule == "" ? 0 : 1
  name                = "github_usage_audit_action_run_schedule"
  description         = "Run on cron schedule"
  schedule_expression = var.audit_cron_schedule
}

data "template_file" "audit_event" {
  template = file("${path.module}/json/lambda_event.json")
  vars = {
    action = "audit"
  }
}

resource "aws_cloudwatch_event_target" "run_audit_every_x_minutes" {
  count     = var.audit_cron_schedule == "" ? 0 : 1
  rule      = element(aws_cloudwatch_event_rule.audit_run_schedule.*.name, 0)
  target_id = aws_lambda_function.github_usage_lambda.function_name
  arn       = aws_lambda_function.github_usage_lambda.arn
  input     = data.template_file.audit_event.rendered
}

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_audit_lambda" {
  count         = var.audit_cron_schedule == "" ? 0 : 1
  statement_id  = "AllowAuditExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_usage_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = element(aws_cloudwatch_event_rule.audit_run_schedule.*.arn, 0)
}

