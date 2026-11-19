"""Diagnostic redaction preserves genuine failures and their reproducible causes."""
import os
from pathlib import Path
import pytest
import subprocess
import sys
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from scripts.test_report_privacy import redact_text

ROOT = Path(__file__).resolve().parents[1]


def test_redaction_covers_windows_home_spellings_without_erasing_failure_cause():
    value = r'fixture-host C:\Users\test-person C:/Users/test-person C:\\Users\\test-person /tmp/pytest-of-test-person/session failure: wrong denominator'
    cleaned = redact_text(value, hostname='fixture-host', home=r'C:\Users\test-person')
    assert 'fixture-host' not in cleaned and 'test-person' not in cleaned
    assert cleaned.endswith('failure: wrong denominator')


@pytest.mark.parametrize(("mode", "exit_code"), [
    ("pass", 0), ("fail", 1), ("xdist", 1), ("interrupt", 2), ("exit_before_replace", 73),
])
def test_real_pytest_reports_are_safe_at_first_persistence(mode, exit_code):
    cache = ROOT/'.pytest_cache'
    cache.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='report-privacy-', dir=cache) as name:
        folder = Path(name)
        control = folder/'test_control.py'
        home = str(folder/'stage2-fixture-home')
        marker = f"stage2-fixture-host {home} /tmp/pytest-of-stage2-fixture-user/run"
        probe = folder/'privacy_probe.py'
        probe.write_text(
            "from pathlib import Path\n"
            "import os\nimport platform\nimport pytest\n"
            "platform.node = lambda: 'stage2-fixture-host'\n"
            "original_replace = os.replace\n"
            "def inspect_replace(source, target):\n"
            "    if Path(target).name == 'result.xml':\n"
            "        check(Path(source).read_bytes())\n"
            "        if os.environ['PRIVACY_TEST_EXIT'] == '1':\n"
            "            os._exit(73)\n"
            "    return original_replace(source, target)\n"
            "os.replace = inspect_replace\n"
            "def check(raw):\n"
            "    for token in (b'stage2-fixture-host', b'stage2-fixture-home', b'stage2-fixture-user'):\n"
            "        assert token not in raw, 'unsafe first JUnit write'\n"
            "@pytest.hookimpl(wrapper=True, trylast=True)\n"
            "def pytest_sessionfinish(session):\n"
            "    result = yield\n"
            "    report = Path(session.config.option.xmlpath)\n"
            "    if not hasattr(session.config, 'workerinput'):\n"
            "        check(report.read_bytes())\n"
            "    return result\n",
            encoding='utf-8')
        body = "assert False, 'controlled denominator failure ' + marker"
        if mode in {'pass', 'exit_before_replace'}:
            body = "assert True"
        elif mode == 'interrupt':
            body = "raise KeyboardInterrupt('controlled interruption ' + marker)"
        control.write_text(
            f"marker = {marker!r}\n"
            "def test_pass():\n    pass\n"
            "def test_control(record_property):\n"
            "    record_property('identity', marker)\n"
            f"    {body}\n", encoding='utf-8')
        report = folder/'result.xml'
        environment = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
                           PYTEST_ADDOPTS='', PYTEST_PLUGINS='', PYTHONDONTWRITEBYTECODE='1',
                           HOME=home, USERPROFILE=home, PYTHONPATH=str(folder),
                           PRIVACY_TEST_EXIT=str(int(mode == 'exit_before_replace')))
        workers = ['-p', 'xdist.plugin', '-n', '2'] if mode == 'xdist' else []
        result = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-o', 'addopts=', '-q',
            '-p', 'privacy_probe', *workers, '--junitxml', str(report), str(control)], cwd=ROOT,
            env=environment, capture_output=True, text=True, encoding='utf-8', timeout=60)
        assert result.returncode == exit_code, result.stdout + result.stderr
        if mode == 'exit_before_replace':
            assert not report.exists()
            staged, = folder.glob('.private-report-*')
            suite = ET.parse(staged).getroot()[0]
            assert (suite.get('tests'), suite.get('failures')) == ('2', '0')
            return
        assert not list(folder.glob('.private-report-*'))
        suite = ET.parse(report).getroot()[0]
        assert 'hostname' not in suite.attrib
        combined = report.read_text(encoding='utf-8') + result.stdout + result.stderr
        assert not any(token in combined for token in (
            'stage2-fixture-host', 'stage2-fixture-home', 'stage2-fixture-user'))
        if mode in {'fail', 'xdist'}:
            assert (suite.get('tests'), suite.get('failures')) == ('2', '1')
            assert 'controlled denominator failure' in suite.find('testcase/failure').text
        elif mode == 'pass':
            assert (suite.get('tests'), suite.get('failures')) == ('2', '0')
            assert suite.find(".//property[@name='identity']").get('value') != marker
        else:
            assert 'controlled interruption' in combined
