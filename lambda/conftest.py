import json

import pytest


@pytest.fixture()
def sns_message():
    """ Attach get_sns_event function to a pytest fixture """
    return get_sns_event()


@pytest.fixture()
def http_event():
    """ Attach get_http_event function to a pytest fixture """
    return get_http_event()


@pytest.fixture()
def event_body():
    """ Attach get_event_body to a pytest fixture """
    return get_event_body()


@pytest.fixture()
def github_members_page_1():
    return json.dumps(
        [
            {"login": "user-c"},
            {"login": "user-d"},
            {"login": "user-e"},
            {"login": "user-f"},
        ]
    )


@pytest.fixture()
def github_members_page_2():
    return json.dumps(
        [
            {"login": "user-g"},
            {"login": "user-h"},
            {"login": "user-i"},
            {"login": "user-j"},
        ]
    )


@pytest.fixture()
def github_members_page_3():
    return json.dumps([])


# @pytest.fixture()
# def ssm_params():
#     """ Attach get_ssm_params function to a pytest fixture """
#     return get_ssm_params()


def get_event_body():
    """ Create event body """
    return {"action": "usage"}


def get_http_event():
    message = get_event_body()
    http_event = {
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


def get_sns_event():
    """ Get an example event to be received by lambda via SNS """
    message = get_event_body()

    sns_event = {"Records": [{"Sns": {"Message": json.dumps(message)}}]}

    return sns_event


# def get_ssm_params():
#     """ Mock ssm get-parameters-by-path response """
#     return {
#         "Parameters": [
#             {
#                 "Name": "/slack/channels/test-channel-1",
#                 "Value": "https://test.chann.el/1/webhook/url"
#             },
#             {
#                 "Name": "/slack/channels/test-channel-2",
#                 "Value": "https://test.chann.el/2/webhook/url"
#             }
#         ]
#     }
