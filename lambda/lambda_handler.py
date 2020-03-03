"""Handler."""
from github_usage import process_event
from logger import LOG


def lambda_handler(event, context):
    """Handler."""
    LOG.debug("Lambda handler")
    return process_event(event)
