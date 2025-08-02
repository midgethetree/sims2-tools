"""Common utilities shared between SiMidge and SimTracker for handling error logging."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType


def config_logging(appname: str) -> None:
    """Configure the logging system."""
    if "APPDATA" in os.environ:
        statehome: Path = Path(os.environ["APPDATA"])
    elif "XDG_STATE_HOME" in os.environ:
        statehome = Path(os.environ["XDG_STATE_HOME"])
    else:
        statehome = Path(os.environ["HOME"]) / ".local/state"

    (statehome / appname).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        handlers=[
            RotatingFileHandler(
                Path(statehome) / appname / "error.log",
                delay=True,
                maxBytes=100000,
                backupCount=5,
            ),
        ],
        format="%(asctime)s %(name)s:%(funcName)s:%(lineno)d\n%(levelname)s %(message)s\n",
        level=logging.INFO,
    )

    sys.excepthook = handle_exception


def handle_exception(
    exception_type: type[BaseException],
    value: BaseException,
    tb: TracebackType | None,
) -> None:
    """Handle an exception by logging it.

    Args:
        exception_type: Type of exception.
        value: Exception.
        tb: Traceback.
    """
    if issubclass(exception_type, KeyboardInterrupt):
        sys.__excepthook__(exception_type, value, tb)
        return

    logging.error("Uncaught exception", exc_info=(exception_type, value, tb))
