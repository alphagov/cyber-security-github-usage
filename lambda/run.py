""" Run process notification offline to report user coverage """
import json

from github_usage import process_notification


if __name__ == "__main__":
    """ Register a test user """
    notification = {
        "action": "usage"
    }
    response = process_notification(notification)
    print(json.dumps(response, indent=2, default=str))
