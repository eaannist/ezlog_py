"""
ezlog_py: simple, performant logging with ANSI colors (Python port of ezlog).
5 levels: error, warn, info, success, debug. Short aliases: e, w, i, s, d.
"""
from ezlog_py.config.logger import create_error_handler, log
from ezlog_py.ezlog import EzLog
from ezlog_py.types import (
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
    "log",
    "create_error_handler",
    "LogLevel",
    "LogColors",
    "EzlogConfig",
    "LevelsConfig",
    "LevelConfig",
    "LogArgs",
    "ConsoleMethod",
]


def main() -> None:
    """CLI entry point: runs a short demo of ezlog_py."""
    log.success("Application started")
    log.info("Environment: dev")
    log.w("Warning message")
    log.e("Error message")
    log.d("Debug message")
    logger = EzLog(
        {
            "levels": {
                "error": True,
                "warn": True,
                "info": True,
                "success": True,
                "debug": False,
            },
            "useColors": True,
            "useLevels": True,
            "useSymbols": False,
            "useTimestamp": True,
        }
    )
    logger.info("User data:", {"id": 1, "name": "John"})
    logger.configure({"useTimestamp": False})
    logger.s("Done")
