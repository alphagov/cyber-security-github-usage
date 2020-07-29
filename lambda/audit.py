import json
import os

import boto3
from botocore.exceptions import ClientError

import github_api
from logger import LOG


def start(message=None):
    """ Start an audit of github membership """
    org = os.environ.get("GITHUB_ORG")
    LOG.info({"action": "Starting github audit", "org": org})

    sns_org_members = create_sns_message({"action": "log_org_membership", "org": org})
    publish_alert(sns_org_members)

    sns_org_repos = create_sns_message({"action": "log_org_repos", "org": org})
    publish_alert(sns_org_repos)

    sns_org_teams = create_sns_message({"action": "log_org_teams", "org": org})
    publish_alert(sns_org_teams)
    return True


def log_org_membership(message=None):
    """ Audit github organization membership """
    org = os.environ.get("GITHUB_ORG")
    LOG.info({"action": "Audit organization members", "org": org})
    members = github_api.get_github_org_members(org)
    for member in members:
        event = {
            "type": "OrganizationMember",
            "org": org,
            "member": member,
            "team": None,
            "repository": None,
        }
        LOG.info(event)
    return True


def log_org_teams(message=None):
    """ Audit github organization teams """
    org = os.environ.get("GITHUB_ORG")
    LOG.info({"action": "Audit organization teams", "org": org})
    teams = github_api.get_github_org_teams(org)
    for team in teams:
        event = {
            "type": "OrganizationTeam",
            "org": org,
            "member": None,
            "team": team,
            "repository": None,
        }
        LOG.info(event)
        sns_team_membership = create_sns_message(
            {"action": "log_org_team_membership", "org": org, "team": team}
        )
        publish_alert(sns_team_membership)

        sns_team_repos = create_sns_message(
            {"action": "log_org_team_repos", "org": org, "team": team}
        )
        publish_alert(sns_team_repos)
    return True


def log_org_team_membership(message=None):
    """ Audit github organization team membership """
    org = os.environ.get("GITHUB_ORG")
    team = message.get("team", None)
    team_name = team["slug"]
    LOG.info({"action": "Audit team members", "org": org, "team": team_name})
    if team is not None:
        members = github_api.get_github_org_team_members(org, team_name)
        for member in members:
            event = {
                "type": "OrganizationTeamMember",
                "org": org,
                "member": member,
                "team": team,
                "repository": None,
            }
            LOG.info(event)
    else:
        LOG.error({"error": "Team not specified"})

    return True


def log_org_team_repos(message=None):
    """ Audit github organization repo team access """
    org = os.environ.get("GITHUB_ORG")
    team = message.get("team", None)
    team_name = team["slug"]
    LOG.info({"action": "Audit organization team repos", "org": org, "team": team_name})
    if team is not None:
        repos = github_api.get_github_org_team_repositories(org, team_name)
        for repo in repos:
            event = {
                "type": "OrganizationRepoTeam",
                "org": org,
                "member": None,
                "team": team,
                "repository": repo,
            }
            LOG.info(event)
    else:
        LOG.error({"error": "Team not specified"})
    return True


def log_org_repos(message=None):
    """ Audit github organization repositories """
    org = os.environ.get("GITHUB_ORG")
    LOG.info({"action": "Audit organization org repos", "org": org})
    repos = github_api.get_github_org_repositories(org)
    for repo in repos:
        event = {
            "type": "OrganizationRepo",
            "org": org,
            "member": None,
            "team": None,
            "repository": repo,
        }
        LOG.info(event)
        sns_repo_contributors = create_sns_message(
            {"action": "log_org_repo_contributors", "org": org, "repo": repo}
        )
        publish_alert(sns_repo_contributors)

    return True


def log_org_repo_contributors(message=None):
    """ Audit github organization repository contributors """
    org = os.environ.get("GITHUB_ORG")
    repo = message.get("repo", None)
    LOG.info(
        {"action": "Audit organization org repo contributors", "org": org, "repo": repo}
    )
    repo_name = repo["name"]
    if repo is not None:
        members = github_api.get_github_org_repo_contributors(org, repo_name)
        for member in members:
            event = {
                "type": "OrganizationRepoContributor",
                "org": org,
                "member": member,
                "team": None,
                "repository": repo,
            }
            LOG.info(event)
    else:
        LOG.error({"error": "Repo not specified"})
    return True


def create_sns_message(body):
    """ Create the message to publish to SNS """
    try:
        payload = json.dumps(body)

        message = json.dumps(
            {"default": "Default payload", "sqs": payload, "lambda": payload}
        )
        LOG.debug("MESSAGE: %s", message)

        return message
    except TypeError as err:
        LOG.error({"error": err})


def publish_alert(message):
    """ Publish alert message to SNS """
    try:
        topic_arn = os.environ.get("SNS_ARN")
        subject = "GitHub organization access audit"
        sns = boto3.client("sns")
        sns_response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject,
            MessageStructure="json",
        )
        LOG.debug("SNS Response: %s", sns_response)
        LOG.info("Alert published to SNS")

        return sns_response
    except ClientError as err:
        LOG.error({"error": err})
