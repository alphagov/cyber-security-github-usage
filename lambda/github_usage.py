""" Handle events from pre-commit hook reporting """
import os

import boto3
import botocore
import requests

from logger import LOG


TOKEN_PREFIX = "/alert-processor/tokens/github/"


def process_notification(notification):
    """
    Receive event body forwarded from lambda handler.
    """
    actions = {
        "register": register,
        "commit": commit,
        "usage": usage
    }
    action = notification["action"]
    process_action = actions[action]
    success = process_action(notification)
    if not success:
        LOG.error(f"Processing failed for {action}")
    return success


def get_ssm_param(param:str) -> str:
    """ Get parameter by path and return value """
    try:
        client = boto3.client("ssm")
        response = client.get_parameter(
            Name=param,
            WithDecryption=True
        )
        value = response["Value"]
    except botocore.exceptions.ClientError as err:
        LOG.error(f"Failed to get SSM param: {param}: {err}")
        value = None
    return value


def get_ssm_params(path:str) -> str:
    """ Get parameter by path and return value """
    try:
        has_next_page = True
        next_token = None
        params = []
        while has_next_page:
            client = boto3.client("ssm")
            params = {
                "Path": path,
                "Recursive": True,
                "WithDecryption": True
            }
            if next_token:
                params["NextToken"] = next_token
            response = client.get_parameters_by_path(**params)

            # Iterate parameters in response and append to dictionary
            for param in response["Parameters"]:
                name = param["Name"].replace(path, "")
                params[name] = param["Value"]

            # Check for next page in results
            has_next_page = "NextToken" in response
            if has_next_page:
                next_token = response["NextToken"]
            else:
                next_token = None

    except botocore.exceptions.ClientError as err:
        LOG.error(f"Failed to get SSM param: {param}: {err}")
        params = []
    return params


def set_ssm_param(param, value):
    """ Write param to SSM and return success status """
    try:
        client = boto3.client("ssm")
        response = client.put_parameter(
            Name=param,
            Value=value,
            Type='SecureString',
            Overwrite=True
        )
        success = "Version" in response
    except botocore.exceptions.ClientError as err:
        LOG.error(f"Failed to set SSM param: {param}: {err}")
        success = False
    return success


def get_github_org_members(token):
    """ Get all paged list of members from GitHub rest API """
    org = os.environ.get("GITHUB_ORG")

    page = 1
    page_items = 1
    members = []
    while page_items > 0:
        url = f"https://api.github.com/orgs/{org}/members?page={page}"
        response = requests.get(url).json()
        page_items = response.count()
        for user in response:
            members.append(user["login"])

    return members


def register(notification):
    """
    Register user.

    Record user token in SSM.
    Report to Splunk.
    """
    username = notification["username"]
    token = notification["user_secret"]
    param = f"{TOKEN_PREFIX}{username}"
    param_set = set_ssm_param(param, token)
    return param_set


def commit(notification):
    """
    Record a commit event to splunk.

    Assign commit hash to gihub user and record.
    """
    return True

def usage(notification):
    """
    Compare registered users to org membership.
    """
    access_token_param = "/github/usage/pat"
    access_token = get_ssm_param(access_token_param)
    user_tokens = get_ssm_params(TOKEN_PREFIX)
    members = get_github_org_members(access_token)


    return user_tokens