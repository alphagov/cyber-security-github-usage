import json
from typing import Dict, List, Union

import pytest


@pytest.fixture()
def sns_message() -> Dict[str, List[Dict[str, Dict[str, str]]]]:
    """ Attach get_sns_event function to a pytest fixture """
    return get_sns_event()


@pytest.fixture()
def http_event() -> Dict[str, Union[str, bool, Dict[str, str]]]:
    """ Attach get_http_event function to a pytest fixture """
    return get_http_event()


@pytest.fixture()
def event_body() -> Dict[str, str]:
    """ Attach get_event_body to a pytest fixture """
    return get_event_body()


@pytest.fixture()
def github_members_page_1() -> str:
    return json.dumps(
        [
            {"login": "user-c"},
            {"login": "user-d"},
            {"login": "user-e"},
            {"login": "user-f"},
        ]
    )


@pytest.fixture()
def github_members_page_2() -> str:
    return json.dumps(
        [
            {"login": "user-g"},
            {"login": "user-h"},
            {"login": "user-i"},
            {"login": "user-j"},
        ]
    )


@pytest.fixture()
def github_members_page_3() -> str:
    return json.dumps([])


def get_event_body() -> Dict[str, str]:
    """ Create event body """
    return {"action": "usage"}


def get_http_event() -> Dict[str, Union[str, bool, Dict[str, str]]]:
    message = get_event_body()
    http_event: Dict[str, Union[str, bool, Dict[str, str]]] = {
        "httpMethod": "POST",
        "path": "/",
        "headers": {
            "accept-encoding": "identity",
            "connection": "close",
            "content-length": "694",
            "content-type": "application/json",
            "x-amzn-trace-id": "Root=1-1234",
            "x-forwarded-for": "1.2.3.4",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "body": json.dumps(message),
        "isBase64Encoded": False,
    }
    return http_event


def get_sns_event() -> Dict[str, List[Dict[str, Dict[str, str]]]]:
    """ Get an example event to be received by lambda via SNS """
    message = get_event_body()

    sns_event = {"Records": [{"Sns": {"Message": json.dumps(message)}}]}

    return sns_event


@pytest.fixture()
def sns_event() -> Dict[str, List[Dict[str, Dict[str, str]]]]:
    return get_sns_event()
