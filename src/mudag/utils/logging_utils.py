"""Module for logging configuration."""

import logging
import os
import sys
from typing import Optional


def setup_logger(
    log_level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file, or None to log to stderr only

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("mudag")

    # Set level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logger.setLevel(numeric_level)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
    )
    simple_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # Create file handler if a log file is specified
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger
