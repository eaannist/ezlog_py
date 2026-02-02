#!/usr/bin/env python3
"""
ezlog demo: init with two settings, then use ezlog.log or stdlib logging.
Run: uv run python demo.py  or  ezlog-py (CLI)
"""
import logging
from datetime import datetime
from typing import Any

import ezlog


def _sep(title: str) -> None:
    print("\n" + "=" * 60 + f"\n  {title}\n" + "=" * 60)


def main() -> None:
    # Only ezlog: init with the two settings
    ezlog.init(use_colors=True, use_timestamp=True)

    _sep("1. ezlog.log (direct)")
    ezlog.log.success("Application started")
    ezlog.log.info("Environment: dev")
    ezlog.log.warn("Rate limit approaching")
    ezlog.log.error("Something went wrong")
    ezlog.log.debug("Request details: GET /api/users")

    _sep("2. Short aliases (e, w, i, s, d)")
    ezlog.log.s("Success via alias")
    ezlog.log.i("Info via alias")
    ezlog.log.w("Warning via alias")
    ezlog.log.e("Error via alias")
    ezlog.log.d("Debug via alias")

    _sep("3. Stdlib logging (wired internally)")
    logging.info("Message via logging.info()")
    logging.warning("Warning via logging.warning()")
    logging.error("Error via logging.error()")
    try:
        raise ValueError("Demo exception")
    except ValueError:
        logging.exception("Exception with traceback (ezlog formatting)")

    _sep("4. Objects and errors")
    ezlog.log.info("User data:", {"id": 1, "name": "John", "roles": ["admin", "user"]})
    ezlog.log.error("Database error:", ValueError("Connection refused"))
    ezlog.log.info("Event at:", datetime(2024, 6, 15, 12, 0, 0))

    _sep("5. Circular reference (safe serialization)")
    obj: dict[str, Any] = {"name": "Node", "children": []}
    obj["parent"] = obj
    ezlog.log.info("Tree node:", obj)

    _sep("6. Color properties (custom formatting)")
    port = 3000
    ezlog.log.s(f"Server on port {ezlog.log.cyan}{port}{ezlog.log.white}")
    ezlog.log.i(
        f"Levels: {ezlog.log.red}error {ezlog.log.yellow}warn {ezlog.log.cyan}info "
        f"{ezlog.log.green}success {ezlog.log.magenta}debug"
    )

    _sep("Done")
    print()


if __name__ == "__main__":
    main()
