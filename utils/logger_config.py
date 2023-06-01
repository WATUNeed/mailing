import logging
from logging.handlers import RotatingFileHandler

from settings import settings


def configurate_logging_file():
    logger = logging.getLogger("uvicorn")
    logger.setLevel(settings.FILE_LOGGING_LEVEL)
    handler = RotatingFileHandler(**settings.get_file_logging_class_attributes)
    formatter = logging.Formatter(**settings.get_file_logging_formatter_attributes)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
