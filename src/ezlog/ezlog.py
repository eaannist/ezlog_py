"""
EzLog: simple, performant logging with ANSI colors.
Mirrors ezlog (TypeScript) API: 5 levels, short aliases, safe serialization.
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback
from datetime import datetime
from typing import Any, Callable

from ezlog.types import EzlogConfig, LevelConfig, LogLevel

# Compiled regex for stack line formatting (path:line:col).
_STACK_PATH_LINE_RE = re.compile(r"(\(?)([^\s()]+):(\d+):(\d+)(\)?)")
_STACK_FILE_RE = re.compile(r"^\s*File\s*")
_STACK_AT_RE = re.compile(r"^\s*at\s*")


def _safe_symbol(s: str, fallback: str = "?") -> str:
    """Use fallback if default encoding cannot encode s (e.g. Windows cp1252 and ✓)."""
    try:
        enc = getattr(sys.stdout, "encoding", None) or sys.getdefaultencoding()
        s.encode(enc)
        return s
    except (UnicodeEncodeError, AttributeError):
        return fallback


_DEFAULT_CONFIG: EzlogConfig = {
    "levels": {
        "error": True,
        "warn": True,
        "info": True,
        "success": True,
        "debug": True,
    },
    "useColors": True,
    "useLevels": True,
    "useSymbols": True,
    "useTimestamp": True,
}


def _merge_levels(
    base: dict[str, bool], override: dict[str, bool] | None
) -> dict[str, bool]:
    out = dict(base)
    if override:
        out.update(override)
    return out


class EzLog:
    """
    Simple, performant, type-safe logging with ANSI colors.
    Levels: error, warn, info, success, debug. Short aliases: e, w, i, s, d.
    """

    def __init__(self, config: EzlogConfig | None = None) -> None:
        cfg = config or {}
        self._config: EzlogConfig = {
            "levels": _merge_levels(
                _DEFAULT_CONFIG.get("levels", {}),  # type: ignore[arg-type]
                cfg.get("levels"),
            ),
            "useColors": cfg.get("useColors", _DEFAULT_CONFIG.get("useColors", True)),
            "useLevels": cfg.get("useLevels", _DEFAULT_CONFIG.get("useLevels", True)),
            "useSymbols": cfg.get("useSymbols", _DEFAULT_CONFIG.get("useSymbols", True)),
            "useTimestamp": cfg.get(
                "useTimestamp", _DEFAULT_CONFIG.get("useTimestamp", True)
            ),
        }
        self._colors = self._build_colors()
        self._level_config = self._build_level_config()

    def _build_colors(self) -> dict[str, str]:
        use = self._config.get("useColors", True)
        return {
            "red": "\x1b[31m" if use else "",
            "yellow": "\x1b[33m" if use else "",
            "cyan": "\x1b[36m" if use else "",
            "green": "\x1b[32m" if use else "",
            "magenta": "\x1b[35m" if use else "",
            "white": "\x1b[0m" if use else "",
        }

    def _build_level_config(self) -> dict[str, LevelConfig]:
        c = self._colors
        return {
            "error": {
                "symbol": "x",
                "text": "ERROR",
                "color": c["red"],
                "consoleFn": lambda s: print(s, file=sys.stderr),
            },
            "warn": {
                "symbol": "!",
                "text": "WARN",
                "color": c["yellow"],
                "consoleFn": lambda s: print(s, file=sys.stderr),
            },
            "info": {
                "symbol": "i",
                "text": "INFO",
                "color": c["cyan"],
                "consoleFn": lambda s: print(s),
            },
            "success": {
                "symbol": _safe_symbol("✓", "+"),
                "text": "SUCCESS",
                "color": c["green"],
                "consoleFn": lambda s: print(s),
            },
            "debug": {
                "symbol": "d",
                "text": "DEBUG",
                "color": c["magenta"],
                "consoleFn": lambda s: print(s),
            },
        }

    def configure(self, config: EzlogConfig) -> None:
        """Update configuration at runtime."""
        if "levels" in config and config["levels"]:
            self._config["levels"] = _merge_levels(
                self._config.get("levels") or {}, config["levels"]
            )
        for key in ("useColors", "useLevels", "useSymbols", "useTimestamp"):
            if key in config and config[key] is not None:
                self._config[key] = config[key]  # type: ignore[typeddict-unknown-key]
        if "useColors" in config:
            self._colors = self._build_colors()
            self._level_config = self._build_level_config()

    def get_config(self) -> EzlogConfig:
        """Return a copy of current config."""
        return {
            "levels": dict(self._config.get("levels") or {}),
            "useColors": self._config.get("useColors", True),
            "useLevels": self._config.get("useLevels", True),
            "useSymbols": self._config.get("useSymbols", True),
            "useTimestamp": self._config.get("useTimestamp", True),
        }

    def _get_timestamp(self, color: str) -> str:
        if not self._config.get("useTimestamp", True):
            return ""
        now = datetime.now().isoformat()[:19].replace("T", " ")
        return f"[{color}{now}{self._colors['white']}] "

    def _get_prefix(self, level: LogLevel) -> str:
        lc = self._level_config[level]
        display = lc["symbol"] if self._config.get("useSymbols", True) else lc["text"]
        ts = self._get_timestamp(lc["color"])
        if self._config.get("useLevels", True):
            return (
                f"{self._colors['white']}{ts}"
                f"[{lc['color']}{display}{self._colors['white']}] "
            )
        return f"{self._colors['white']}{ts}"

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
                    f"{self._colors['white']}{self._colors['red']}"
                    f"{trimmed}{self._colors['white']}"
                )
                continue
            cleaned = _STACK_FILE_RE.sub("  at ", trimmed)
            cleaned = _STACK_AT_RE.sub("  at ", cleaned)
            highlighted = _STACK_PATH_LINE_RE.sub(
                lambda m: f"{m.group(1)}{self._colors['cyan']}{m.group(2)}"
                f"{self._colors['white']}:{self._colors['magenta']}{m.group(3)}"
                f"{self._colors['white']}:{self._colors['magenta']}{m.group(4)}"
                f"{self._colors['white']}{m.group(5)}",
                cleaned,
            )
            out_lines.append(
                f"  {self._colors['magenta']}at{self._colors['white']} {highlighted}"
            )
        return "\n".join(out_lines)

    def _format_arg(self, arg: Any) -> str:
        if isinstance(arg, BaseException):
            parts = [
                f"{self._colors['red']}{type(arg).__name__}"
                f"{self._colors['white']}: {arg}"
            ]
            if getattr(arg, "code", None) is not None:
                parts.append(
                    f"{self._colors['cyan']}code{self._colors['white']}: {arg.code}"
                )
            if getattr(arg, "status_code", None) is not None:
                parts.append(
                    f"{self._colors['cyan']}statusCode{self._colors['white']}: "
                    f"{arg.status_code}"
                )
            if getattr(arg, "statusCode", None) is not None:
                parts.append(
                    f"{self._colors['cyan']}statusCode{self._colors['white']}: "
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
                    f"{self._colors['cyan']}cause{self._colors['white']}: {cstr}"
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
        return str(arg)

    def _format_args(self, *args: Any) -> str:
        return " ".join(self._format_arg(a) for a in args)

    def _log(self, level: LogLevel, *args: Any) -> None:
        levels = self._config.get("levels") or {}
        if not levels.get(level, True) or not args:
            return
        lc = self._level_config[level]
        msg = f"{self._get_prefix(level)}{self._format_args(*args)}"
        lc["consoleFn"](msg)

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

    @property
    def green(self) -> str:
        return self._colors["green"]

    @property
    def red(self) -> str:
        return self._colors["red"]

    @property
    def yellow(self) -> str:
        return self._colors["yellow"]

    @property
    def cyan(self) -> str:
        return self._colors["cyan"]

    @property
    def magenta(self) -> str:
        return self._colors["magenta"]

    @property
    def white(self) -> str:
        return self._colors["white"]


# --- create_error_handler (uses internal logger, not exported as "log") ---

_IS_PRODUCTION = os.environ.get("ENV", "").lower() == "production"

_log = EzLog(
    {
        "levels": {
            "error": True,
            "warn": True,
            "info": True,
            "success": True,
            "debug": not _IS_PRODUCTION,
        },
        "useColors": True,
        "useLevels": True,
        "useSymbols": True,
        "useTimestamp": True,
    }
)


def _default_is_http_error(err: Any) -> bool:
    """True if err has status_code or statusCode (common HTTP error pattern)."""
    return hasattr(err, "status_code") or hasattr(err, "statusCode")


def _default_status_code(err: Any) -> int:
    """Extract status code from error (status_code or statusCode)."""
    return getattr(err, "status_code", None) or getattr(err, "statusCode", 500)


def create_error_handler(
    *,
    is_http_error: Callable[[Any], bool] | None = None,
    get_method: Callable[[Any], str] | None = None,
    get_url: Callable[[Any], str] | None = None,
) -> Callable[[Any, Any], None]:
    """
    Create error handler for router on_error callback.
    Logs by level: 5xx -> error, 4xx -> warn, else -> info.
    """
    is_http = is_http_error or _default_is_http_error
    get_m = get_method or (
        lambda req: getattr(req, "method", getattr(req, "METHOD", "?"))
    )
    get_u = get_url or (
        lambda req: getattr(req, "url", getattr(req, "path", "?"))
    )

    def handler(err: Any, request: Any = None) -> None:
        if request is None:
            method, url = "?", "?"
        else:
            method, url = get_m(request), get_u(request)
        if is_http(err):
            code = _default_status_code(err)
            if code >= 500:
                _log.e(f"[{method}] {url} - {code}", err)
            elif code >= 400:
                _log.w(f"[{method}] {url} - {code}", err)
            else:
                _log.i(f"[{method}] {url} - {code}", err)
        else:
            _log.e(f"[{method}] {url} - Unhandled error", err)

    return handler
