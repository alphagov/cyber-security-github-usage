import pytest
import requests_mock

import stubs
from github_usage import (
    TOKEN_PREFIX,
    get_github_org_members,
    get_ssm_params,
    process_message,
)


def test_process_message():
    # should_succeed = [{"action": "register"},
    # {"action": "commit"}, {"action": "usage"}]
    should_succeed = [{"action": "commit"}]
    for message in should_succeed:
        assert process_message(message) is True


def test_get_routing_options():
    """Test routing get_routing_options function"""
    stubber = stubs.mock_ssm()

    with stubber:
        ssm_params = get_ssm_params(TOKEN_PREFIX)
        assert ssm_params["user-a"] == "github-token-a"
        assert ssm_params["user-d"] == "github-token-d"

        stubber.deactivate()


@pytest.mark.usefixtures("github_members_page_1")
@pytest.mark.usefixtures("github_members_page_2")
@pytest.mark.usefixtures("github_members_page_3")
@requests_mock.Mocker(kw="mocker")
def test_send_to_splunk(
    github_members_page_1, github_members_page_2, github_members_page_3, **args
):
    """Test using request mocker."""
    org = "testorg"
    token = "abc123"
    # os.environ["GITHUB_ORG"] = org

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
