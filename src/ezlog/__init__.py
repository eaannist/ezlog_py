"""
ezlog: simple, performant logging with ANSI colors (Python port of ezlog).
Install as ezlog-py from PyPI. Import ezlog, call init(use_colors, use_timestamp),
then use ezlog.log or stdlib logging; both go through ezlog formatting.
5 levels: error, warn, info, success, debug (no NOTSET/CRITICAL).
"""
from __future__ import annotations

import logging

from ezlog.ezlog import EzLog, _EzLogHandler
from ezlog.types import (
    ConsoleMethod,
    EzlogConfig,
    LevelConfig,
    LevelsConfig,
    LogArgs,
    LogColors,
    LogLevel,
)

__all__ = [
    "EzLog",
    "init",
    "log",
    "LogLevel",
    "LogColors",
    "EzlogConfig",
    "LevelsConfig",
    "LevelConfig",
    "LogArgs",
    "ConsoleMethod",
]

# Set by init(); use ezlog.log after calling ezlog.init().
log: EzLog | None = None


def init(
    *,
    use_colors: bool = True,
    use_timestamp: bool = True,
) -> EzLog:
    """
    Initialize ezlog and wire it to stdlib logging. Call once at startup.
    After init(), use ezlog.log for direct logging (including .success()) or
    logging.info() / logger.error() etc.; all go through ezlog formatting.
    """
    global log
    log = EzLog({
        "useColors": use_colors,
        "useTimestamp": use_timestamp,
    })
    root = logging.getLogger()
    root.addHandler(_EzLogHandler(log))
    root.setLevel(logging.DEBUG)
    return log


def main() -> None:
    """CLI entry point: init + short demo."""
    init(use_colors=True, use_timestamp=True)
    assert log is not None
    log.success("Application started")
    log.info("Environment: dev")
    log.w("Warning message")
    log.e("Error message")
    log.d("Debug message")
    log.info("User data:", {"id": 1, "name": "John"})
    log.configure({"useTimestamp": False})
    log.s("Done")
