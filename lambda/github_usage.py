""" Handle events from pre-commit hook reporting """
import os

import boto3
import botocore
import requests

from event_parser import parse_messages
from logger import LOG

TOKEN_PREFIX = "/alert-processor/tokens/github/"


def process_event(event):
    """
    Read SNS messages from event and pass to notification handler
    """
    messages = parse_messages(event)
    for message in messages:
        process_message(message)


def process_message(message):
    """
    Receive event body forwarded from lambda handler.
    """
    actions = {"register": register, "commit": commit, "usage": usage}
    action = message["action"]
    process_action = actions[action]
    success = process_action(message)
    if not success:
        LOG.error("Processing failed for %s", action)
    return success


def get_ssm_param(param: str) -> str:
    """ Get parameter by path and return value """
    try:
        client = boto3.client("ssm")
        response = client.get_parameter(Name=param, WithDecryption=True)
        if "Parameter" in response:
            value = response["Parameter"]["Value"]
        else:
            value = None
    except (botocore.exceptions.ClientError, KeyError) as err:
        LOG.error("Failed to get SSM param: %s: %s", param, err)
        value = None
    return value


def get_ssm_params(path: str) -> dict:
    """ Get parameter by path and return value """
    try:
        has_next_page = True
        next_token = None
        params = {}
        while has_next_page:
            client = boto3.client("ssm")
            request = {"Path": path, "Recursive": True, "WithDecryption": True}
            if next_token:
                request["NextToken"] = next_token
            response = client.get_parameters_by_path(**request)

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
        LOG.error("Failed to get SSM params on path: %s: %s", path, err)
        params = []
    return params


def set_ssm_param(param: str, value: str) -> bool:
    """ Write param to SSM and return success status """
    try:
        client = boto3.client("ssm")
        response = client.put_parameter(
            Name=param, Value=value, Type="SecureString", Overwrite=True
        )
        success = "Version" in response
    except botocore.exceptions.ClientError as err:
        LOG.error("Failed to set SSM param: %s: %s", param, err)
        success = False
    return success


def delete_ssm_param(param: str) -> bool:
    """ Delete SSM parameter and return status """
    try:
        client = boto3.client("ssm")
        response = client.delete_parameter(Name=param)
        #  delete parameter returns an empty dict
        success = response == {}
    except botocore.exceptions.ClientError as err:
        LOG.error("Failed to set SSM param: %s: %s", param, err)
        success = False
    return success


def get_github_org_members(org: str, token: str) -> list:
    """ Get all paged list of members from GitHub rest API """
    page = 1
    page_items = 1
    members = []
    while page_items > 0:
        page_items = 0
        url = f"https://api.github.com/orgs/{org}/members?page={page}"
        headers = {"authorization": f"token {token}"}
        response = requests.get(url, headers=headers).json()
        if isinstance(response, list):
            LOG.debug("Got member page %s", page)
            page_items = len(response)
            for user in response:
                members.append(user["login"])
        else:
            LOG.error(str(response))
        page += 1

    LOG.debug("Found %s members: %s", org, str(len(members)))

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


def commit(message=None):
    """
    Record a commit event to splunk.

    Assign commit hash to gihub user and record.
    """
    return True


def usage(message=None):
    """
    Compare registered users to org membership.
    """
    access_token_param = os.environ.get("GITHUB_TOKEN")
    access_token = get_ssm_param(access_token_param)
    user_tokens = get_ssm_params(TOKEN_PREFIX)

    org = os.environ.get("GITHUB_ORG")
    members = get_github_org_members(org, access_token)
    member_count = len(members)
    removed = 0

    removed_usernames = []
    if member_count > 0:
        for username in user_tokens.keys():
            if username not in members:
                removed_usernames.append(username)

    for username in removed_usernames:
        delete_ssm_param(f"{TOKEN_PREFIX}{username}")
        del user_tokens[username]
        removed += 1

    registered_count = len(user_tokens.keys())
    coverage = 100 * registered_count / member_count
    stats = {
        "org": org,
        "registered": registered_count,
        "removed": removed,
        "members": member_count,
        "users": [*user_tokens],
        "percent_coverage": f"{coverage:.1f}",
    }
    LOG.debug(str(stats))
    return stats
