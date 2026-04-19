"""Type definitions for ezlog (mirrors ezlog TypeScript API). Constants and defaults in defaults.py."""
from typing import Any, Callable, Literal, TypedDict, Union

# --- Level and color literals (all stdlib + success; NOTSET skipped) ---
LogLevel = Literal["debug", "info", "success", "warn", "error", "critical"]
LogColors = Literal[
    "reset",
    "white",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "gray",
    "red",
    "green",
    "light-red",
    "light-green",
    "light-yellow",
    "light-blue",
    "light-magenta",
    "light-cyan",
    "light-white",
]
TimestampColor = LogColors | Literal["as_levels"]
SegmentsColor = TimestampColor

StdLibLevelKey = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
StdLevel = Union[StdLibLevelKey, LogLevel, int]


class TimestampConfig(TypedDict, total=False):
    """Timestamp configuration. If missing, use defaults. Use timestamp: False to disable."""

    color: TimestampColor
    format: str


class SegmentConfig(TypedDict, total=False):
    """Additional prefix segment: text with optional color (or 'as_levels')."""

    text: str
    color: SegmentsColor


class LevelConfig(TypedDict):
    """Per-level config: symbol, text, color. consoleFn is injected by ezlog (not user-configurable)."""

    symbol: str
    text: str
    color: LogColors


class LevelsConfig(TypedDict, total=False):
    """Per-level enable/disable: LevelConfig or False to disable."""

    debug: Union[LevelConfig, Literal[False]]
    info: Union[LevelConfig, Literal[False]]
    success: Union[LevelConfig, Literal[False]]
    warn: Union[LevelConfig, Literal[False]]
    error: Union[LevelConfig, Literal[False]]
    critical: Union[LevelConfig, Literal[False]]


class EzlogConfig(TypedDict, total=False):
    """Logger configuration (partial for updates)."""

    useColors: bool
    useLevels: bool
    useSymbols: bool
    textColor: LogColors
    bracesColor: LogColors
    timestamp: Union[TimestampConfig, Literal[False]]
    levels: LevelsConfig
    stdlibLevel: StdLevel


ConsoleMethod = Callable[..., None]
LogArgs = tuple[Any, ...]
