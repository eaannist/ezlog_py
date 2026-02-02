#!/usr/bin/env python3
"""
ezlog_py demo: configuration, usage, and showcase.
Run: uv run python demo.py  or  python -m ezlog_py (then use ezlog-py CLI)
"""
from datetime import datetime
from typing import Any

from ezlog_py import EzLog, create_error_handler, log


def _sep(title: str) -> None:
    print("\n" + "=" * 60 + f"\n  {title}\n" + "=" * 60)


def demo_default_log() -> None:
    """Use the global log instance (debug off when ENV=production)."""
    _sep("1. Default log instance")
    log.success("Application started")
    log.info("Environment: dev")
    log.warn("Rate limit approaching")
    log.error("Something went wrong")
    log.debug("Request details: GET /api/users")


def demo_short_aliases() -> None:
    """Short aliases: e, w, i, s, d."""
    _sep("2. Short aliases (e, w, i, s, d)")
    logger = EzLog({"useColors": True, "useTimestamp": True})
    logger.s("Success via alias")
    logger.i("Info via alias")
    logger.w("Warning via alias")
    logger.e("Error via alias")
    logger.d("Debug via alias")


def demo_custom_configuration() -> None:
    """Custom EzLog: levels, colors, symbols vs text, timestamp."""
    _sep("3. Custom configuration")
    logger = EzLog(
        {
            "levels": {
                "error": True,
                "warn": True,
                "info": True,
                "success": True,
                "debug": False,
            },
            "useColors": True,
            "useLevels": True,
            "useSymbols": False,
            "useTimestamp": True,
        }
    )
    logger.info("Using text labels (INFO, WARN, etc.)")
    logger.success("Success label")
    logger.warn("Warn label")
    logger.debug("This is disabled and will not appear")


def demo_runtime_configure() -> None:
    """Update configuration at runtime with configure()."""
    _sep("4. Runtime configure()")
    logger = EzLog(
        {
            "useColors": True,
            "useTimestamp": True,
            "useSymbols": True,
        }
    )
    logger.info("Before: timestamp + symbols")
    logger.configure({"useTimestamp": False})
    logger.info("After: no timestamp")
    logger.configure({"useSymbols": False})
    logger.info("After: text labels")
    logger.configure({"useTimestamp": True, "useSymbols": True})


def demo_objects_and_errors() -> None:
    """Log plain objects, errors, dates; safe serialization."""
    _sep("5. Objects, errors, dates")
    logger = EzLog({"useColors": True, "useTimestamp": False})
    logger.info(
        "User data:",
        {"id": 1, "name": "John", "roles": ["admin", "user"]},
    )
    logger.error("Database error:", ValueError("Connection refused"))
    logger.info("Event at:", datetime(2024, 6, 15, 12, 0, 0))


def demo_circular_reference() -> None:
    """Circular references are replaced with [Circular Reference]."""
    _sep("6. Circular reference (safe serialization)")
    logger = EzLog({"useColors": False, "useTimestamp": False})
    obj: dict[str, Any] = {"name": "Node", "children": []}
    obj["parent"] = obj
    logger.info("Tree node:", obj)


def demo_color_properties() -> None:
    """Use logger color properties for custom formatted messages."""
    _sep("7. Color properties (custom formatting)")
    logger = EzLog({"useColors": True})
    port = 3000
    logger.s(f"Server running on port {logger.cyan}{port}{logger.white}")
    logger.i(
        f"Levels: {logger.red}error {logger.yellow}warn {logger.cyan}info "
        f"{logger.green}success {logger.magenta}debug"
    )


def demo_error_handler() -> None:
    """create_error_handler for router/on_error style (e.g. FastAPI, Starlette)."""
    _sep("8. create_error_handler showcase")
    handler = create_error_handler()

    class MockRequest:
        method = "GET"
        url = "/api/users/42"
        path = "/api/users/42"

    req = MockRequest()

    class ServerError(Exception):
        status_code = 500

    handler(ServerError("Internal error"), req)

    class ClientError(Exception):
        status_code = 404

    handler(ClientError("Not found"), req)
    handler(ValueError("Unexpected"), req)


def demo_edge_cases() -> None:
    """No args (no-op), multiple args, None."""
    _sep("9. Edge cases")
    logger = EzLog({"useColors": False, "useTimestamp": False})
    logger.info()
    logger.info("Part 1", "Part 2", {"key": "value"})
    logger.info(None)


def main() -> None:
    print("\n  ezlog_py demo – configuration, usage, showcase\n")
    demo_default_log()
    demo_short_aliases()
    demo_custom_configuration()
    demo_runtime_configure()
    demo_objects_and_errors()
    demo_circular_reference()
    demo_color_properties()
    demo_error_handler()
    demo_edge_cases()
    _sep("Done")
    print()


if __name__ == "__main__":
    main()
