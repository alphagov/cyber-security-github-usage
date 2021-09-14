import json
import os
import uuid
from typing import Any, Dict, Optional, Union

import boto3
from botocore.exceptions import ClientError  # type: ignore
from mypy_boto3_sns import SNSClient

import github_api
from logger import LOG


def start(message: Dict[str, Any]) -> None:
    """
    Start an audit of github membership

    The message argument is not used but is included as it's a
    passthru from the lambda invoke.
    """
    org = os.environ.get("GITHUB_ORG")
    audit_id = str(uuid.uuid4())
    LOG.info({"action": "Starting github audit", "org": org, "audit_id": audit_id})

    send_sns_trigger(action="log_org_membership", org=org, audit_id=audit_id)

    send_sns_trigger(action="log_org_repos", org=org, audit_id=audit_id)

    send_sns_trigger(action="log_org_teams", org=org, audit_id=audit_id)


def log_org_membership(message: Dict[str, Any]) -> None:
    """ Audit github organization membership """
    org = os.environ["GITHUB_ORG"]
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info({"action": "Audit organization members", "org": org})
        members = github_api.get_github_org_members(org)
        event = make_audit_event(
            type="OrganizationMemberCount",
            org=org,
            count=len(members),
            audit_id=audit_id,
        )
        LOG.info(event)
        for member in members:
            event = make_audit_event(
                type="OrganizationMember", org=org, member=member, audit_id=audit_id
            )
            LOG.info(event)


def log_org_teams(message: Dict[str, Any]) -> None:
    """ Audit github organization teams """
    org = os.environ["GITHUB_ORG"]
    audit_id = message.get("audit_id")
    if audit_id is not None:
        LOG.info({"action": "Audit organization teams", "org": org})
        teams = github_api.get_github_org_teams(org)
        event = make_audit_event(
            type="OrganizationTeamCount", org=org, count=len(teams), audit_id=audit_id
        )
        LOG.info(event)
        for team in teams:
            event = make_audit_event(
                type="OrganizationTeam", org=org, team=team, audit_id=audit_id
            )
            LOG.info(event)
            send_sns_trigger(
                action="log_org_team_membership",
                org=org,
                team=team,
                audit_id=audit_id,
            )

            send_sns_trigger(
                action="log_org_team_repos", org=org, team=team, audit_id=audit_id
            )


def log_org_team_membership(message: Dict[str, Any]) -> None:
    """ Audit github organization team membership """
    org = os.environ["GITHUB_ORG"]

    team = message["team"]

    team_name: Optional[str] = team.get("slug")

    audit_id = message.get("audit_id")
    if audit_id:
        LOG.info({"action": "Audit team members", "org": org, "team": team_name})
        if team and team_name:
            members = github_api.get_github_org_team_members(org, team_name)
            event = make_audit_event(
                type="OrganizationTeamMemberCount",
                org=org,
                team=team,
                count=len(members),
                audit_id=audit_id,
            )
            LOG.info(event)
            for member in members:
                event = make_audit_event(
                    type="OrganizationTeamMember",
                    org=org,
                    member=member,
                    team=team,
                    audit_id=audit_id,
                )
                LOG.info(event)
        else:
            raise IncompleteAuditError(
                audit_id=audit_id,
                source=message,
                message="Team not specified",
            )


def log_org_team_repos(message: Dict[str, Any]) -> None:
    """ Audit github organization repo team access """
    org = os.environ["GITHUB_ORG"]

    team = message["team"]

    audit_id = message.get("audit_id")
    if team and audit_id:
        team_name = team["slug"]

        LOG.info(
            {
                "action": "Audit organization team repos",
                "org": org,
                "team": team_name,
                "audit_id": audit_id,
            }
        )
        if team:
            repos = github_api.get_github_org_team_repositories(org, team_name)
            for repo in repos:
                event = make_audit_event(
                    type="OrganizationRepoTeam",
                    org=org,
                    team=team,
                    repository=repo,
                    audit_id=audit_id,
                )
                LOG.info(event)
                send_sns_trigger(
                    action="log_org_repo_team_members",
                    org=org,
                    repo=repo,
                    team=team,
                    audit_id=audit_id,
                )
        else:
            raise IncompleteAuditError(
                audit_id=audit_id,
                source=message,
                message="Missing parameter",
            )


def log_org_repos(message: Dict[str, Union[str, Dict[str, str]]]) -> None:
    """ Audit github organization repositories """
    org = os.environ["GITHUB_ORG"]
    audit_id = message.get("audit_id")
    if isinstance(audit_id, str):
        LOG.info({"action": "Audit organization org repos", "org": org})
        repos = github_api.get_github_org_repositories(org)
        event = make_audit_event(
            type="OrganizationRepoCount", org=org, count=len(repos), audit_id=audit_id
        )
        LOG.info(event)
        for repo in repos:
            event = make_audit_event(
                type="OrganizationRepo", org=org, repository=repo, audit_id=audit_id
            )
            LOG.info(event)
            send_sns_trigger(
                action="log_org_repo_contributors",
                org=org,
                repo=repo,
                audit_id=audit_id,
            )


def log_org_repo_contributors(message: Dict[str, Any]) -> None:
    """ Audit github organization repository contributors """
    org = os.environ["GITHUB_ORG"]
    repo = message.get("repo", None)
    audit_id = message.get("audit_id")
    if audit_id:
        LOG.info(
            {
                "action": "Audit organization org repo contributors",
                "org": org,
                "repo": repo,
                "audit_id": audit_id,
            }
        )

        if repo:
            repo_name = repo["name"]
            members = github_api.get_github_org_repo_contributors(org, repo_name)
            for member in members:
                event = make_audit_event(
                    type="OrganizationRepoContributor",
                    org=org,
                    member=member,
                    repository=repo,
                    audit_id=audit_id,
                )
                LOG.info(event)
        else:
            raise IncompleteAuditError(
                audit_id=audit_id, source=message, message="Repo not specified"
            )


def log_org_repo_team_members(message: Dict[str, Any]) -> None:
    """ Audit github organization repository team members """
    org = os.environ["GITHUB_ORG"]
    repo = message.get("repo")

    team = message.get("team")

    if isinstance(team, dict):
        team_name: Optional[str] = team.get("slug")
    else:
        team_name = None

    audit_id = message.get("audit_id")

    if audit_id and team_name:
        LOG.info(
            {
                "action": "Audit organization org repo contributors",
                "org": org,
                "repo": repo,
                "audit_id": audit_id,
            }
        )

        if repo and team:
            members = github_api.get_github_org_team_members(org, team_name)
            for member in members:
                event = make_audit_event(
                    type="OrganizationRepoTeamMember",
                    org=org,
                    member=member,
                    team=team,
                    repository=repo,
                    audit_id=audit_id,
                )
                LOG.info(event)
        else:
            raise IncompleteAuditError(
                audit_id=audit_id, message="Repo not specified", source=message
            )


def create_sns_message(audit_id: str, body: Dict[str, Any]) -> str:
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
        raise IncompleteAuditError(audit_id=audit_id, message=err, source=body)


def publish_alert(audit_id: str, message: str) -> Any:
    """ Publish alert message to SNS """
    try:
        topic_arn = os.environ["SNS_ARN"]
        subject = "GitHub organization access audit"
        sns: SNSClient = boto3.client("sns")  # type: ignore
        sns_response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject,
            MessageStructure="json",
        )
        LOG.debug("SNS Response: %s", sns_response)
        LOG.info("Alert ed to SNS")

        return sns_response
    except ClientError as err:
        raise IncompleteAuditError(audit_id=audit_id, source=message, message=err)
        return None


def make_audit_event(
    type: Optional[str] = None,
    org: Optional[str] = None,
    member: Optional[Dict[str, Any]] = None,
    team: Optional[Dict[str, Any]] = None,
    repository: Optional[Dict[str, Any]] = None,
    count: int = 0,
    audit_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create an audit event dictionary with a fixed data model

    Converts arguments to a dictionary.
    The Nones should be present in the dictionary.
    """
    return locals()


def send_sns_trigger(
    action: Optional[str] = None,
    org: Optional[str] = None,
    repo: Optional[Dict[str, Any]] = None,
    team: Optional[Dict[str, Any]] = None,
    audit_id: str = "",
) -> Any:
    """
    Create the SNS payload to trigger the next lambda invovation
    """
    event = locals()
    payload = create_sns_message(audit_id, event)
    response = publish_alert(audit_id, payload)
    return response


class IncompleteAuditError(Exception):
    """
    Create a wrapper to log an
    """

    def __init__(
        self,
        audit_id: str,
        source: Union[str, Any],
        message: Union[str, TypeError] = "Incomplete audit error",
    ):
        self.audit_id = audit_id
        self.message = message
        self.source = source
        super().__init__(self.message)
        LOG.error(
            {
                "audit_id": audit_id,
                "error": "Incomplete audit",
                "message": message,
                "source": source,
            }
        )
