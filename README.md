# ezlogger

Simple, performant logging with ANSI colors for Python.

- **5 levels**: `error`, `warn`, `info`, `success`, `debug`
- **Short aliases**: `e`, `w`, `i`, `s`, `d`
- **ANSI colors**: red, yellow, cyan, green, magenta
- **Config**: levels on/off, colors, symbols vs text, timestamp
- **Safe serialization**: circular refs, dates, exceptions
- **Zero dependencies**

## Install

```bash
pip install -e .
```

## Usage

```python
from ezlogger import EzLog, log

# Default instance (debug off in production via ENV=production)
log.success("Application started")
log.info("Environment: dev")
log.w("Warning")
log.e("Error")
log.d("Debug")

# Custom config
logger = EzLog({
    "levels": {"error": True, "warn": True, "info": True, "success": True, "debug": False},
    "useColors": True,
    "useLevels": True,
    "useSymbols": False,
    "useTimestamp": True,
})
logger.configure({"useTimestamp": False})

# Objects and errors
log.info("User:", {"id": 1, "name": "John"})
log.error("Failed", Exception("Connection failed"))

# Error handler for routers (e.g. FastAPI/Starlette)
from ezlogger import create_error_handler
on_error = create_error_handler()
on_error(exception, request)
```

## Config

| Option        | Description                          |
|---------------|--------------------------------------|
| `levels`      | Enable/disable per level             |
| `useColors`   | ANSI colors on/off                   |
| `useLevels`   | Show level label before message      |
| `useSymbols`  | Use symbols (x, !, i, ✓, d) or text  |
| `useTimestamp` | ISO timestamp before message      |

## Exports

- `EzLog` – logger class  
- `log` – default instance (debug off when `ENV=production`)  
- `create_error_handler(is_http_error=..., get_method=..., get_url=...)` – for router error callbacks  
- Types: `LogLevel`, `LogColors`, `EzlogConfig`, `LevelConfig`, `LogArgs`, `ConsoleMethod`
