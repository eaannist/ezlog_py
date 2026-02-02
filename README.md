# ezlog

Simple, performant logging with ANSI colors for Python.  
Published on PyPI as **ezlog-py** (import as `ezlog`).

- **5 levels**: `error`, `warn`, `info`, `success`, `debug` (no NOTSET/CRITICAL)
- **Short aliases**: `e`, `w`, `i`, `s`, `d`
- **ANSI colors**: red, yellow, cyan, green, magenta
- **Stdlib integration**: after `init()`, `logging.info()` etc. go through ezlog formatting
- **Zero dependencies**

## Install

```bash
pip install ezlog-py
```

## Usage

Import only ezlog, call **init** with the two settings, then use **ezlog.log** or stdlib **logging** (both go through ezlog):

```python
import ezlog

ezlog.init(use_colors=True, use_timestamp=True)

# Direct ezlog (includes .success() level)
ezlog.log.success("Application started")
ezlog.log.info("Environment: dev")
ezlog.log.w("Warning")
ezlog.log.e("Error")
ezlog.log.d("Debug")

# Stdlib logging (wired internally; same formatting)
import logging
logging.info("Hello from stdlib")
logging.error("Something failed", exc_info=True)
```

## init (two settings)

| Argument        | Default | Description     |
|----------------|--------|-----------------|
| `use_colors`   | `True` | ANSI colors     |
| `use_timestamp`| `True` | ISO timestamp   |

## Levels

Ezlog has 5 levels: **error**, **warn**, **info**, **success**, **debug**.  
Stdlib DEBUG/INFO/WARNING/ERROR are mapped to ezlog; NOTSET is skipped, CRITICAL is treated as error.

## Exports

- `init(use_colors=..., use_timestamp=...)` – initialize and wire to stdlib logging
- `log` – EzLog instance (set after `init()`); use for direct logging and `.success()`
- `EzLog` – logger class (for custom instances)
- Types: `LogLevel`, `LogColors`, `EzlogConfig`, `LevelsConfig`, `LevelConfig`, `LogArgs`, `ConsoleMethod`
