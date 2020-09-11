import os
import time
from typing import Any, Dict, List, Optional, Union

import requests

import config
from logger import LOG

TOKEN_PREFIX = "/alert-processor/tokens/github/"
API_ROOT = "https://api.github.com"
ACCESS_TOKEN = None


def set_github_access_token(token: str) -> None:
    """ Get the access token once """
    global ACCESS_TOKEN
    ACCESS_TOKEN = token


def get_github_access_token() -> Optional[str]:
    """ Get the access token once """
    global ACCESS_TOKEN
    if ACCESS_TOKEN is None:
        access_token_param = os.environ["GITHUB_TOKEN"]
        ACCESS_TOKEN = config.get_ssm_param(access_token_param)
    return ACCESS_TOKEN


def get_github_api_paged_data(url: str) -> List[Any]:
    token = get_github_access_token()
    page = 1
    page_size = 100
    page_items = 1
    items = []
    while page_items > 0:
        page_items = 0
        page_url = f"{url}?page={page}&per_page={page_size}"
        headers = {"authorization": f"token {token}"}
        response = requests.get(page_url, headers=headers)

        if response.status_code == 200:
            response_items = response.json()
            LOG.debug("Got item page %s for URL %s", page, url)
            page_items = len(response_items)
            # append page to parent array
            for item in response_items:
                items.append(item)
        else:
            raise GithubApiError(response.text)
        page += 1
        # this sleep is important to prevent rate limiting
        time.sleep(4)

    return items


def get_github_org_members(org: str) -> List[Dict[str, str]]:
    """ Get all paged list of members from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/members"
    members = get_github_api_paged_data(url)
    return members


def get_github_org_teams(org: str) -> List[Dict[str, Any]]:
    """ Get all paged list of org teams from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/teams"
    teams = get_github_api_paged_data(url)
    return teams


def get_github_org_team_members(org: str, team: str) -> List[Dict[str, str]]:
    """ Get all paged list of team members from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/teams/{team}/members"
    members = get_github_api_paged_data(url)
    return members


def get_github_org_repositories(
    org: str,
) -> List[
    Dict[str, Union[int, str, bool, List[str], Dict[str, Union[str, int, bool]]]]
]:
    """ Get all paged list of repositories from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/repos"
    repositories = get_github_api_paged_data(url)
    return repositories


def get_github_org_team_repositories(
    org: str, team: str
) -> List[
    Dict[str, Union[int, str, bool, List[str], Dict[str, Union[str, int, bool]]]]
]:
    """ Get all paged list of team repositories from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/teams/{team}/repos"
    teams = get_github_api_paged_data(url)
    return teams


def get_github_org_repo_contributors(org: str, repo: str) -> List[Dict[str, str]]:
    """ Get users granted individual access to a given repository """
    url = f"{API_ROOT}/repos/{org}/{repo}/contributors"
    contributors = get_github_api_paged_data(url)
    return contributors


def get_member_logins(members: List[Dict[str, str]]) -> List[str]:
    """ Reduce a list of github member objects to a list of logins (usernames) """
    return [member["login"] for member in members]


class GithubApiError(Exception):
    """
    Create a wrapper to log an
    """

    def __init__(
        self, message: Union[str, TypeError] = "Incomplete audit error",
    ):
        self.message = message
        super().__init__(self.message)
        LOG.error({"error": "GithubApiError", "message": message})
