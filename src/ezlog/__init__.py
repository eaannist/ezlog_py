"""
ezlog: simple, performant logging with ANSI colors (Python port of ezlog).
Install as ezlog-py from PyPI. Create log = EzLog() or EzLog(config).
Wires itself to stdlib logging. 6 levels: debug, info, success, warn, error, critical.
"""
from __future__ import annotations

from ezlog.defaults import (
    COLOR_CODES,
    DEFAULT_COLORS,
    DEFAULT_SYMBOLS_FALLBACK,
    DEFAULT_TIMESTAMP,
    DEFAULT_TIMESTAMP_COLOR,
    DEFAULT_TIMESTAMP_FORMAT,
    DEFAULT_TEXTS,
)
from ezlog.ezlog import EzLog
from ezlog.types import (
    ConsoleMethod,
    EzlogConfig,
    LevelConfig,
    LevelsConfig,
    LogArgs,
    LogColors,
    LogLevel,
    TimestampConfig,
    TimestampColor,
)

__all__ = [
    "EzLog",
    "LogLevel",
    "LogColors",
    "TimestampColor",
    "TimestampConfig",
    "EzlogConfig",
    "LevelsConfig",
    "LevelConfig",
    "LogArgs",
    "ConsoleMethod",
    "COLOR_CODES",
    "DEFAULT_SYMBOLS_FALLBACK",
    "DEFAULT_TEXTS",
    "DEFAULT_COLORS",
    "DEFAULT_TIMESTAMP",
    "DEFAULT_TIMESTAMP_FORMAT",
    "DEFAULT_TIMESTAMP_COLOR",
]


def main() -> None:
    """CLI entry point: EzLog() + short demo."""
    log_instance = EzLog()
    log_instance.success("Application started")
    log_instance.info("Environment: dev")
    log_instance.w("Warning message")
    log_instance.e("Error message")
    log_instance.d("Debug message")
    log_instance.info("User data:", {"id": 1, "name": "John"})
    log_instance.configure({"timestamp": False})
    log_instance.s("Done")
