#!/usr/bin/env python3
"""
ezlog showcase: full demo of EzLog features.
Run: uv run python demo.py  or  ezlog-py (CLI)
"""
import json
import logging
from datetime import datetime
from typing import Any

from ezlog import COLOR_CODES, EzLog, init
from ezlog.defaults import DEFAULT_COLORS, DEFAULT_TEXTS, DEFAULT_SYMBOLS_FALLBACK


def _sep(title: str) -> None:
    print("\n" + "=" * 60 + f"\n  {title}\n" + "=" * 60)


def main() -> None:
    # -------------------------------------------------------------------------
    # 1. Create logger (wires to stdlib automatically)
    # -------------------------------------------------------------------------
    _sep("1. Create logger – wires to stdlib automatically")
    log = EzLog(use_colors=True, use_timestamp=True)
    log.info("Single EzLog() call wires itself to logging.getLogger()")
    log.info("From now on, logging.info(), logging.error(), etc. use ezlog formatting")

    # -------------------------------------------------------------------------
    # 2. All 6 levels (debug, info, success, warn, error, critical)
    # -------------------------------------------------------------------------
    _sep("2. All 6 levels (severity order)")
    log.debug("Debug: request details, internal state")
    log.info("Info: environment, config loaded")
    log.success("Success: operation completed")
    log.warn("Warning: rate limit approaching, deprecated API")
    log.error("Error: operation failed, retry later")
    log.critical("Critical: system failure, shutdown")

    # -------------------------------------------------------------------------
    # 3. Short aliases (d, i, s, w, e, c)
    # -------------------------------------------------------------------------
    _sep("3. Short aliases (d, i, s, w, e, c)")
    log.d("Same as log.debug(...)")
    log.i("Same as log.info(...)")
    log.s("Same as log.success(...)")
    log.w("Same as log.warn(...)")
    log.e("Same as log.error(...)")
    log.c("Same as log.critical(...)")

    # -------------------------------------------------------------------------
    # 4. Stdlib logging – all levels (wired to ezlog)
    # -------------------------------------------------------------------------
    _sep("4. Stdlib logging – all levels go through ezlog")
    logging.debug("logging.debug() -> ezlog debug")
    logging.info("logging.info() -> ezlog info")
    logging.warning("logging.warning() -> ezlog warn")
    logging.error("logging.error() -> ezlog error")
    logging.critical("logging.critical() -> ezlog critical")

    # -------------------------------------------------------------------------
    # 5. Exceptions and tracebacks
    # -------------------------------------------------------------------------
    _sep("5. Exceptions and tracebacks (ezlog formatting)")
    try:
        raise ValueError("Demo exception for traceback")
    except ValueError:
        logging.exception("Exception with traceback")

    # -------------------------------------------------------------------------
    # 6. Config at construction (dict)
    # -------------------------------------------------------------------------
    _sep("6. Config at construction (dict)")
    no_ts = EzLog({"useColors": True, "timestamp": False})
    no_ts.info("This line has no timestamp prefix")
    no_ts.success("Symbol and level label still shown")

    # -------------------------------------------------------------------------
    # 7. configure() at runtime
    # -------------------------------------------------------------------------
    _sep("7. configure() at runtime – timestamp: False or { format?, color? }")
    log.configure({"timestamp": False})
    log.info("Timestamp disabled via configure()")
    log.configure({"timestamp": {"format": "%Y-%m-%d %H:%M:%S", "color": "as_levels"}})
    log.info("Timestamp re-enabled (color: as_levels)")
    log.configure({"timestamp": {"format": "%H:%M", "color": "cyan"}})
    log.info("Custom format and color")

    # -------------------------------------------------------------------------
    # 8. useSymbols False / useLevels False
    # -------------------------------------------------------------------------
    _sep("8. useSymbols False and useLevels False")
    text_only = EzLog(
        {"useColors": False, "timestamp": False, "useSymbols": False}
    )
    text_only.info("Shows level text (e.g. INFO) instead of symbol")
    no_level = EzLog(
        {"useColors": False, "timestamp": False, "useLevels": False}
    )
    no_level.info("No level/symbol prefix, only message")

    # -------------------------------------------------------------------------
    # 9. Objects: dict, list, datetime
    # -------------------------------------------------------------------------
    _sep("9. Objects – dict, list, datetime (JSON-safe serialization)")
    log.info("User payload:", {"id": 1, "name": "John", "roles": ["admin", "user"]})
    log.info("Items:", [1, 2, 3, {"nested": True}])
    log.info("Event at:", datetime(2024, 6, 15, 12, 0, 0))

    # -------------------------------------------------------------------------
    # 10. Errors as first-class (exception object)
    # -------------------------------------------------------------------------
    _sep("10. Errors as first-class (exception object + traceback)")
    log.error("Database error:", ValueError("Connection refused"))
    log.info("Exception metadata is serialized safely")

    # -------------------------------------------------------------------------
    # 11. Circular reference (safe serialization)
    # -------------------------------------------------------------------------
    _sep("11. Circular reference (safe serialization)")
    obj: dict[str, Any] = {"name": "Node", "children": []}
    obj["parent"] = obj
    log.info("Tree node:", obj)
    log.info('Circular refs become "[Circular Reference]"')

    # -------------------------------------------------------------------------
    # 12. Color properties (custom formatted messages)
    # -------------------------------------------------------------------------
    _sep("12. Color properties (log.red, log.cyan, log.reset, etc.)")
    port = 3000
    log.s(f"Server listening on {log.cyan}{port}{log.reset}")
    log.i(
        "Colors: {\n"
        f"{"\n".join(f"        {code}{color}" for color, code in COLOR_CODES.items())}"
        "\n    }"
    )

    # -------------------------------------------------------------------------
    # 13. Custom level config (symbol, text, color; disable level)
    # -------------------------------------------------------------------------
    _sep("13. Custom level config (override symbol/text/color; disable level)")
    custom = EzLog(
        {
            "useColors": True,
            "timestamp": False,
            "levels": {
                "info": {
                    "symbol": "I",
                    "text": "NOTE",
                    "color": "light-cyan",
                },
                "debug": False,
            },
        }
    )
    custom.info("Custom info: NOTE + light-cyan")
    custom.debug("This is disabled and will not print")

    # -------------------------------------------------------------------------
    # 14. init() and ezlog.log (global logger)
    # -------------------------------------------------------------------------
    _sep("14. init() – global ezlog.log")
    init(use_colors=True, use_timestamp=False)
    import ezlog as ez

    ez.log.i("Use ezlog.log after init()")
    ez.log.s("Same API as EzLog() instance")

    # -------------------------------------------------------------------------
    # 15. get_config() – inspect current config
    # -------------------------------------------------------------------------
    _sep("15. get_config() – inspect current config")
    cfg = log.get_config()
    print("Current config (no consoleFn in levels):")
    print(json.dumps({k: v for k, v in cfg.items() if k == "levels"}, indent=2))
    print("Flags:", {k: cfg.get(k) for k in ("useColors", "useLevels", "useSymbols", "timestamp")})

    # -------------------------------------------------------------------------
    # 16. Defaults (DEFAULT_TEXTS, DEFAULT_COLORS, DEFAULT_SYMBOLS_FALLBACK)
    # -------------------------------------------------------------------------
    _sep("16. Defaults – DEFAULT_TEXTS, DEFAULT_COLORS, DEFAULT_SYMBOLS_FALLBACK")
    print("DEFAULT_TEXTS:", DEFAULT_TEXTS)
    print("DEFAULT_COLORS:", DEFAULT_COLORS)
    print("DEFAULT_SYMBOLS_FALLBACK (default/fallback per level):")
    for level, entry in DEFAULT_SYMBOLS_FALLBACK.items():
        # ASCII-safe for Windows cp1252
        d, f = ascii(entry["default"]), ascii(entry["fallback"])
        print(f"  {level}: default={d}, fallback={f}")

    # -------------------------------------------------------------------------
    # 17. Multiple loggers (different configs)
    # -------------------------------------------------------------------------
    _sep("17. Multiple loggers (different configs)")
    dev = EzLog({"useColors": True})
    prod = EzLog({"useColors": False, "timestamp": {"color": "as_levels"}, "levels": {"debug": False}})
    dev.d("Dev logger: debug enabled")
    prod.d("Prod logger: debug disabled (this won't print)")
    prod.i("Prod logger: info still works")

    _sep("Done")
    print()


if __name__ == "__main__":
    main()
