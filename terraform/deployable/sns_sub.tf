data "aws_sns_topic" "github_usage_sub" {
  name = "alert-controller-github-usage"
}

resource "aws_lambda_permission" "cloudwatch_forwarder_euw2_sns_invoke" {
  statement_id  = "CloudForwarderEUW2AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_usage_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = data.aws_sns_topic.github_usage_sub.arn
}

resource "aws_sns_topic_subscription" "github_usage_sub_sns_subscription" {
  topic_arn = data.aws_sns_topic.github_usage_sub.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.github_usage_lambda.arn
}
