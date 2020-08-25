""" Declare a logger to be used by any module """
import datetime
import json
import logging
import os
import sys
from dataclasses import asdict, is_dataclass


class JsonFormatter(logging.Formatter):
    """ Handle log invokes with string, dict or json.dumps """

    def format(self, record: logging.LogRecord) -> str:
        """ Detect formatting of self message and encode as valid JSON """

        data = {}
        data.update(vars(record))

        # If the data['msg'] is valid JSON, convert it to python dict
        # so it can be embedded in output as a nested dict instead of
        # a JSON string.
        try:
            parsed = json.loads(data["msg"])
            data["msg"] = parsed
        except (TypeError, ValueError):
            pass

        # If data['msg'] is a dataclass convert it to a dict otherwise
        # JSON serialisation will fail.
        if is_dataclass(data["msg"]):
            data["msg"] = asdict(data["msg"])

        # If data['args'] is provided, use msg['data'] as a format
        # template and data['args'] as the variables. If the
        # number of template placeholders does not match the number of
        # args, this will fail.
        if ("args" in data) and len(data["args"]) > 0:
            try:
                data["msg"] = data["msg"] % tuple(data["args"])
            except TypeError:
                pass

        data["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return json.dumps(data)


def build_logger(log_name: str, log_level: str = "ERROR") -> logging.Logger:
    """ Create shared logger and custom JSON handler """
    logger = logging.getLogger(log_name)
    handler = logging.StreamHandler(sys.stdout)

    # //if isinstance(JsonFormatter, logging.Formatter):
    fmt = JsonFormatter()
    handler.setFormatter(fmt)

    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    return logger


LOG_LEVEL = str(os.getenv("LOG_LEVEL", "DEBUG"))
LOG = build_logger("github_usage", log_level=LOG_LEVEL)
