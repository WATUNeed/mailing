import logging
from logging.handlers import RotatingFileHandler
from typing import Any

import uvicorn

from settings import settings


def configurate_logging_file():
    """
    Configures the logger to log file.
    :return:
    """
    file_logger = logging.getLogger("uvicorn")
    file_logger.setLevel(settings.FILE_LOGGING_LEVEL)
    handler = RotatingFileHandler(**settings.get_file_logging_class_attributes)
    formatter = logging.Formatter(**settings.get_file_logging_formatter_attributes)
    handler.setFormatter(formatter)
    file_logger.addHandler(handler)


def configurate_logging_uvicorn_console() -> dict[str, Any]:
    """
    Configures uvicorn console logging.
    :return:
    """
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = settings.LOGGING_FORMAT
    log_config["formatters"]["access"]["datefmt"] = settings.LOGGING_DATEFMT
    log_config["formatters"]["default"]["fmt"] = settings.LOGGING_FORMAT
    log_config["formatters"]["default"]["datefmt"] = settings.LOGGING_DATEFMT
    return log_config
