"""Manual smoke tests for colors and stdlib-level controls."""
from __future__ import annotations

import logging

from ezlog import EzLog
from ezlog.defaults import COLOR_CODES

# Color preview
for colour, code in COLOR_CODES.items():
    print(f"{code}{colour}{COLOR_CODES['reset']}")

# Stdlib-level feature preview
log = EzLog({"useColors": True, "timestamp": False, "stdlibLevel": "INFO"})
logging.debug("DEBUG hidden at INFO")
logging.info("INFO visible at INFO")

log.set_stdlib_debug(True)
logging.debug("DEBUG visible after set_stdlib_debug(True)")

log.set_stdlib_level("ERROR")
logging.warning("WARNING hidden at ERROR")
logging.error("ERROR visible at ERROR")