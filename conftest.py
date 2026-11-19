"""Diagnostic privacy applies before pytest returns reports to callers."""
import functools

import pytest
from scripts.test_report_privacy import install_junit_writer, redact_text


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    install_junit_writer(config)
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


def pytest_unconfigure(config):
    saved = getattr(config, '_diagnostic_privacy_writer', None)
    if saved is not None:
        writer, original = saved
        writer.write = original
