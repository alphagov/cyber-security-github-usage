import stubs
from github_usage import TOKEN_PREFIX, get_ssm_params, process_message


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
