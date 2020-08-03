import os
import time

import requests

import config
from logger import LOG

TOKEN_PREFIX = "/alert-processor/tokens/github/"
API_ROOT = "https://api.github.com"
ACCESS_TOKEN = None


def set_github_access_token(token):
    """ Get the access token once """
    global ACCESS_TOKEN
    ACCESS_TOKEN = token


def get_github_access_token():
    """ Get the access token once """
    global ACCESS_TOKEN
    if ACCESS_TOKEN is None:
        access_token_param = os.environ.get("GITHUB_TOKEN")
        ACCESS_TOKEN = config.get_ssm_param(access_token_param)
    return ACCESS_TOKEN


def get_github_api_paged_data(url: str) -> list:
    token = get_github_access_token()
    page = 1
    page_size = 100
    page_items = 1
    items = []
    while page_items > 0:
        page_items = 0
        page_url = f"{url}?page={page}&per_page={page_size}"
        headers = {"authorization": f"token {token}"}
        response = requests.get(page_url, headers=headers).json()
        if isinstance(response, list):
            LOG.debug("Got item page %s for URL %s", page, url)
            page_items = len(response)
            for item in response:
                items.append(item)
        else:
            LOG.error(response)
        page += 1
        time.sleep(4)

    return items


def get_github_org_members(org: str) -> list:
    """ Get all paged list of members from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/members"
    members = get_github_api_paged_data(url)
    return members


def get_github_org_teams(org: str) -> list:
    """ Get all paged list of org teams from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/teams"
    teams = get_github_api_paged_data(url)
    return teams


def get_github_org_team_members(org: str, team: str) -> list:
    """ Get all paged list of team members from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/teams/{team}/members"
    members = get_github_api_paged_data(url)
    return members


def get_github_org_repositories(org: str) -> list:
    """ Get all paged list of repositories from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/repos"
    repositories = get_github_api_paged_data(url)
    return repositories


def get_github_org_team_repositories(org: str, team: str) -> list:
    """ Get all paged list of team repositories from GitHub rest API """
    url = f"{API_ROOT}/orgs/{org}/teams/{team}/repos"
    teams = get_github_api_paged_data(url)
    return teams


def get_github_org_repo_contributors(org: str, repo: str) -> list:
    """ Get users granted individual access to a given repository """
    url = f"{API_ROOT}/repos/{org}/{repo}/contributors"
    contributors = get_github_api_paged_data(url)
    return contributors


def get_member_logins(members: list) -> list:
    """ Reduce a list of github member objects to a list of logins (usernames) """
    return [member["login"] for member in members]
