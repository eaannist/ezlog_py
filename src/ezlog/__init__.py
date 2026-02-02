"""
ezlog: simple, performant logging with ANSI colors (Python port of ezlog).
Install as ezlog-py from PyPI; import as: from ezlog import EzLog, create_error_handler.
5 levels: error, warn, info, success, debug. Short aliases: e, w, i, s, d.
"""
from ezlog.ezlog import EzLog, create_error_handler
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
    """CLI entry point: short demo (users create their own EzLog())."""
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
    logger.success("Application started")
    logger.info("Environment: dev")
    logger.w("Warning message")
    logger.e("Error message")
    logger.d("Debug message")
    logger.info("User data:", {"id": 1, "name": "John"})
    logger.configure({"useTimestamp": False})
    logger.s("Done")
