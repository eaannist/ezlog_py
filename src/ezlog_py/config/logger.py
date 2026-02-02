"""
Default log instance and create_error_handler for router/onError-style usage.
Environment-based levels, global log, error handler factory.
"""
from __future__ import annotations

import os
from typing import Any, Callable

from ezlog_py.ezlog import EzLog

_IS_PRODUCTION = os.environ.get("ENV", "").lower() == "production"

log = EzLog(
    {
        "levels": {
            "error": True,
            "warn": True,
            "info": True,
            "success": True,
            "debug": not _IS_PRODUCTION,
        },
        "useColors": True,
        "useLevels": True,
        "useSymbols": True,
        "useTimestamp": True,
    }
)


def _default_is_http_error(err: Any) -> bool:
    """True if err has status_code or statusCode (common HTTP error pattern)."""
    return hasattr(err, "status_code") or hasattr(err, "statusCode")


def _default_status_code(err: Any) -> int:
    """Extract status code from error (status_code or statusCode)."""
    return getattr(err, "status_code", None) or getattr(err, "statusCode", 500)


def create_error_handler(
    *,
    is_http_error: Callable[[Any], bool] | None = None,
    get_method: Callable[[Any], str] | None = None,
    get_url: Callable[[Any], str] | None = None,
) -> Callable[[Any, Any], None]:
    """
    Create error handler for router on_error callback.
    Logs by level: 5xx -> error, 4xx -> warn, else -> info.
    """
    is_http = is_http_error or _default_is_http_error
    get_m = get_method or (
        lambda req: getattr(req, "method", getattr(req, "METHOD", "?"))
    )
    get_u = get_url or (
        lambda req: getattr(req, "url", getattr(req, "path", "?"))
    )

    def handler(err: Any, request: Any = None) -> None:
        if request is None:
            method, url = "?", "?"
        else:
            method, url = get_m(request), get_u(request)
        if is_http(err):
            code = _default_status_code(err)
            if code >= 500:
                log.e(f"[{method}] {url} - {code}", err)
            elif code >= 400:
                log.w(f"[{method}] {url} - {code}", err)
            else:
                log.i(f"[{method}] {url} - {code}", err)
        else:
            log.e(f"[{method}] {url} - Unhandled error", err)

    return handler
