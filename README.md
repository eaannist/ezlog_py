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

log = EzLog()  # or EzLog({"useColors": True, "timestamp": False})

# Direct ezlog (includes .success() level)
log.success("Application started")
log.i("Hello")
log.w("Oops")
log.e("OMG")
log.d("hmmm..")

# Stdlib logging (wired internally; same formatting)
import logging
logging.info("From stdlib")
logging.error("Failed", exc_info=True)
```

## Configuration

```python
# Example: custom config (partial overrides)
log = EzLog({
    "useColors": True,
    "useLevels": True,
    "useSymbols": False,
    "textColor": "white",
    "bracesColor": "light-white",
    "stdlibLevel": "INFO",
    "timestamp": {
        "color": "white",
        "format": "%Y-%m-%d %H:%M:%S",
    },
    "levels": {
        "info": {"text": "Information"},
        "debug": isDevelopment, # disable debug in production
        "critical": False,      # or disable a level entirely
    },
})
```

Each option has a default and is optional.

- **useColors** : boolean – Enable ANSI colors. Default `True`.
- **useLevels** : boolean – Show level label/symbol in output. Default `True`.
- **useSymbols** : boolean – Use symbol for level (if `False`, use text label). Default `True`.
- **textColor** : `LogColors` – define text color (e.g. `"light-red"`, `"cyan"`). Default `white`.
- **bracesColor** : `LogColors` – define braces color (e.g. `"light-red"`, `"cyan"`). Default `light-white`.
- **timestamp** : `TimestampConfig` or `False` – Configure timestamp, or set to `False` to disable.
- **levels** : `LevelsConfig` – Keys: `debug`, `info`, `success`, `warn`, `error`, `critical`. Each value is a `LevelConfig` (partial override) or `False` to disable that level.
- **stdlibLevel** : `StdLevel` – Root stdlib logging threshold used by ezlog wiring. `StdLevel` accepts: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` (case-insensitive), ezlog level names (`"debug"`, `"warn"`, etc.), or a numeric stdlib level.

#### `LevelConfig`

- **color** : `LogColors` – Level color (e.g. `"light-red"`, `"cyan"`).
- **text** : str – Level label (e.g. `"INFO"`, `"Error"`).
- **symbol** : str – Level symbol; validated with a safe fallback when the system doesn’t support the character.

#### `TimestampConfig`

- **format** : str – strftime format (e.g. `"%Y-%m-%d %H:%M:%S"`). Default from `ezlog.defaults.DEFAULT_TIMESTAMP_FORMAT`.
- **color** : `LogColors` or `"as_levels"` – Timestamp color. `"as_levels"` uses the same color as the log level. Default `"as_levels"`.

## Module / contextual segments

You can create logger "views" with additional prefixed segments, useful to tag modules, subsystems, or request scopes, without reconfiguring the global logger:

```python
from ezlog import EzLog, add_segments

base_log = EzLog({"useColors": True, "timestamp": {"color": "as_levels"}})

# Per-module logger (LogicModule)
logic_log = base_log.with_segments([
    {"text": "LogicModule", "color": "as_levels"},
])

# Or using the helper function:
api_log = add_segments(base_log, [
    {"text": "API", "color": "as_levels"},
])

logic_log.i("message from logic module")
api_log.i("message from API layer")
```

Output example:

```text
[2026-03-12 11:36:28] [LogicModule] [i] message from logic module
[2026-03-12 11:36:29] [API] [i] message from API layer
```

Segments use the same color system as timestamps: `"color": "as_levels"` reuses the level color, or you can pass any `LogColors` value.

## Levels

- **Order (severity)**: `debug` → `info` → `success` → `warn` → `error` → `critical`.
- **Short aliases**: `d`, `i`, `s`, `w`, `e`, `c`.
- **Stdlib mapping**: `logging.DEBUG` → debug, `logging.INFO` → info, `logging.WARNING` → warn, `logging.ERROR` → error, `logging.CRITICAL` → critical. `NOTSET` is skipped.
- Default symbols and colors are in `ezlog.defaults` (`DEFAULT_TEXTS`, `DEFAULT_COLORS`, `DEFAULT_SYMBOLS_FALLBACK`).

### Runtime stdlib level control

You can control how much stdlib logging gets through ezlog:

```python
import logging
from ezlog import EzLog

log = EzLog({"stdlibLevel": "INFO"})  # suppress stdlib DEBUG by default
logging.debug("hidden (filtered by stdlibLevel=INFO)")
logging.info("visible (passes stdlibLevel=INFO)")

log.set_stdlib_debug(True)     # DEBUG
log.set_stdlib_debug(False)    # INFO

log.set_stdlib_level("ERROR")  # threshold by name
log.set_stdlib_level(logging.WARNING)  # threshold by numeric level
```

## Color properties

When **useColors** is enabled, the logger exposes: 
| Standard colors   | Light colors       |
|-------------------|--------------------|
| `log.red`         | `log.light_red`    |
| `log.yellow`      | `log.lyellow`      |
| `log.cyan`        | `log.lcyan`        |
| `log.green`       | `log.lgreen`       |
| `log.magenta`     | `log.lmagenta`     |
| `log.blue`        | `log.lblue`        |
| `log.white`       | `log.lwhite`       |
| `log.black`       |                    |
| `log.gray`        |                    |

Use them for custom formatted output; end colored segments with `log.reset`.

## Exports

- **EzLog**(config?) – Create logger (wires to stdlib on construction). Config optional: `EzLog()` or `EzLog({"useColors": True, "timestamp": False})`.
- **Types** – `LogLevel`, `LogColors`, `TimestampColor`, `TimestampConfig`, `SegmentConfig`, `EzlogConfig`, `LevelsConfig`, `LevelConfig`, `LogArgs`, `ConsoleMethod`.
- **Constants** (from `ezlog.defaults`) – `COLOR_CODES`, `RESET`, `DEFAULT_SYMBOLS_FALLBACK`, `DEFAULT_TEXTS`, `DEFAULT_COLORS`, `DEFAULT_TIMESTAMP_FORMAT`, `DEFAULT_TIMESTAMP_COLOR`, `DEFAULT_TIMESTAMP`.
