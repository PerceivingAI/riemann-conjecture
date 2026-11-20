"""Diagnostic redaction preserves genuine failures and their reproducible causes."""
import os
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from scripts.test_report_privacy import redact_text, sanitize_junit

ROOT = Path(__file__).resolve().parents[1]


def test_redaction_covers_windows_home_spellings_without_erasing_failure_cause():
    value = r'fixture-host C:\Users\test-person C:/Users/test-person C:\\Users\\test-person /tmp/pytest-of-test-person/session failure: wrong denominator'
    cleaned = redact_text(value, hostname='fixture-host', home=r'C:\Users\test-person')
    assert 'fixture-host' not in cleaned and 'test-person' not in cleaned
    assert cleaned.endswith('failure: wrong denominator')


def test_junit_redaction_preserves_counts_results_and_failure_text(tmp_path):
    path = tmp_path/'report.xml'
    path.write_text('<testsuites><testsuite name="pytest" hostname="private-host" tests="2" failures="1" errors="0">'
        '<testcase name="passed"/><testcase name="failed"><failure message="wrong denominator">'
        'expected exact denominator 7, got 9</failure></testcase></testsuite></testsuites>', encoding='utf-8')
    result = sanitize_junit(path)
    suite = ET.parse(path).getroot()[0]
    assert result['hostname_attributes_removed'] == 1
    assert suite.attrib == {'name':'pytest','tests':'2','failures':'1','errors':'0'}
    assert suite.find('testcase/failure').text == 'expected exact denominator 7, got 9'
    assert 'private-host' not in path.read_text(encoding='utf-8')


def test_real_pytest_failure_report_and_terminal_do_not_expose_identity():
    cache = ROOT/'.pytest_cache'
    cache.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='report-privacy-', dir=cache) as name:
        folder = Path(name)
        control = folder/'test_control.py'
        control.write_text('def test_control():\n    assert False, "controlled denominator failure"\n', encoding='utf-8')
        report = folder/'result.xml'
        environment = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-o', 'addopts=', '-q',
            '--junitxml', str(report), str(control)], cwd=ROOT, env=environment,
            capture_output=True, text=True, timeout=60)
        assert result.returncode == 1, 'controlled failing test must remain a failure'
        suite = ET.parse(report).getroot()[0]
        assert suite.get('failures') == '1' and suite.find('testcase/failure') is not None
        assert 'hostname' not in suite.attrib
        combined = report.read_text(encoding='utf-8')+result.stdout+result.stderr
        assert platform.node() not in combined, 'host identity leaked through diagnostics'
        assert str(Path.home()) not in combined, 'user-home identity leaked through diagnostics'
        assert 'controlled denominator failure' in combined
