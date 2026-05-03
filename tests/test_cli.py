"""Tests for virplot.cli._Formatter."""

import logging

from virplot.cli import _Formatter


def test_formatter_info_omits_level():
    handler = logging.StreamHandler()
    handler.setFormatter(_Formatter())
    record = logging.LogRecord("test", logging.INFO, "", 0, "hello", (), None)
    assert handler.format(record) == "[VirPlot] hello"


def test_formatter_warning_includes_level():
    handler = logging.StreamHandler()
    handler.setFormatter(_Formatter())
    record = logging.LogRecord("test", logging.WARNING, "", 0, "caution", (), None)
    assert handler.format(record) == "[VirPlot] WARNING: caution"


def test_formatter_error_includes_level():
    handler = logging.StreamHandler()
    handler.setFormatter(_Formatter())
    record = logging.LogRecord("test", logging.ERROR, "", 0, "bad", (), None)
    assert handler.format(record) == "[VirPlot] ERROR: bad"


def test_formatter_debug_includes_level():
    handler = logging.StreamHandler()
    handler.setFormatter(_Formatter())
    record = logging.LogRecord("test", logging.DEBUG, "", 0, "detail", (), None)
    assert handler.format(record) == "[VirPlot] DEBUG: detail"
