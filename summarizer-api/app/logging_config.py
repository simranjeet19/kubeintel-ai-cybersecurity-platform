import logging
import sys

from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("kubeintel")
    logger.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logging()
