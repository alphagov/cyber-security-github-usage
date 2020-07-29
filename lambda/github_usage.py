""" Handle events from pre-commit hook reporting """
import json
import os

import audit
import config
import github_api
from event_parser import parse_messages
from logger import LOG

TOKEN_PREFIX = "/alert-processor/tokens/github/"
API_ROOT = "https://api.github.com"


def process_event(event):
    """
    Read SNS messages from event and pass to notification handler
    """
    messages = parse_messages(event)
    responses = []
    for message in messages:
        response = process_message(message)
        responses.append(response)
    return responses


def process_message(message):
    """
    Receive event body forwarded from lambda handler.
    """
    actions = {
        "register": register,
        "commit": commit,
        "usage": usage,
        "audit": audit.start,
        "log_org_membership": audit.log_org_membership,
        "log_org_teams": audit.log_org_teams,
        "log_org_team_membership": audit.log_org_team_membership,
        "log_org_team_repos": audit.log_org_team_repos,
        "log_org_repos": audit.log_org_repos,
        "log_org_repo_contributors": audit.log_org_repo_contributors,
    }
    action = message["action"]
    process_action = actions[action]
    success = process_action(message)
    if not success:
        LOG.error("Processing failed for %s", action)
    return success


def register(notification):
    """
    Register user.

    Record user token in SSM.
    Report to Splunk.
    """
    username = notification["username"]
    token = notification["user_secret"]
    param = f"{TOKEN_PREFIX}{username}"
    param_set = config.set_ssm_param(param, token)
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
    user_tokens = config.get_ssm_params(TOKEN_PREFIX)

    org = os.environ.get("GITHUB_ORG")
    members = github_api.get_member_logins(github_api.get_github_org_members(org))

    member_count = len(members)
    removed = 0

    removed_usernames = []
    if member_count > 0:
        for username in user_tokens.keys():
            if username not in members:
                removed_usernames.append(username)

    for username in removed_usernames:
        config.delete_ssm_param(f"{TOKEN_PREFIX}{username}")
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
    LOG.info(json.dumps(stats, default=str))
    return stats
