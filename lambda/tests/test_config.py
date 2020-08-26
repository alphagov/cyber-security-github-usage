import stubs

from config import get_ssm_params
from github_usage import TOKEN_PREFIX


def test_get_ssm_params():
    """Test routing get_routing_options function"""
    stubber = stubs.mock_ssm_get_parameters_by_path()

    with stubber:
        ssm_params = get_ssm_params(TOKEN_PREFIX)
        assert ssm_params["user-a"] == "github-token-a"
        assert ssm_params["user-d"] == "github-token-d"

        stubber.deactivate()
