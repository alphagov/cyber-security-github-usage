""" Create mock boto3 clients for testing """

import boto3
from botocore.stub import Stubber


def _keep_it_real():
    """ Keep the native """
    if not getattr(boto3, "real_client", None):
        boto3.real_client = boto3.client


def mock_sts():
    _keep_it_real()
    client = boto3.real_client("sts")

    stubber = Stubber(client)

    # mock get_function response
    mock_caller_identity = {
        "UserId": "ABCDEFGHIJKLMNOPQRST:1234567890123456789",
        "Account": "123456789012",
        "Arn": "arn:aws:sts::123456789012:assumed-role/IamRoleName/1234567890123456789",
    }
    stubber.add_response("get_caller_identity", mock_caller_identity)

    stubber.activate()
    # override boto.client to return the mock client
    boto3.client = lambda service: client
    return stubber


def mock_ssm_get_parameters_by_path():
    _keep_it_real()
    client = boto3.real_client("ssm")

    stubber = Stubber(client)

    # mock get_function response
    mock_get_parameters_by_path_page_1 = {
        "Parameters": [
            {
                "Name": "/alert-processor/tokens/github/user-a",
                "Value": "github-token-a",
            },
            {
                "Name": "/alert-processor/tokens/github/user-b",
                "Value": "github-token-b",
            },
        ],
        "NextToken": "page-2",
    }

    stubber.add_response(
        "get_parameters_by_path",
        mock_get_parameters_by_path_page_1,
        {
            "Path": "/alert-processor/tokens/github/",
            "Recursive": True,
            "WithDecryption": True,
        },
    )

    mock_get_parameters_by_path_page_2 = {
        "Parameters": [
            {
                "Name": "/alert-processor/tokens/github/user-c",
                "Value": "github-token-c",
            },
            {
                "Name": "/alert-processor/tokens/github/user-d",
                "Value": "github-token-d",
            },
        ]
    }

    stubber.add_response(
        "get_parameters_by_path",
        mock_get_parameters_by_path_page_2,
        {
            "Path": "/alert-processor/tokens/github/",
            "Recursive": True,
            "WithDecryption": True,
            "NextToken": "page-2",
        },
    )

    stubber.activate()
    # override boto.client to return the mock client
    boto3.client = lambda service: client
    return stubber


def mock_ssm_usage():
    _keep_it_real()
    client = boto3.real_client("ssm")

    stubber = Stubber(client)
    get_parameter_response = {"Parameter": {"Value": "abc123"}}
    stubber.add_response(
        "get_parameter",
        get_parameter_response,
        {"Name": "/github/usage/pat", "WithDecryption": True},
    )

    # mock get_function response
    mock_get_parameters_by_path_page_1 = {
        "Parameters": [
            {
                "Name": "/alert-processor/tokens/github/user-a",
                "Value": "github-token-a",
            },
            {
                "Name": "/alert-processor/tokens/github/user-b",
                "Value": "github-token-b",
            },
        ],
        "NextToken": "page-2",
    }

    stubber.add_response(
        "get_parameters_by_path",
        mock_get_parameters_by_path_page_1,
        {
            "Path": "/alert-processor/tokens/github/",
            "Recursive": True,
            "WithDecryption": True,
        },
    )

    mock_get_parameters_by_path_page_2 = {
        "Parameters": [
            {
                "Name": "/alert-processor/tokens/github/user-c",
                "Value": "github-token-c",
            },
            {
                "Name": "/alert-processor/tokens/github/user-d",
                "Value": "github-token-d",
            },
        ]
    }

    stubber.add_response(
        "get_parameters_by_path",
        mock_get_parameters_by_path_page_2,
        {
            "Path": "/alert-processor/tokens/github/",
            "Recursive": True,
            "WithDecryption": True,
            "NextToken": "page-2",
        },
    )

    stubber.add_response(
        "delete_parameter", {}, {"Name": "/alert-processor/tokens/github/user-a"},
    )

    stubber.add_response(
        "delete_parameter", {}, {"Name": "/alert-processor/tokens/github/user-b"},
    )

    stubber.activate()
    # override boto.client to return the mock client
    boto3.client = lambda service: client
    return stubber
