"""Redact host identity and user-home paths from diagnostic test reports only."""
import os
from pathlib import Path
import platform
import re
import stat
import tempfile
import xml.etree.ElementTree as ET

from _pytest.junitxml import LogXML, xml_key


def redact_text(text, *, hostname=None, home=None):
    hostname = platform.node() if hostname is None else hostname
    home = str(Path.home()) if home is None else home
    variants = {home, home.replace('\\', '/'), home.replace('\\', '\\\\')}
    for value in sorted(variants, key=len, reverse=True):
        if value:
            text = re.sub(re.escape(value), '<USER_HOME>', text, flags=re.IGNORECASE)
    if hostname:
        text = re.sub(re.escape(hostname), '<REDACTED_HOST>', text, flags=re.IGNORECASE)
    text = re.sub(r"pytest-of-[^/\\\s<>\"']+", 'pytest-of-USER', text, flags=re.IGNORECASE)
    return text


def _encode_junit(root):
    """Filter the complete XML tree in memory before opening any output."""
    for node in root.iter():
        node.attrib.pop('hostname', None)
        for key, value in tuple(node.attrib.items()):
            node.attrib[key] = redact_text(value)
        if node.text is not None:
            node.text = redact_text(node.text)
        if node.tail is not None:
            node.tail = redact_text(node.tail)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def _publish_junit(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        info = path.lstat()
    except FileNotFoundError:
        pass
    else:
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('report privacy requires a regular unshared report file')
    descriptor, temporary = tempfile.mkstemp(prefix='.private-report-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class _PrivateLogXML(LogXML):
    def pytest_sessionfinish(self):
        # Keep pytest's reporting and aggregation. Replace only its disk writer.
        duration = self.suite_start.elapsed()
        suite = ET.Element(
            'testsuite', name=self.suite_name,
            errors=str(self.stats['error']), failures=str(self.stats['failure']),
            skipped=str(self.stats['skipped']),
            tests=str(sum(self.stats.values()) - self.cnt_double_fail_tests),
            time=f'{duration.seconds:.3f}',
            timestamp=self.suite_start.as_utc().astimezone().isoformat(),
        )
        properties = self._get_global_properties_node()
        if properties is not None:
            suite.append(properties)
        for reporter in self.node_reporters_ordered:
            suite.append(reporter.to_xml())
        root = ET.Element('testsuites', name='pytest tests')
        root.append(suite)
        _publish_junit(Path(self.logfile), _encode_junit(root))


def install_junit_writer(config):
    """Replace the controller's stock reporter before it receives any events."""
    stock = config.stash.get(xml_key, None)
    if stock is None:
        if getattr(config.option, 'xmlpath', None) and not hasattr(config, 'workerinput'):
            raise RuntimeError('cannot install private JUnit writer without pytest junitxml')
        return
    private = _PrivateLogXML(
        stock.logfile, stock.prefix, stock.suite_name, stock.logging,
        stock.report_duration, stock.family, stock.log_passing_tests,
    )
    config.pluginmanager.unregister(stock)
    config.pluginmanager.register(private)
    config.stash[xml_key] = private
