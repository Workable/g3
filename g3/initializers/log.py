import logging

from g3.config import log_config

levels = logging.getLevelNamesMapping()


def initialize() -> None:
    """
    Initializes the project's loggers.
    """
    logging.basicConfig()
    g3_logger = logging.getLogger("g3")
    g3_logger.setLevel(levels[log_config.level.upper()])
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.CRITICAL)
