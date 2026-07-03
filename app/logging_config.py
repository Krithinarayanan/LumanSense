"""Logging configuration module for the LumanSense system.

This module provides utility functions to configure standard logging formatters,
console stream handlers, and file redirection handlers.
"""

import logging


def setup_logging(log_file: str = "luman_sense.log") -> None:
    """Sets up the global logging configuration to output to console and a file.

    Args:
        log_file: Path to the log file where messages will be appended.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
