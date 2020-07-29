import boto3
from botocore.exceptions import ClientError

from logger import LOG


def get_ssm_param(param: str) -> str:
    """ Get parameter by path and return value """
    try:
        client = boto3.client("ssm")
        response = client.get_parameter(Name=param, WithDecryption=True)
        if "Parameter" in response:
            value = response["Parameter"]["Value"]
        else:
            value = None
    except (ClientError, KeyError) as err:
        LOG.error("Failed to get SSM param: %s: %s", param, err)
        value = None
    return value


def get_ssm_params(path: str) -> dict:
    """ Get parameter by path and return value """
    try:
        has_next_page = True
        next_token = None
        params = {}
        while has_next_page:
            client = boto3.client("ssm")
            request = {"Path": path, "Recursive": True, "WithDecryption": True}
            if next_token:
                request["NextToken"] = next_token
            response = client.get_parameters_by_path(**request)

            # Iterate parameters in response and append to dictionary
            for param in response["Parameters"]:
                name = param["Name"].replace(path, "")
                params[name] = param["Value"]

            # Check for next page in results
            has_next_page = "NextToken" in response
            if has_next_page:
                next_token = response["NextToken"]
            else:
                next_token = None

    except ClientError as err:
        LOG.error("Failed to get SSM params on path: %s: %s", path, err)
        params = []
    return params


def set_ssm_param(param: str, value: str) -> bool:
    """ Write param to SSM and return success status """
    try:
        client = boto3.client("ssm")
        response = client.put_parameter(
            Name=param, Value=value, Type="SecureString", Overwrite=True
        )
        success = "Version" in response
    except ClientError as err:
        LOG.error("Failed to set SSM param: %s: %s", param, err)
        success = False
    return success


def delete_ssm_param(param: str) -> bool:
    """ Delete SSM parameter and return status """
    try:
        client = boto3.client("ssm")
        response = client.delete_parameter(Name=param)
        #  delete parameter returns an empty dict
        success = response == {}
    except ClientError as err:
        LOG.error("Failed to set SSM param: %s: %s", param, err)
        success = False
    return success
