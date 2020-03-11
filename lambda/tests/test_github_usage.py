from github_usage import process_event


def test_process_event():
    # should_succeed = [{"action": "register"},
    # {"action": "commit"}, {"action": "usage"}]
    should_succeed = [{"action": "commit"}]
    for event in should_succeed:
        assert process_event(event) is True
