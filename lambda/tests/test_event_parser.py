import pytest

from event_parser import parse_messages


@pytest.mark.usefixtures("sns_message")
@pytest.mark.usefixtures("event_body")
def test_parse_messages_with_sns_message(sns_message, event_body):
    assert parse_messages(sns_message)[0] == event_body


@pytest.mark.usefixtures("http_event")
@pytest.mark.usefixtures("event_body")
def test_parse_messages_with_http_event(http_event, event_body):
    assert parse_messages(http_event)[0] == event_body
