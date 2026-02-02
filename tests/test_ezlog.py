"""Tests for EzLog (mirrors ezlog.test.ts)."""
from datetime import datetime

from ezlog_py import EzLog


class TestEzLogBasicLogging:
    """EzLog - Basic Logging."""

    def test_should_create_logger_instance(self) -> None:
        logger = EzLog()
        assert logger is not None

    def test_should_have_all_log_methods(self) -> None:
        logger = EzLog()
        assert callable(logger.error)
        assert callable(logger.warn)
        assert callable(logger.info)
        assert callable(logger.success)
        assert callable(logger.debug)

    def test_should_have_short_alias_methods(self) -> None:
        logger = EzLog()
        assert callable(logger.e)
        assert callable(logger.w)
        assert callable(logger.i)
        assert callable(logger.s)
        assert callable(logger.d)


class TestEzLogLevelConfiguration:
    """EzLog - Level Configuration."""

    def test_should_not_log_when_level_is_disabled(self) -> None:
        logger = EzLog(
            {
                "levels": {
                    "error": True,
                    "warn": True,
                    "info": False,
                    "success": False,
                    "debug": False,
                },
                "useColors": False,
                "useTimestamp": False,
            }
        )
        logger.info("This should not log")
        logger.success("This should not log")
        logger.debug("This should not log")
        assert True  # no throw

    def test_should_log_when_level_is_enabled(self) -> None:
        logger = EzLog(
            {
                "levels": {
                    "error": True,
                    "warn": True,
                    "info": True,
                    "success": True,
                    "debug": True,
                },
                "useColors": False,
                "useTimestamp": False,
            }
        )
        logger.error("Error message")
        logger.info("Info message")
        assert True  # no throw


class TestEzLogConfiguration:
    """EzLog - Configuration."""

    def test_should_use_symbols_when_use_symbols_is_true(self) -> None:
        logger = EzLog(
            {
                "useColors": False,
                "useTimestamp": False,
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
                "useTimestamp": False,
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
                "useTimestamp": False,
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
                "useTimestamp": False,
            }
        )
        config = logger.get_config()
        assert config.get("useColors") is False
        assert config.get("useTimestamp") is False
        assert "levels" in config


class TestEzLogObjectFormatting:
    """EzLog - Object Formatting."""

    def test_should_format_plain_objects_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        logger.info({"id": 1, "name": "Test"})
        assert True  # no throw

    def test_should_format_error_objects_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        logger.error(ValueError("Test error"))
        assert True  # no throw

    def test_should_format_date_objects_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        date = datetime(2024, 1, 1, 0, 0, 0)
        logger.info(date)
        assert True  # no throw

    def test_should_handle_circular_references_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        obj: dict[str, object] = {"name": "Test"}
        obj["self"] = obj
        logger.info(obj)
        assert True  # no throw

    def test_should_format_arrays_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        logger.info([1, 2, 3])
        assert True  # no throw


class TestEzLogColorProperties:
    """EzLog - Color Properties."""

    def test_should_expose_color_properties_when_colors_enabled(self) -> None:
        logger = EzLog({"useColors": True})
        assert logger.red == "\x1b[31m"
        assert logger.yellow == "\x1b[33m"
        assert logger.cyan == "\x1b[36m"
        assert logger.green == "\x1b[32m"
        assert logger.magenta == "\x1b[35m"
        assert logger.white == "\x1b[0m"

    def test_should_return_empty_strings_when_colors_disabled(self) -> None:
        logger = EzLog({"useColors": False})
        assert logger.red == ""
        assert logger.yellow == ""
        assert logger.cyan == ""
        assert logger.green == ""
        assert logger.magenta == ""
        assert logger.white == ""


class TestEzLogEdgeCases:
    """EzLog - Edge Cases."""

    def test_should_not_throw_when_no_arguments_provided(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        logger.info()
        assert True  # no throw

    def test_should_handle_multiple_arguments_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        logger.info("Message 1", "Message 2", {"key": "value"})
        assert True  # no throw

    def test_should_handle_none_without_throwing(self) -> None:
        logger = EzLog({"useColors": False, "useTimestamp": False})
        logger.info(None)
        assert True  # no throw
