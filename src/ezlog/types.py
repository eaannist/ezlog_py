"""Type definitions for ezlog (mirrors ezlog TypeScript API)."""
from typing import Any, Callable, Literal, TypedDict

LogLevel = Literal["error", "warn", "info", "success", "debug"]
LogColors = Literal["red", "yellow", "cyan", "green", "magenta", "white"]


class LevelsConfig(TypedDict, total=False):
    """Per-level enable/disable."""

    error: bool
    warn: bool
    info: bool
    success: bool
    debug: bool


class EzlogConfig(TypedDict, total=False):
    """Logger configuration (partial for updates)."""

    levels: LevelsConfig
    useColors: bool
    useLevels: bool
    useSymbols: bool
    useTimestamp: bool


class LevelConfig(TypedDict):
    """Internal config per level: symbol, text, color, writer."""

    symbol: str
    text: str
    color: str
    consoleFn: Callable[..., None]


ConsoleMethod = Callable[..., None]
LogArgs = tuple[Any, ...]
