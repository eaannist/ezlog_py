"""Default constants and values for ezlog. Types live in types.py."""

# --- ANSI ---

from ezlog.types import TimestampColor

COLOR_CODES: dict[str, str] = {
    "reset": "\x1b[0m",
    "black": "\x1b[30m",
    "white": "\x1b[37m",
    "yellow": "\x1b[33m",
    "green": "\x1b[32m",
    "cyan": "\x1b[36m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "red": "\x1b[31m",
    "gray": "\x1b[90m",
    "light-white": "\x1b[97m",
    "light-yellow": "\x1b[93m",
    "light-green": "\x1b[92m",
    "light-cyan": "\x1b[96m",
    "light-blue": "\x1b[94m",
    "light-magenta": "\x1b[95m",
    "light-red": "\x1b[91m",
}

# --- Per-level symbol: default (preferred) and fallback (encoding-safe) ---
DEFAULT_SYMBOLS_FALLBACK: dict[str, dict[str, str]] = {
    "success": {"default": "✓", "fallback": "o"},
    "error": {"default": "×", "fallback": "x"},
    "warn": {"default": "!", "fallback": "!"},
    "critical": {"default": "!", "fallback": "!"},
    "debug": {"default": "d", "fallback": "d"},
    "info": {"default": "i", "fallback": "i"},
}

# --- Per-level default label text ---
DEFAULT_TEXTS: dict[str, str] = {
    "debug": "DEBUG",
    "info": "INFO",
    "success": "SUCCESS",
    "warn": "WARNING",
    "error": "ERROR",
    "critical": "CRITICAL",
}

# --- Per-level default color name (key of COLOR_CODES) ---
DEFAULT_COLORS: dict[str, str] = {
    "debug": "light-magenta",
    "info": "cyan",
    "success": "light-green",
    "warn": "light-yellow",
    "error": "red",
    "critical": "light-red",
}

# --- Timestamp: format and color ("as_levels" = use level color) ---
DEFAULT_TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S"
DEFAULT_TIMESTAMP_COLOR: TimestampColor = "gray"
DEFAULT_TIMESTAMP: dict[str, str] = {
    "format": DEFAULT_TIMESTAMP_FORMAT,
    "color": DEFAULT_TIMESTAMP_COLOR,
}

# --- Global config defaults ---
USE_COLORS_DEFAULT = True
USE_LEVELS_DEFAULT = True
USE_SYMBOLS_DEFAULT = True
TEXT_COLOR_DEFAULT = "white"
BRACES_COLOR_DEFAULT = "gray"
DEFAULT_SEGMENTS_COLOR = "white"
DEFAULT_STDLIB_LEVEL = "DEBUG"