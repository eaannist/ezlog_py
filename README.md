# ezlog

Simple, performant logging with ANSI colors for Python.  
Published on PyPI as **ezlog-py**.

- **6 levels**: `debug`, `info`, `success`, `warn`, `error`, `critical`
- **Short aliases**: `d`, `i`, `s`, `w`, `e`, `c`
- **ANSI colors**: full palette
- **Stdlib integration**: creating an EzLog wires it to stdlib logging automatically
- **Zero dependencies**

## Install

```bash
pip install ezlog-py
```

## Usage

Create a logger; it wires itself to stdlib logging. Use `log.i()`, `log.success()`, and anywhere `logging.info()` / `logger.error()` also go through ezlog:

```python
from ezlog import EzLog

log = EzLog(use_colors=True, use_timestamp=True)

# Direct ezlog (includes .success() level)
log.success("Application started")
log.i("Hello")
log.w("Warning")
log.e("Error")
log.d("Debug")

# Stdlib logging (wired internally; same formatting)
import logging
logging.info("From stdlib")
logging.error("Failed", exc_info=True)
```

You can pass a config dict: `EzLog({"useColors": True, "timestamp": False})` or mix: `EzLog({"useColors": True}, use_timestamp=False)`.

## Configuration

Config is an `EzlogConfig` (partial updates supported):

- **useColors**, **useLevels**, **useSymbols** – booleans
- **timestamp** – `False` to disable, or `TimestampConfig`: **format** (str, e.g. `"%Y-%m-%d %H:%M:%S"`), **color** (`"as_levels"` to use level color, or any `LogColors`)
- **levels** – per-level config: each level is either a `LevelConfig` or `False` (to disable)

`LevelConfig` has **symbol**, **text**, **color** (no `consoleFn`; output target is fixed by ezlog). You can override defaults or disable a level:

```python
log = EzLog({
    "useColors": True,
    "levels": {
        "info": {"symbol": "I", "text": "Info", "color": "light-cyan"},
        "debug": False,
    },
})
```

Constants and defaults live in `ezlog.defaults` (`DEFAULT_SYMBOLS_FALLBACK`, `DEFAULT_TEXTS`, `DEFAULT_COLORS`, `COLOR_CODES`, etc.); types in `ezlog.types`.

## init (optional)

`ezlog.init(use_colors=..., use_timestamp=...)` creates an EzLog (wired to stdlib) and sets `ezlog.log`. Use it if you prefer `ezlog.log.i("...")` instead of keeping your own `log` variable.

## Levels

Ezlog has 6 levels (severity order): **debug**, **info**, **success**, **warn**, **error**, **critical**.  
Each has a default symbol and color (overridable). Stdlib DEBUG/INFO/WARNING/ERROR/CRITICAL map to ezlog; NOTSET is skipped.

## Color properties

When colors are enabled, the logger exposes: `log.red`, `log.yellow`, `log.cyan`, `log.green`, `log.magenta`, `log.white`, `log.gray`, `log.reset`. Use them for custom formatted messages (use `log.reset` after colored segments).

## Exports

- **EzLog**(config?, use_colors?, use_timestamp?) – create logger (wires to stdlib on construction)
- **init**(use_colors=..., use_timestamp=...) – optional; sets `ezlog.log`
- **log** – set by `init()`; use after `ezlog.init()`
- **Types**: `LogLevel`, `LogColors`, `TimestampColor`, `TimestampConfig`, `EzlogConfig`, `LevelsConfig`, `LevelConfig`, `LogArgs`, `ConsoleMethod`
- **Constants** (from `ezlog.defaults`): `COLOR_CODES`, `RESET`, `DEFAULT_SYMBOLS_FALLBACK`, `DEFAULT_TEXTS`, `DEFAULT_COLORS`, `DEFAULT_TIMESTAMP_FORMAT`, `DEFAULT_TIMESTAMP_COLOR`, `DEFAULT_TIMESTAMP`
