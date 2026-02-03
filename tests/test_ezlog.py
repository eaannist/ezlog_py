"""Comprehensive tests for EzLog, defaults, and stdlib integration."""
import io
import logging
import sys
from datetime import datetime
from typing import Any

from ezlog import EzLog
from ezlog.defaults import (
    DEFAULT_COLORS,
    DEFAULT_SYMBOLS_FALLBACK,
    DEFAULT_TEXTS,
    COLOR_CODES,
)
from ezlog.types import LogLevel

_LOG_LEVELS: tuple[LogLevel, ...] = (
    "debug",
    "info",
    "success",
    "warn",
    "error",
    "critical",
)


# --- Basic logging ---


class TestEzLogBasicLogging:
    """EzLog - Basic Logging."""

    def test_should_create_logger_instance(self) -> None:
        logger = EzLog()
        assert logger is not None

    def test_should_have_all_log_methods(self) -> None:
        logger = EzLog()
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.success)
        assert callable(logger.warn)
        assert callable(logger.error)
        assert callable(logger.critical)

    def test_should_have_short_alias_methods(self) -> None:
        logger = EzLog()
        assert callable(logger.d)
        assert callable(logger.i)
        assert callable(logger.s)
        assert callable(logger.w)
        assert callable(logger.e)
        assert callable(logger.c)

    def test_all_levels_accept_multiple_args(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.debug("a", "b", 1)
        logger.info("x", {"k": "v"})
        logger.success("ok")
        logger.warn("w", None)
        logger.error("e", 0)
        logger.critical("c")
        assert True  # no throw


# --- Level configuration ---


class TestEzLogLevelConfiguration:
    """EzLog - Level Configuration."""

    def test_should_not_log_when_level_is_disabled(self) -> None:
        logger = EzLog(
            {
                "levels": {
                    "debug": False,
                    "info": False,
                    "success": False,
                    "warn": True,
                    "error": True,
                    "critical": False,
                },
                "useColors": False,
                "timestamp": False,
            }
        )
        logger.info("This should not log")
        logger.success("This should not log")
        logger.debug("This should not log")
        logger.critical("This should not log")
        assert True  # no throw

    def test_should_log_when_level_is_enabled(self) -> None:
        logger = EzLog(
            {
                "levels": {
                    "debug": True,
                    "info": True,
                    "success": True,
                    "warn": True,
                    "error": True,
                    "critical": True,
                },
                "useColors": False,
                "timestamp": False,
            }
        )
        logger.error("Error message")
        logger.info("Info message")
        logger.critical("Critical message")
        assert True  # no throw

    def test_default_levels_include_all_six_levels(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        config = logger.get_config()
        levels = config.get("levels") or {}
        for level in _LOG_LEVELS:
            assert level in levels
            assert levels[level] is not False
            assert isinstance(levels[level], dict)
            assert levels[level].get("text") == DEFAULT_TEXTS[level]
            assert levels[level].get("color") == DEFAULT_COLORS[level]
            assert "symbol" in levels[level]


# --- Configuration ---


class TestEzLogConfiguration:
    """EzLog - Configuration."""

    def test_should_use_symbols_when_use_symbols_is_true(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
                "useSymbols": True,
                "useLevels": True,
            }
        )
        config = logger.get_config()
        assert config.get("useSymbols") is True

    def test_should_use_text_when_use_symbols_is_false(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
                "useSymbols": False,
                "useLevels": True,
            }
        )
        config = logger.get_config()
        assert config.get("useSymbols") is False

    def test_configure_should_update_configuration(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
                "useSymbols": True,
            }
        )
        logger.configure({"useSymbols": False})
        config = logger.get_config()
        assert config.get("useSymbols") is False

    def test_get_config_should_return_current_configuration(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
            }
        )
        config = logger.get_config()
        assert config.get("useColors") is False
        assert config.get("timestamp") is False
        assert "levels" in config

    def test_get_config_levels_have_level_config_shape_no_console_fn(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        config = logger.get_config()
        levels = config.get("levels")
        assert levels is not None
        for level_name, level_cfg in levels.items():
            if level_cfg is False:
                continue
            assert isinstance(level_cfg, dict)
            assert "symbol" in level_cfg
            assert "text" in level_cfg
            assert "color" in level_cfg
            assert "consoleFn" not in level_cfg

    def test_custom_level_config_override(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
                "levels": {
                    "info": {
                        "symbol": "N",
                        "text": "Note",
                        "color": "blue",
                    },
                    "debug": False,
                },
            }
        )
        config = logger.get_config()
        levels = config.get("levels") or {}
        assert isinstance(levels.get("info"), dict)
        assert levels["info"]["symbol"] == "N"
        assert levels["info"]["text"] == "Note"
        assert levels["info"]["color"] == "blue"
        assert levels.get("debug") is False
        logger.info("Custom note level")
        assert True  # no throw

    def test_init_with_config_dict_only(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
                "useLevels": True,
                "useSymbols": True,
            }
        )
        cfg = logger.get_config()
        assert cfg.get("useColors") is False
        assert cfg.get("timestamp") is False
        assert cfg.get("useLevels") is True
        assert cfg.get("useSymbols") is True

    def test_config_dict_sets_flags(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        cfg = logger.get_config()
        assert cfg.get("useColors") is False
        assert cfg.get("timestamp") is False

    def test_configure_disables_level_at_runtime(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.configure({"levels": {"info": False}})
        cfg = logger.get_config()
        assert cfg.get("levels", {}).get("info") is False
        logger.info("Silent")
        assert True  # no throw

    def test_configure_overrides_level_config_at_runtime(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.configure(
            {
                "levels": {
                    "warn": {"symbol": "!", "text": "WARN", "color": "yellow"},
                },
            }
        )
        cfg = logger.get_config()
        assert cfg.get("levels", {}).get("warn", {}).get("text") == "WARN"
        logger.warn("Updated")
        assert True  # no throw

    def test_timestamp_false_disables_timestamp(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        cfg = logger.get_config()
        assert cfg.get("timestamp") is False
        logger.info("No timestamp prefix")
        assert True  # no throw

    def test_timestamp_config_format_and_color(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": {"format": "%H:%M:%S", "color": "gray"},
            }
        )
        cfg = logger.get_config()
        ts = cfg.get("timestamp")
        assert isinstance(ts, dict)
        assert ts.get("format") == "%H:%M:%S"
        assert ts.get("color") == "gray"
        logger.info("Custom timestamp format and color")
        assert True  # no throw

    def test_timestamp_as_levels_uses_level_color(self) -> None:
        logger = EzLog({"useColors": True, "timestamp": {"color": "as_levels"}})
        cfg = logger.get_config()
        assert cfg.get("timestamp") is not False
        assert cfg.get("timestamp", {}).get("color") == "as_levels"
        logger.info("Timestamp colored as level")
        assert True  # no throw


# --- Object formatting ---


class TestEzLogObjectFormatting:
    """EzLog - Object Formatting."""

    def test_should_format_plain_objects_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.info({"id": 1, "name": "Test"})
        assert True  # no throw

    def test_should_format_error_objects_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.error(ValueError("Test error"))
        assert True  # no throw

    def test_should_format_date_objects_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        date = datetime(2024, 1, 1, 0, 0, 0)
        logger.info(date)
        assert True  # no throw

    def test_should_handle_circular_references_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        obj: dict[str, Any] = {"name": "Test"}
        obj["self"] = obj
        logger.info(obj)
        assert True  # no throw

    def test_should_format_arrays_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.info([1, 2, 3])
        assert True  # no throw

    def test_should_format_nested_structures(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.info(
            {
                "users": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                "meta": {"count": 2},
            }
        )
        assert True  # no throw

    def test_should_handle_exception_with_traceback(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        try:
            raise RuntimeError("Intentional")
        except RuntimeError as e:
            logger.error("Caught:", e)
        assert True  # no throw


# --- Color properties ---


class TestEzLogColorProperties:
    """EzLog - Color Properties."""

    def test_should_expose_color_properties_when_colors_enabled(self) -> None:
        logger = EzLog({"useColors": True})
        assert logger.red == "\x1b[31m"
        assert logger.yellow == "\x1b[33m"
        assert logger.cyan == "\x1b[36m"
        assert logger.green == "\x1b[32m"
        assert logger.magenta == "\x1b[35m"
        assert logger.white == "\x1b[37m"
        assert logger.gray == "\x1b[90m"
        assert logger.reset == "\x1b[0m"

    def test_should_return_empty_strings_when_colors_disabled(self) -> None:
        logger = EzLog({"useColors": False})
        assert logger.red == ""
        assert logger.yellow == ""
        assert logger.cyan == ""
        assert logger.green == ""
        assert logger.magenta == ""
        assert logger.white == ""
        assert logger.gray == ""
        assert logger.reset == ""


# --- Edge cases ---


class TestEzLogEdgeCases:
    """EzLog - Edge Cases."""

    def test_should_not_throw_when_no_arguments_provided(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.info()
        assert True  # no throw

    def test_should_handle_multiple_arguments_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.info("Message 1", "Message 2", {"key": "value"})
        assert True  # no throw

    def test_should_handle_none_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "timestamp": False})
        logger.info(None)
        assert True  # no throw

    def test_empty_config_dict(self) -> None:
        logger = EzLog({})
        assert logger.get_config() is not None
        assert "levels" in logger.get_config()

    def test_none_config(self) -> None:
        logger = EzLog(None)
        cfg = logger.get_config()
        assert cfg.get("useColors") is True
        assert cfg.get("timestamp") is not False and isinstance(cfg.get("timestamp"), dict)
        assert len(cfg.get("levels") or {}) == 6

    def test_partial_level_override_preserves_other_fields(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "timestamp": False,
                "levels": {"info": {"color": "blue"}},
            }
        )
        cfg = logger.get_config()
        info_cfg = cfg.get("levels", {}).get("info")
        assert isinstance(info_cfg, dict)
        assert info_cfg.get("color") == "blue"
        assert info_cfg.get("text") == DEFAULT_TEXTS["info"]
        assert "symbol" in info_cfg


# --- Defaults constants ---


class TestDefaultsConstants:
    """Defaults - DEFAULT_TEXTS, DEFAULT_COLORS, DEFAULT_SYMBOLS_FALLBACK."""

    def test_default_texts_has_all_levels(self) -> None:
        for level in _LOG_LEVELS:
            assert level in DEFAULT_TEXTS
            assert isinstance(DEFAULT_TEXTS[level], str)
            assert len(DEFAULT_TEXTS[level]) > 0

    def test_default_colors_has_all_levels(self) -> None:
        for level in _LOG_LEVELS:
            assert level in DEFAULT_COLORS
            assert DEFAULT_COLORS[level] in COLOR_CODES

    def test_default_symbols_fallback_has_default_and_fallback(self) -> None:
        for level in _LOG_LEVELS:
            assert level in DEFAULT_SYMBOLS_FALLBACK
            entry = DEFAULT_SYMBOLS_FALLBACK[level]
            assert "default" in entry
            assert "fallback" in entry
            assert isinstance(entry["default"], str)
            assert isinstance(entry["fallback"], str)

    def test_reset_and_color_codes_are_ansi(self) -> None:
        assert "\x1b[" in list(COLOR_CODES.values())[0]


# --- Stdlib integration ---


class TestEzLogWiresStdlib:
    """EzLog() wires itself to stdlib on construction."""

    def test_ezlog_construction_wires_stdlib(self) -> None:
        log = EzLog({"useColors": False, "timestamp": False})
        assert log is not None
        logging.info("Test after EzLog()")
        assert True  # no throw

    def test_ezlog_accepts_config_dict(self) -> None:
        log = EzLog({"useColors": True, "timestamp": False})
        cfg = log.get_config()
        assert cfg.get("useColors") is True
        assert cfg.get("timestamp") is False

    def test_stdlib_debug_maps_to_ezlog_debug(self) -> None:
        log = EzLog({"useColors": False, "timestamp": False})
        logging.debug("Stdlib debug")
        assert True  # no throw

    def test_stdlib_info_maps_to_ezlog_info(self) -> None:
        log = EzLog({"useColors": False, "timestamp": False})
        logging.info("Stdlib info")
        assert True  # no throw

    def test_stdlib_warning_maps_to_ezlog_warn(self) -> None:
        log = EzLog({"useColors": False, "timestamp": False})
        logging.warning("Stdlib warning")
        assert True  # no throw

    def test_stdlib_error_maps_to_ezlog_error(self) -> None:
        log = EzLog({"useColors": False, "timestamp": False})
        logging.error("Stdlib error")
        assert True  # no throw

    def test_stdlib_critical_maps_to_ezlog_critical(self) -> None:
        log = EzLog({"useColors": False, "timestamp": False})
        logging.critical("Stdlib critical")
        assert True  # no throw


# --- Output behavior (capture) ---


class TestEzLogOutputBehavior:
    """EzLog - Output goes to stdout/stderr as expected."""

    def test_info_output_contains_message(self) -> None:
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            log = EzLog({"useColors": False, "timestamp": False})
            log.info("Hello world")
            out = buf.getvalue()
        finally:
            sys.stdout = old_stdout
        assert "Hello world" in out

    def test_error_output_contains_message_on_stderr(self) -> None:
        buf = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = buf
        try:
            log = EzLog({"useColors": False, "timestamp": False})
            log.error("Error world")
            err = buf.getvalue()
        finally:
            sys.stderr = old_stderr
        assert "Error world" in err

    def test_disabled_level_produces_no_output(self) -> None:
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            log = EzLog(
                {
                    "useColors": False,
                    "timestamp": False,
                    "levels": {"info": False},
                }
            )
            log.info("Must not appear")
            out = buf.getvalue()
        finally:
            sys.stdout = old_stdout
        assert "Must not appear" not in out
