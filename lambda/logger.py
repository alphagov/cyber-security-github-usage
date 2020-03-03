""" Declare a logger to be used by any module """
import os
import logging


LOG = logging.getLogger('github_usage')
STDERRLOGGER = logging.StreamHandler()
STDERRLOGGER.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
LOG.addHandler(STDERRLOGGER)
LOG.setLevel(getattr(logging, str(os.getenv('LOG_LEVEL', 'ERROR'))))