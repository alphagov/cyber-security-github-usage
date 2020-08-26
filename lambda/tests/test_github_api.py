import json

import pytest
import requests_mock

from github_api import (
    get_github_org_members,
    get_member_logins,
    set_github_access_token,
)


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
    set_github_access_token(token)

    mocker = args["mocker"]
    for i, page in enumerate(
        [github_members_page_1, github_members_page_2, github_members_page_3], start=1
    ):
        mocker.get(
            f"https://api.github.com/orgs/{org}/members?page={i}",
            request_headers={"Authorization": f"token {token}"},
            text=page,
        )

    members = get_member_logins(get_github_org_members(org))

    assert "user-c" in members
    assert "user-j" in members
    assert "user-a" not in members


@pytest.mark.usefixtures("github_members_page_1")
def test_get_member_logins(github_members_page_1):
    members_response = json.loads(github_members_page_1)
    members = get_member_logins(members_response)
    assert len(members) == len(members_response)
    assert members[0] == members_response[0]["login"]
    assert "user-c" in members
