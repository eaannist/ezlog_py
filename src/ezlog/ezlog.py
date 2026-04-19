"""
EzLog: simple, performant logging with ANSI colors.
All levels: debug, info, success, warn, error, critical (NOTSET skipped).
Wires itself to stdlib logging; constants in defaults.py, types in types.py.
"""
from __future__ import annotations

import json
import logging
import re
import sys
import traceback
from datetime import datetime
from typing import Any, Literal

from ezlog.defaults import (
    BRACES_COLOR_DEFAULT,
    COLOR_CODES,
    DEFAULT_COLORS,
    DEFAULT_SEGMENTS_COLOR,
    DEFAULT_SYMBOLS_FALLBACK,
    DEFAULT_STDLIB_LEVEL,
    DEFAULT_TIMESTAMP,
    DEFAULT_TIMESTAMP_FORMAT,
    DEFAULT_TEXTS,
    TEXT_COLOR_DEFAULT,
    USE_COLORS_DEFAULT,
    USE_LEVELS_DEFAULT,
    USE_SYMBOLS_DEFAULT,
)
from ezlog.types import (
    EzlogConfig,
    LevelConfig,
    LevelsConfig,
    LogLevel,
    StdLevel,
    SegmentConfig,
    TimestampConfig,
)

# Stdlib level -> ezlog level. NOTSET skipped.
_STDLIB_LEVEL_MAP = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warn",
    logging.ERROR: "error",
    logging.CRITICAL: "critical",
}

# Compiled regex for stack line formatting (path:line:col).
_STACK_PATH_LINE_RE = re.compile(r"(\(?)([^\s()]+):(\d+):(\d+)(\)?)")
_STACK_FILE_RE = re.compile(r"^\s*File\s*")
_STACK_AT_RE = re.compile(r"^\s*at\s*")

_LOG_LEVELS: tuple[LogLevel, ...] = (
    "debug",
    "info",
    "success",
    "warn",
    "error",
    "critical",
)

_STDLIB_LEVEL_NAME_MAP: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

_STD_LEVEL_FROM_EZLOG: dict[LogLevel, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "success": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _safe_symbol(s: str, fallback: str = "?") -> str:
    """Use fallback if default encoding cannot encode s (e.g. Windows cp1252 and ✓)."""
    try:
        enc = getattr(sys.stdout, "encoding", None) or sys.getdefaultencoding()
        s.encode(enc)
        return s
    except (UnicodeEncodeError, AttributeError):
        return fallback


def _get_default_levels() -> LevelsConfig:
    """Build LevelsConfig from DEFAULT_TEXTS, DEFAULT_COLORS, DEFAULT_SYMBOLS_FALLBACK."""
    return {
        level: {
            "symbol": DEFAULT_SYMBOLS_FALLBACK[level]["default"],
            "text": DEFAULT_TEXTS[level],
            "color": DEFAULT_COLORS[level],
        }
        for level in _LOG_LEVELS
    }


def _merge_levels(
    default_levels: LevelsConfig, user_levels: LevelsConfig | None
) -> LevelsConfig:
    """Merge default level config with user overrides. Level can be LevelConfig or False."""
    merged: LevelsConfig = {}
    for level in _LOG_LEVELS:
        if user_levels and level in user_levels and user_levels[level] is False:
            merged[level] = False
            continue
        base: LevelConfig | False = default_levels.get(level)
        override = (user_levels or {}).get(level) if user_levels else None
        if isinstance(base, dict) and base:
            level_cfg: LevelConfig = dict(base)
            if isinstance(override, dict) and override:
                level_cfg.update({k: v for k, v in override.items() if v is not None})
            merged[level] = level_cfg
        elif isinstance(override, dict) and override:
            merged[level] = dict(override)
    return merged


def _merge_timestamp(
    default_ts: TimestampConfig, user_ts: TimestampConfig | Literal[False] | None
) -> TimestampConfig | Literal[False]:
    """Merge default timestamp config with user override. False disables timestamp."""
    if user_ts is False:
        return False
    if not user_ts:
        return dict(default_ts)
    return {**default_ts, **{k: v for k, v in user_ts.items() if v is not None}}


class EzLog:
    def __init__(self, config: EzlogConfig | None = None) -> None:
        default_levels: LevelsConfig = _get_default_levels()
        cfg = dict(config) if config else {}
        self._config = {
            "levels": _merge_levels(default_levels, cfg.get("levels")),
            "useColors": cfg.get("useColors", USE_COLORS_DEFAULT),
            "useLevels": cfg.get("useLevels", USE_LEVELS_DEFAULT),
            "useSymbols": cfg.get("useSymbols", USE_SYMBOLS_DEFAULT),
            "textColor": cfg.get("textColor", TEXT_COLOR_DEFAULT),
            "bracesColor": cfg.get("bracesColor", BRACES_COLOR_DEFAULT),
            "timestamp": _merge_timestamp(
                DEFAULT_TIMESTAMP,
                cfg.get("timestamp") if "timestamp" in cfg else None,
            ),
            "stdlibLevel": cfg.get("stdlibLevel", DEFAULT_STDLIB_LEVEL),
        }
        self._colors = self._build_colors()
        self._level_config: dict[str, dict[str, Any]] = self._build_level_config()
        _wire_to_stdlib(self, self._resolve_stdlib_level(self._config.get("stdlibLevel", DEFAULT_STDLIB_LEVEL)))

    def _build_colors(self) -> dict[str, str]:
        use = self._config.get("useColors", True)
        return {
            **({k: (v if use else "") for k, v in COLOR_CODES.items()}),
        }

    def _build_level_config(self) -> dict[str, dict[str, Any]]:
        levels = self._config.get("levels") or {}
        out: dict[str, dict[str, Any]] = {}
        _stderr = lambda s: print(s, file=sys.stderr)
        _stdout = lambda s: print(s)
        for level in _LOG_LEVELS:
            lc = levels.get(level)
            if lc is False:
                continue
            if not isinstance(lc, dict):
                continue
            color_name = lc.get("color", DEFAULT_COLORS.get(level, "white"))
            color_code = self._colors.get(color_name, self._colors["reset"])
            text = lc.get("text", DEFAULT_TEXTS.get(level, level))
            raw_symbol = lc.get(
                "symbol",
                DEFAULT_SYMBOLS_FALLBACK.get(level, {}).get("default", "?"),
            )
            fallback = DEFAULT_SYMBOLS_FALLBACK.get(level, {}).get("fallback", "?")
            symbol = _safe_symbol(raw_symbol or fallback, fallback)
            out[level] = {
                "symbol": symbol,
                "text": text,
                "color": color_code,
                "consoleFn": _stderr if level in ("error", "warn", "critical") else _stdout,
            }
        return out

    def configure(self, config: EzlogConfig) -> None:
        """Update configuration at runtime."""
        if "levels" in config and config["levels"]:
            self._config["levels"] = _merge_levels(
                self._config.get("levels") or {}, config["levels"]
            )
        if "timestamp" in config:
            self._config["timestamp"] = _merge_timestamp(
                self._config.get("timestamp") or DEFAULT_TIMESTAMP,
                config["timestamp"],
            )
        for key in ("useColors", "useLevels", "useSymbols", "textColor", "bracesColor"):
            if key in config and config[key] is not None:
                self._config[key] = config[key]  # type: ignore[typeddict-unknown-key]
        if "stdlibLevel" in config and config["stdlibLevel"] is not None:
            self.set_stdlib_level(config["stdlibLevel"])
        if "useColors" in config or "levels" in config:
            self._colors = self._build_colors()
            self._level_config = self._build_level_config()

    def get_config(self) -> EzlogConfig:
        """Return a copy of current config."""
        ts = self._config.get("timestamp")
        return {
            "levels": dict(self._config.get("levels") or {}),
            "useColors": self._config.get("useColors", True),
            "useLevels": self._config.get("useLevels", True),
            "useSymbols": self._config.get("useSymbols", True),
            "textColor": self._config.get("textColor", "white"),
            "bracesColor": self._config.get("bracesColor", "light-white"),
            "timestamp": False if ts is False else dict(ts or {}),
            "stdlibLevel": self._config.get("stdlibLevel", DEFAULT_STDLIB_LEVEL),
        }

    def _resolve_stdlib_level(self, level: StdLevel) -> int:
        """Normalize stdlib level from int, stdlib name, or ezlog level name."""
        if isinstance(level, int):
            if level in _STDLIB_LEVEL_MAP:
                return level
            raise ValueError(f"Invalid stdlib numeric level: {level}")
        normalized = level.strip().upper()
        if normalized in _STDLIB_LEVEL_NAME_MAP:
            return _STDLIB_LEVEL_NAME_MAP[normalized]
        lowered = level.strip().lower()
        if lowered in _STD_LEVEL_FROM_EZLOG:
            return _STD_LEVEL_FROM_EZLOG[lowered]  # type: ignore[index]
        raise ValueError(f"Invalid stdlib level: {level}")

    def set_stdlib_level(self, level: StdLevel) -> None:
        """Set root stdlib logging level while keeping ezlog wire active."""
        numeric_level = self._resolve_stdlib_level(level)
        if isinstance(level, str):
            self._config["stdlibLevel"] = level.upper()
        else:
            self._config["stdlibLevel"] = level
        _wire_to_stdlib(self, numeric_level)

    def set_stdlib_debug(self, enabled: bool) -> None:
        """Shortcut: DEBUG when enabled, INFO when disabled."""
        self.set_stdlib_level(logging.DEBUG if enabled else logging.INFO)

    def _get_timestamp(self, level: LogLevel) -> str:
        if self._config.get("timestamp") is False:
            return ""
        ts_cfg = self._config.get("timestamp") or {}
        fmt = ts_cfg.get("format", DEFAULT_TIMESTAMP_FORMAT)
        color_key = ts_cfg.get("color", "as_levels")
        if color_key == "as_levels":
            color_code = self._level_config[level]["color"]
        else:
            color_code = self._colors.get(color_key, self._colors["reset"])
        now_str = datetime.now().strftime(fmt)
        braces_name = self._config.get("bracesColor", "light-white")
        braces_code = self._colors.get(braces_name, self._colors["reset"])
        return (
            f"{braces_code}[{color_code}{now_str}{self._colors['reset']}"
            f"{braces_code}]{self._colors['reset']} "
        )

    def _format_segments(
        self, level: LogLevel, segments: list[SegmentConfig] | None
    ) -> str:
        if not segments:
            return ""
        lc = self._level_config[level]
        base_color = lc["color"]
        braces_name = self._config.get("bracesColor", "light-white")
        braces_code = self._colors.get(braces_name, self._colors["reset"])
        parts: list[str] = []
        for seg in segments:
            text = seg.get("text")
            if not text:
                continue
            color_key = seg.get("color", DEFAULT_SEGMENTS_COLOR)
            if color_key == "as_levels":
                color_code = base_color
            else:
                color_code = self._colors.get(color_key, self._colors["reset"])
            parts.append(
                f"{braces_code}[{color_code}{text}{self._colors['reset']}"
                f"{braces_code}]{self._colors['reset']} "
            )
        return "".join(parts)

    def _get_prefix(
        self, level: LogLevel, segments: list[SegmentConfig] | None = None
    ) -> str:
        lc = self._level_config[level]
        display = lc["symbol"] if self._config.get("useSymbols", True) else lc["text"]
        ts = self._get_timestamp(level)
        segs = self._format_segments(level, segments)
        braces_name = self._config.get("bracesColor", "light-white")
        braces_code = self._colors.get(braces_name, self._colors["reset"])
        if self._config.get("useLevels", True):
            return (
                f"{self._colors['reset']}{ts}{segs}"
                f"{braces_code}[{lc['color']}{display}{self._colors['reset']}"
                f"{braces_code}]{self._colors['reset']} "
            )
        return f"{self._colors['reset']}{ts}{segs}"

    def _safe_stringify(self, obj: Any, space: int | None = None) -> str:
        try:
            cloned = self._safe_clone_for_logging(obj)
            return json.dumps(cloned, indent=space, default=str)
        except (TypeError, ValueError, RecursionError):
            return "[Non-serializable object]"

    def _safe_clone_for_logging(
        self, obj: Any, depth: int = 0, seen: set[int] | None = None
    ) -> Any:
        if depth > 10:
            return "[Max Depth Reached]"
        seen = seen or set()
        if obj is None:
            return obj
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseException):
            return {
                "name": type(obj).__name__,
                "message": str(obj),
                "stack": (
                    str(obj.__traceback__)
                    if getattr(obj, "__traceback__", None)
                    else None
                ),
            }
        if isinstance(obj, list):
            if id(obj) in seen:
                return "[Circular Reference]"
            seen.add(id(obj))
            try:
                return [self._safe_clone_for_logging(x, depth + 1, seen) for x in obj]
            finally:
                seen.discard(id(obj))
        if isinstance(obj, dict):
            if id(obj) in seen:
                return "[Circular Reference]"
            seen.add(id(obj))
            out: dict[str, Any] = {}
            try:
                for k, v in obj.items():
                    try:
                        out[k] = self._safe_clone_for_logging(v, depth + 1, seen)
                    except RecursionError:
                        out[k] = "[Circular Reference]"
                return out
            finally:
                seen.discard(id(obj))
        return obj

    def _format_stack(self, stack: str) -> str:
        if not stack:
            return ""
        lines = stack.strip().split("\n")
        out_lines = []
        for i, line in enumerate(lines):
            trimmed = line.strip()
            if i == 0:
                out_lines.append(
                    f"{self._colors['reset']}{self._colors['light-red']}"
                    f"{trimmed}{self._colors['reset']}"
                )
                continue
            cleaned = _STACK_FILE_RE.sub("  at ", trimmed)
            cleaned = _STACK_AT_RE.sub("  at ", cleaned)
            highlighted = _STACK_PATH_LINE_RE.sub(
                lambda m: f"{m.group(1)}{self._colors['cyan']}{m.group(2)}"
                f"{self._colors['reset']}:{self._colors['magenta']}{m.group(3)}"
                f"{self._colors['reset']}:{self._colors['magenta']}{m.group(4)}"
                f"{self._colors['reset']}{m.group(5)}",
                cleaned,
            )
            out_lines.append(
                f"  {self._colors['magenta']}at{self._colors['reset']} {highlighted}"
            )
        return "\n".join(out_lines)

    def _format_arg(self, arg: Any) -> str:
        if isinstance(arg, BaseException):
            parts = [
                f"{self._colors['light-red']}{type(arg).__name__}"
                f"{self._colors['reset']}: {arg}"
            ]
            if getattr(arg, "code", None) is not None:
                parts.append(
                    f"{self._colors['cyan']}code{self._colors['reset']}: {arg.code}"
                )
            if getattr(arg, "status_code", None) is not None:
                parts.append(
                    f"{self._colors['cyan']}statusCode{self._colors['reset']}: "
                    f"{arg.status_code}"
                )
            if getattr(arg, "statusCode", None) is not None:
                parts.append(
                    f"{self._colors['cyan']}statusCode{self._colors['reset']}: "
                    f"{arg.statusCode}"
                )
            cause = getattr(arg, "__cause__", None)
            if cause is not None:
                cstr = (
                    f"{type(cause).__name__}: {cause}"
                    if isinstance(cause, BaseException)
                    else str(cause)
                )
                parts.append(
                    f"{self._colors['cyan']}cause{self._colors['reset']}: {cstr}"
                )
            tb = getattr(arg, "__traceback__", None)
            if tb is not None:
                parts.append(
                    self._format_stack("".join(traceback.format_tb(tb)))
                )
            return "\n".join(parts) + "\n"
        if isinstance(arg, (dict, list)):
            try:
                safe = self._safe_clone_for_logging(arg)
                return self._safe_stringify(safe, 2) + "\n"
            except (TypeError, ValueError, RecursionError):
                return "[Non-serializable object]\n"
        text = str(arg)
        if not text:
            return text
        text_color_name = self._config.get("textColor", "white")
        text_color_code = self._colors.get(text_color_name, self._colors["reset"])
        return f"{text_color_code}{text}{self._colors['reset']}"

    def _format_args(self, *args: Any) -> str:
        return " ".join(self._format_arg(a) for a in args)

    def _log_with_segments(
        self, level: LogLevel, segments: list[SegmentConfig] | None, *args: Any
    ) -> None:
        levels = self._config.get("levels") or {}
        if levels.get(level) is False or not args:
            return
        lc = self._level_config.get(level)
        if not lc:
            return
        msg = f"{self._get_prefix(level, segments)}{self._format_args(*args)}"
        lc["consoleFn"](msg)

    def _log(self, level: LogLevel, *args: Any) -> None:
        self._log_with_segments(level, None, *args)

    def error(self, *args: Any) -> None:
        self._log("error", *args)

    def e(self, *args: Any) -> None:
        self._log("error", *args)

    def warn(self, *args: Any) -> None:
        self._log("warn", *args)

    def w(self, *args: Any) -> None:
        self._log("warn", *args)

    def info(self, *args: Any) -> None:
        self._log("info", *args)

    def i(self, *args: Any) -> None:
        self._log("info", *args)

    def success(self, *args: Any) -> None:
        self._log("success", *args)

    def s(self, *args: Any) -> None:
        self._log("success", *args)

    def debug(self, *args: Any) -> None:
        self._log("debug", *args)

    def d(self, *args: Any) -> None:
        self._log("debug", *args)

    def critical(self, *args: Any) -> None:
        self._log("critical", *args)

    def c(self, *args: Any) -> None:
        self._log("critical", *args)

    def with_segments(self, segments: list[SegmentConfig]) -> "_SegmentedEzLog":
        """Return a logger view that always logs with the given additional segments."""
        return _SegmentedEzLog(self, list(segments))

    @property
    def reset(self) -> str:
        return self._colors["reset"]

    @property
    def black(self) -> str:
        return self._colors["black"]

    @property
    def white(self) -> str:
        return self._colors["white"]

    @property
    def yellow(self) -> str:
        return self._colors["yellow"]

    @property
    def blue(self) -> str:
        return self._colors["blue"]

    @property
    def magenta(self) -> str:
        return self._colors["magenta"]

    @property
    def cyan(self) -> str:
        return self._colors["cyan"]

    @property
    def gray(self) -> str:
        return self._colors["gray"]

    @property
    def red(self) -> str:
        return self._colors["red"]

    @property
    def green(self) -> str:
        return self._colors["green"]

    @property
    def light_red(self) -> str:
        return self._colors["light-red"]

    @property
    def lgreen(self) -> str:
        return self._colors["light-green"]

    @property
    def lyellow(self) -> str:
        return self._colors["light-yellow"]

    @property
    def lblue(self) -> str:
        return self._colors["light-blue"]

    @property
    def lmagenta(self) -> str:
        return self._colors["light-magenta"]

    @property
    def lcyan(self) -> str:
        return self._colors["light-cyan"]

    @property
    def lwhite(self) -> str:
        return self._colors["light-white"]


class _EzLogHandler(logging.Handler):
    """Forwards stdlib LogRecords to EzLog."""

    def __init__(self, ezlog: EzLog) -> None:
        super().__init__()
        self._ezlog = ezlog

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno == logging.NOTSET:
            return
        level_name = _STDLIB_LEVEL_MAP.get(record.levelno)
        if level_name is None:
            level_name = "error"  # unknown levelno -> error
        try:
            msg = self.format(record)
            if record.exc_info and record.exc_info[1] is not None:
                self._ezlog._log(level_name, msg, record.exc_info[1])
            else:
                self._ezlog._log(level_name, msg)
        except Exception:  # noqa: BLE001
            self.handleError(record)


def _wire_to_stdlib(ezlog_instance: EzLog, stdlib_level: int = logging.DEBUG) -> None:
    """Register this EzLog as the handler for stdlib root logger (replaces any previous)."""
    root = logging.getLogger()
    for handler in list(root.handlers):
        if type(handler).__name__ == "_EzLogHandler":
            root.removeHandler(handler)
    root.addHandler(_EzLogHandler(ezlog_instance))
    root.setLevel(stdlib_level)


class _SegmentedEzLog:
    """Lightweight view over EzLog that always logs with additional segments."""

    def __init__(self, base: EzLog, segments: list[SegmentConfig]) -> None:
        self._base = base
        self._segments = segments

    def _log(self, level: LogLevel, *args: Any) -> None:
        self._base._log_with_segments(level, self._segments, *args)

    def debug(self, *args: Any) -> None:
        self._log("debug", *args)

    def info(self, *args: Any) -> None:
        self._log("info", *args)

    def success(self, *args: Any) -> None:
        self._log("success", *args)

    def warn(self, *args: Any) -> None:
        self._log("warn", *args)

    def error(self, *args: Any) -> None:
        self._log("error", *args)

    def critical(self, *args: Any) -> None:
        self._log("critical", *args)

    # Short aliases
    def d(self, *args: Any) -> None:
        self._log("debug", *args)

    def i(self, *args: Any) -> None:
        self._log("info", *args)

    def s(self, *args: Any) -> None:
        self._log("success", *args)

    def w(self, *args: Any) -> None:
        self._log("warn", *args)

    def e(self, *args: Any) -> None:
        self._log("error", *args)

    def c(self, *args: Any) -> None:
        self._log("critical", *args)

    def with_segments(self, segments: list[SegmentConfig]) -> "_SegmentedEzLog":
        """Chain more segments on top of this view."""
        return _SegmentedEzLog(self._base, self._segments + list(segments))

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the base EzLog instance."""
        return getattr(self._base, name)


def add_segments(base_log: EzLog, segments: list[SegmentConfig]) -> _SegmentedEzLog:
    """Return a logger view that always logs with the given additional segments."""
    return base_log.with_segments(segments)
