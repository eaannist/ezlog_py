"""Config package: default log instance and error handler factory."""
from ezlog_py.config.logger import create_error_handler, log

__all__ = ["log", "create_error_handler"]
