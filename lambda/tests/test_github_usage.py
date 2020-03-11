""" Test github_usage.py functions """
import os

import pytest
import requests_mock

import stubs
from github_usage import (
    TOKEN_PREFIX,
    get_github_org_members,
    get_ssm_params,
    process_message,
    usage,
)


def test_process_message():
    # should_succeed = [{"action": "register"},
    # {"action": "commit"}, {"action": "usage"}]
    should_succeed = [{"action": "commit"}]
    for message in should_succeed:
        assert process_message(message) is True


def test_get_ssm_params():
    """Test routing get_routing_options function"""
    stubber = stubs.mock_ssm_get_parameters_by_path()

    with stubber:
        ssm_params = get_ssm_params(TOKEN_PREFIX)
        assert ssm_params["user-a"] == "github-token-a"
        assert ssm_params["user-d"] == "github-token-d"

        stubber.deactivate()


@pytest.mark.usefixtures("github_members_page_1")
@pytest.mark.usefixtures("github_members_page_2")
@pytest.mark.usefixtures("github_members_page_3")
@requests_mock.Mocker(kw="mocker")
def test_get_github_org_members(
    github_members_page_1, github_members_page_2, github_members_page_3, **args
):
    """Test using request mocker."""
    org = "testorg"
    token = "abc123"

    mocker = args["mocker"]
    mocker.get(
        f"https://api.github.com/orgs/{org}/members?page=1",
        request_headers={"Authorization": f"token {token}"},
        text=github_members_page_1,
    )
    mocker.get(
        f"https://api.github.com/orgs/{org}/members?page=2",
        request_headers={"Authorization": f"token {token}"},
        text=github_members_page_2,
    )
    mocker.get(
        f"https://api.github.com/orgs/{org}/members?page=3",
        request_headers={"Authorization": f"token {token}"},
        text=github_members_page_3,
    )

    members = get_github_org_members(org, token)
    assert "user-c" in members
    assert "user-j" in members
    assert "user-a" not in members


@pytest.mark.usefixtures("github_members_page_1")
@pytest.mark.usefixtures("github_members_page_2")
@pytest.mark.usefixtures("github_members_page_3")
@requests_mock.Mocker(kw="mocker")
def test_usage(
    github_members_page_1, github_members_page_2, github_members_page_3, **args
):
    """ Test mocked delete ssm param """
    stubber = stubs.mock_ssm_usage()

    token_var = "/github/usage/pat"
    os.environ["GITHUB_TOKEN"] = token_var
    org = "testorg"
    os.environ["GITHUB_ORG"] = org

    with stubber:
        """Test using request mocker."""
        token = "abc123"

        mocker = args["mocker"]
        mocker.get(
            f"https://api.github.com/orgs/{org}/members?page=1",
            request_headers={"Authorization": f"token {token}"},
            text=github_members_page_1,
        )
        mocker.get(
            f"https://api.github.com/orgs/{org}/members?page=2",
            request_headers={"Authorization": f"token {token}"},
            text=github_members_page_2,
        )
        mocker.get(
            f"https://api.github.com/orgs/{org}/members?page=3",
            request_headers={"Authorization": f"token {token}"},
            text=github_members_page_3,
        )

        stats = usage()
        assert stats["removed"] == 2
        assert stats["members"] == 8
        assert stats["registered"] == 2

        stubber.deactivate()
