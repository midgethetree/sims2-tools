import logging
import sys
from pathlib import Path
from types import TracebackType


def config_logging() -> None:
    logging.basicConfig(
        filename=Path(__file__).parent.parent / "error.log",
        format="%(asctime)s %(name)s:%(funcName)s:%(lineno)d\n%(levelname)s %(message)s\n",
        level=logging.INFO,
    )

    sys.excepthook = handle_exception


def handle_exception(
    exception_type: type[BaseException],
    value: BaseException,
    tb: TracebackType | None,
) -> None:
    if issubclass(exception_type, KeyboardInterrupt):
        sys.__excepthook__(exception_type, value, tb)
        return

    logging.error("Uncaught exception", exc_info=(exception_type, value, tb))
