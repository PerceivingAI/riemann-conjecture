"""Diagnostic privacy applies before pytest returns reports to callers."""
import functools
from pathlib import Path

import pytest
from scripts.test_report_privacy import redact_text, sanitize_junit


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    reporter = config.pluginmanager.getplugin('terminalreporter')
    if reporter is None:
        return
    writer = reporter._tw
    original = writer.write
    @functools.wraps(original)
    def private_write(text, **kwargs):
        return original(redact_text(text), **kwargs)
    writer.write = private_write
    config._diagnostic_privacy_writer = (writer, original)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    try:
        return (yield)
    finally:
        report = getattr(session.config.option, 'xmlpath', None)
        if report is not None and Path(report).is_file():
            sanitize_junit(report)


def pytest_unconfigure(config):
    saved = getattr(config, '_diagnostic_privacy_writer', None)
    if saved is not None:
        writer, original = saved
        writer.write = original
