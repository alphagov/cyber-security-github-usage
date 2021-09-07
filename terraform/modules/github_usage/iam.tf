data "aws_iam_policy_document" "github_usage_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "github_usage_role" {
  name               = "github_usage_role"
  assume_role_policy = data.aws_iam_policy_document.github_usage_assume_role.json
}

# Publish events to SNS topic
data "aws_iam_policy_document" "github_usage_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "sns:Publish"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:PutParameter",
      "ssm:DeleteParameter"
    ]

    resources = [
      "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/alert-processor/tokens/github/*"
    ]
  }
}

resource "aws_iam_policy" "github_usage_policy" {
  name   = "GitHubUsagePolicy"
  policy = data.aws_iam_policy_document.github_usage_policy_document.json
}

resource "aws_iam_role_policy_attachment" "github_usage_policy_attachment" {
  role       = aws_iam_role.github_usage_role.name
  policy_arn = aws_iam_policy.github_usage_policy.arn
}

resource "aws_iam_role_policy_attachment" "health_monitor_canned_policy_attachment" {
  role       = aws_iam_role.github_usage_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "ssm_read_only_policy_attach" {
  role       = aws_iam_role.github_usage_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

