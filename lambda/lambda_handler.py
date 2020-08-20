"""Handler."""
from dataclasses import dataclass
from typing import Any, Dict, List

from github_usage import process_event
from logger import LOG


@dataclass
class LambdaCognitoIdentity:
    cognito_identity_id: str
    cognito_identity_pool_id: str


@dataclass
class LambdaClientContextMobileClient:
    installation_id: str
    app_title: str
    app_version_name: str
    app_version_code: str
    app_package_name: str


@dataclass
class LambdaClientContext:
    client: LambdaClientContextMobileClient
    custom: Dict[str, Any]
    env: Dict[str, Any]


@dataclass
class LambdaContext:
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: LambdaCognitoIdentity
    client_context: LambdaClientContext


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> List[bool]:
    """Handler."""
    LOG.debug("Lambda handler")
    LOG.debug(str(event))
    return process_event(event)
