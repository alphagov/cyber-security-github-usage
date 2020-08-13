""" Parse messages from sns event """
import json
from typing import Any, Dict, List


def get_message_body(message: Dict[str, Any]) -> Any:
    """ Return json decoded message body from either SNS or SQS event model """
    if "body" in message:
        message_text = message.get("body", "")
    elif (
        "Sns" in message
        and message["Sns"]
        and "Message" in message["Sns"]
        and message["Sns"]["Message"]
    ):
        message_text = message["Sns"]["Message"]

    try:
        message_body = json.loads(message_text)
    except (json.JSONDecodeError):
        message_body = message_text

    return message_body


def parse_messages(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the escaped message body from each of the SQS messages in event.Records
    """
    use_default = False
    if "Records" in event:
        messages = [get_message_body(record) for record in event["Records"]]
    elif "body" in event:
        messages = [get_message_body(event)]
        if event["body"] == "":
            use_default = True
    else:
        use_default = True

    if use_default:
        default_message = {"action": "usage"}
        messages = [default_message]
    return messages
