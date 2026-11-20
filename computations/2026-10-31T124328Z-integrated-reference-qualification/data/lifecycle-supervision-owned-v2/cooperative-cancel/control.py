from pathlib import Path
import time
from scripts.whole_source.supervision import require_current
Path(__file__).with_name('ready').write_text('ready')
try:
    while True: time.sleep(.05)
except KeyboardInterrupt:
    try: require_current()
    except ValueError: Path(__file__).with_name('clean').write_text('cancelled admission and cooperative cleanup')
    else: raise AssertionError('new work was admitted after cancel')
