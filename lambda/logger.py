""" Declare a logger to be used by any module """
import datetime
import json
import logging
import os
import sys


class JsonFormatter(logging.Formatter):
    """
    Handle log invokes with string, dict or json.dumps
    """

    def format(self) -> str:  # type: ignore
        """ Detect formatting of self message and encode as valid JSON """
        data = {}
        data.update(vars(self))
        try:
            json.loads(self.msg)  # type: ignore
            parsed = json.loads(self.msg)  # type: ignore
            if type(parsed) in [dict, list]:
                data["msg"] = parsed
        except (TypeError, ValueError):
            pass

        try:
            if ("args" in data) and len(data["args"]) > 0:
                args = data["args"]
                data["msg"] = data["msg"] % args
        except TypeError:
            pass

        data["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return json.dumps(data)


def build_logger(log_name: str, log_level: str = "ERROR") -> logging.Logger:
    """ Create shared logger and custom JSON handler """
    logger = logging.getLogger(log_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter)  # type: ignore
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level))
    return logger


LOG_LEVEL = str(os.getenv("LOG_LEVEL", "ERROR"))
LOG = build_logger("github_usage", log_level=LOG_LEVEL)
