"""Redact host identity and user-home paths from diagnostic test reports only."""
import os
from pathlib import Path
import platform
import re
import stat
import tempfile
import xml.etree.ElementTree as ET


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


def sanitize_junit(path):
    """Remove identifying fields without changing outcomes, counts or failure causes."""
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink() or info.st_nlink != 1:
        raise ValueError('report privacy requires a regular unshared report file')
    tree = ET.parse(path)
    removed = 0
    for node in tree.iter():
        if 'hostname' in node.attrib:
            del node.attrib['hostname']
            removed += 1
        for key, value in tuple(node.attrib.items()):
            node.attrib[key] = redact_text(value)
        if node.text is not None:
            node.text = redact_text(node.text)
        if node.tail is not None:
            node.tail = redact_text(node.tail)
    raw = ET.tostring(tree.getroot(), encoding='utf-8', xml_declaration=True)
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
    return {'hostname_attributes_removed': removed}
