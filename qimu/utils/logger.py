"""Logging setup for qimu."""

import logging
from pathlib import Path

from rich.logging import RichHandler


def setup_logging(
    verbose: bool = False, debug: bool = False, log_file: Path | None = None
) -> logging.Logger:
    """Set up logging for qimu.

    Args:
        verbose: Enable verbose logging (INFO level)
        debug: Enable debug logging (DEBUG level)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    # Determine log level
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Create logger
    logger = logging.getLogger("qimu")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Add rich handler for stderr
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=False,
        show_path=debug,  # Only show path in debug mode
    )
    console_handler.setLevel(level)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add file handler if log_file specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
