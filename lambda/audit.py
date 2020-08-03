import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError

import github_api
from logger import LOG


def start(message=None):
    """ Start an audit of github membership """
    org = os.environ.get("GITHUB_ORG")
    audit_id = str(uuid.uuid4())
    LOG.info({"action": "Starting github audit", "org": org, "audit_id": audit_id})

    sns_org_members = create_sns_message(
        {"action": "log_org_membership", "org": org, "audit_id": audit_id}
    )
    publish_alert(sns_org_members)

    sns_org_repos = create_sns_message(
        {"action": "log_org_repos", "org": org, "audit_id": audit_id}
    )
    publish_alert(sns_org_repos)

    sns_org_teams = create_sns_message(
        {"action": "log_org_teams", "org": org, "audit_id": audit_id}
    )
    publish_alert(sns_org_teams)
    return True


def log_org_membership(message=None):
    """ Audit github organization membership """
    org = os.environ.get("GITHUB_ORG")
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info({"action": "Audit organization members", "org": org})
        members = github_api.get_github_org_members(org)
        event = {
            "type": "OrganizationMemberCount",
            "org": org,
            "count": len(members),
            "audit_id": audit_id,
        }
        LOG.info(event)
        for member in members:
            event = {
                "type": "OrganizationMember",
                "org": org,
                "member": member,
                "team": None,
                "repository": None,
                "audit_id": audit_id,
            }
            LOG.info(event)
    return True


def log_org_teams(message=None):
    """ Audit github organization teams """
    org = os.environ.get("GITHUB_ORG")
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info({"action": "Audit organization teams", "org": org})
        teams = github_api.get_github_org_teams(org)
        event = {
            "type": "OrganizationTeamCount",
            "org": org,
            "count": len(teams),
            "audit_id": audit_id,
        }
        LOG.info(event)
        for team in teams:
            event = {
                "type": "OrganizationTeam",
                "org": org,
                "member": None,
                "team": team,
                "repository": None,
                "audit_id": audit_id,
            }
            LOG.info(event)
            sns_team_membership = create_sns_message(
                {
                    "action": "log_org_team_membership",
                    "org": org,
                    "team": team,
                    "audit_id": audit_id,
                }
            )
            publish_alert(sns_team_membership)

            sns_team_repos = create_sns_message(
                {
                    "action": "log_org_team_repos",
                    "org": org,
                    "team": team,
                    "audit_id": audit_id,
                }
            )
            publish_alert(sns_team_repos)
    return True


def log_org_team_membership(message=None):
    """ Audit github organization team membership """
    org = os.environ.get("GITHUB_ORG")
    team = message.get("team", None)
    team_name = team["slug"]
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info({"action": "Audit team members", "org": org, "team": team_name})
        if team is not None:
            members = github_api.get_github_org_team_members(org, team_name)
            event = {
                "type": "OrganizationTeamMemberCount",
                "org": org,
                "team": team,
                "count": len(members),
                "audit_id": audit_id,
            }
            LOG.info(event)
            for member in members:
                event = {
                    "type": "OrganizationTeamMember",
                    "org": org,
                    "member": member,
                    "team": team,
                    "repository": None,
                    "audit_id": audit_id,
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
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info(
            {
                "action": "Audit organization team repos",
                "org": org,
                "team": team_name,
                "audit_id": audit_id,
            }
        )
        if team is not None:
            repos = github_api.get_github_org_team_repositories(org, team_name)
            for repo in repos:
                event = {
                    "type": "OrganizationRepoTeam",
                    "org": org,
                    "member": None,
                    "team": team,
                    "repository": repo,
                    "audit_id": audit_id,
                }
                LOG.info(event)
                sns_repo_team_members = create_sns_message(
                    {
                        "action": "log_org_repo_team_members",
                        "org": org,
                        "repo": repo,
                        "team": team,
                        "audit_id": audit_id,
                    }
                )
                publish_alert(sns_repo_team_members)
        else:
            LOG.error({"error": "Team not specified"})
    return True


def log_org_repos(message=None):
    """ Audit github organization repositories """
    org = os.environ.get("GITHUB_ORG")
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info({"action": "Audit organization org repos", "org": org})
        repos = github_api.get_github_org_repositories(org)
        event = {
            "type": "OrganizationRepoCount",
            "org": org,
            "count": len(repos),
            "audit_id": audit_id,
        }
        LOG.info(event)
        for repo in repos:
            event = {
                "type": "OrganizationRepo",
                "org": org,
                "member": None,
                "team": None,
                "repository": repo,
                "audit_id": audit_id,
            }
            LOG.info(event)
            sns_repo_contributors = create_sns_message(
                {
                    "action": "log_org_repo_contributors",
                    "org": org,
                    "repo": repo,
                    "audit_id": audit_id,
                }
            )
            publish_alert(sns_repo_contributors)

    return True


def log_org_repo_contributors(message=None):
    """ Audit github organization repository contributors """
    org = os.environ.get("GITHUB_ORG")
    repo = message.get("repo", None)
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info(
            {
                "action": "Audit organization org repo contributors",
                "org": org,
                "repo": repo,
                "audit_id": audit_id,
            }
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
                    "audit_id": audit_id,
                }
                LOG.info(event)
        else:
            LOG.error({"error": "Repo not specified"})
    return True


def log_org_repo_team_members(message=None):
    """ Audit github organization repository team members """
    org = os.environ.get("GITHUB_ORG")
    repo = message.get("repo", None)
    team = message.get("team", None)
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info(
            {
                "action": "Audit organization org repo contributors",
                "org": org,
                "repo": repo,
                "audit_id": audit_id,
            }
        )
        team_name = team["slug"]
        if repo is not None:
            members = github_api.get_github_org_team_members(org, team_name)
            for member in members:
                event = {
                    "type": "OrganizationRepoTeamMember",
                    "org": org,
                    "member": member,
                    "team": team,
                    "repository": repo,
                    "audit_id": audit_id,
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
            {"default": "Default payload", "sqs": payload, "lambda": payload},
            default=str,
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
