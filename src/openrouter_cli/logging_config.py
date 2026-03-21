"""Reusable logging configuration with colors."""

import logging
from typing import Literal

from rich.console import Console
from rich.logging import RichHandler

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LOG_FORMAT = "%(module)s.%(funcName)s: %(message)s"


def setup_logging(
    level: LogLevel = "INFO",
    *,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """Configure logging with colors and appropriate level.

    Args:
        level: Base log level (default: INFO)
        verbose: If True, set level to DEBUG (overrides level)
        quiet: If True, set level to WARNING (overrides level and verbose)
    """
    if quiet:
        effective_level = "WARNING"
    elif verbose:
        effective_level = "DEBUG"
    else:
        effective_level = level

    console = Console(stderr=True)
    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        log_time_format="[ %Y-%m-%d %H:%M:%S ]",
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logging.basicConfig(
        level=effective_level,
        handlers=[handler],
        force=True,
    )
