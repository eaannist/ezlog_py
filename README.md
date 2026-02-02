# ezlog (Python)

Simple, performant logging with ANSI colors for Python.  
Published on PyPI as **ezlog-py** (import as `ezlog`).

- **5 levels**: `error`, `warn`, `info`, `success`, `debug`
- **Short aliases**: `e`, `w`, `i`, `s`, `d`
- **ANSI colors**: red, yellow, cyan, green, magenta
- **Config**: levels on/off, colors, symbols vs text, timestamp
- **Safe serialization**: circular refs, dates, exceptions
- **Zero dependencies**

## Install

```bash
pip install ezlog-py
```

## Usage

```python
from ezlog import EzLog, create_error_handler

# Create your own logger (no pre-initialized log instance)
logger = EzLog({
    "levels": {"error": True, "warn": True, "info": True, "success": True, "debug": False},
    "useColors": True,
    "useLevels": True,
    "useSymbols": False,
    "useTimestamp": True,
})
logger.success("Application started")
logger.info("Environment: dev")
logger.w("Warning")
logger.e("Error")
logger.d("Debug")

logger.configure({"useTimestamp": False})
logger.info("User:", {"id": 1, "name": "John"})
logger.error("Failed", Exception("Connection failed"))

# Error handler for routers (e.g. FastAPI/Starlette)
on_error = create_error_handler()
on_error(exception, request)
```

## Config

| Option         | Description                            |
|----------------|----------------------------------------|
| `levels`      | Enable/disable per level               |
| `useColors`   | ANSI colors on/off                     |
| `useLevels`   | Show level label before message        |
| `useSymbols` | Use symbols (x, !, i, ✓, d) or text   |
| `useTimestamp`| ISO timestamp before message           |

## Exports

- `EzLog` – logger class (create instances yourself)
- `create_error_handler(is_http_error=..., get_method=..., get_url=...)` – for router error callbacks
- Types: `LogLevel`, `LogColors`, `EzlogConfig`, `LevelsConfig`, `LevelConfig`, `LogArgs`, `ConsoleMethod`
