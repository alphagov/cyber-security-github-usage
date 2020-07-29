""" Run process notification offline to report user coverage """
import json
import os
import sys

from github_usage import process_message

if __name__ == "__main__":
    """ Get usage stats """
    if "AWS_ACCESS_KEY_ID" in os.environ:
        action = sys.argv[1] if len(sys.argv) > 1 else "usage"
        notification = {"action": action}
        response = process_message(notification)
        print(json.dumps(response, indent=2, default=str))
    else:
        print("Run with AWS credentials")
