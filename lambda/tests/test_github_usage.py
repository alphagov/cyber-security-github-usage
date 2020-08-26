""" Test github_usage.py functions """
import os

import pytest
import requests_mock
import stubs

from github_api import set_github_access_token
from github_usage import process_message, usage


def test_process_message():
    # should_succeed = [{"action": "register"},
    # {"action": "commit"}, {"action": "usage"}]
    should_succeed = [{"action": "commit"}]
    for message in should_succeed:
        assert process_message(message) is True


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
    token = "abc123"
    set_github_access_token(token)

    with stubber:
        """Test using request mocker."""
        mocker = args["mocker"]
        for i, page in enumerate(
            [github_members_page_1, github_members_page_2, github_members_page_3],
            start=1,
        ):
            mocker.get(
                f"https://api.github.com/orgs/{org}/members?page={i}",
                request_headers={"Authorization": f"token {token}"},
                text=page,
            )

        stats = usage({"action": "usage"})
        assert stats["removed"] == 2
        assert stats["members"] == 8
        assert stats["registered"] == 2

        stubber.deactivate()
