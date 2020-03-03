"""Handler."""
from logger import LOG
from github_usage import process_notification


def lambda_handler(event, context):
    """Handler."""
    LOG.debug("Lambda handler")
    return process_notification(event["body"])
