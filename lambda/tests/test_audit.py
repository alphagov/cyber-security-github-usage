import json
import os

import pytest

import audit
import stubs


@pytest.mark.usefixtures("event_body")
def test_create_sns_message(event_body):
    """ Create the message to publish to SNS """
    sns_message = audit.create_sns_message(event_body)
    message = json.loads(sns_message)
    assert message["lambda"] == json.dumps(event_body)


@pytest.mark.usefixtures("event_body")
def test_publish_alert(event_body):
    """ Publish alert message to SNS """
    sns_message = audit.create_sns_message(event_body)
    topic_arn = "arn:aws:sns:eu-west-2:123456789012:my-topic"
    sns_subject = "GitHub organization access audit"
    sns_message_id = "test123"
    os.environ["SNS_ARN"] = topic_arn

    stubber = stubs.mock_sns_publish(
        sns_message, topic_arn, sns_subject, sns_message_id
    )

    with stubber:
        response = audit.publish_alert(sns_message)
        assert response["MessageId"] == sns_message_id

        stubber.deactivate()


def test_make_audit_event():
    test_event = {"type": "Test", "org": "alphagov", "count": 12}

    event = audit.make_audit_event(type=test_event["type"])
    assert event.get("type") == test_event["type"]
    # Check the org key is present but None
    assert event.get("org", "default") is None
    event = audit.make_audit_event(type=test_event["type"], org=test_event["org"])
    assert event.get("type") == test_event["type"]
    assert event.get("org") == test_event["org"]
    # Check the repository key is present but None
    assert event.get("repository", "default") is None
    event = audit.make_audit_event(
        type=test_event["type"], org=test_event["org"], count=test_event["count"]
    )
    assert event.get("count") == 12
    assert event.get("member", "default") is None
