from pathlib import Path
import json
from scripts.whole_source.supervision import require_current
limit=require_current()['memory_limit_bytes']
kept=bytearray(16*1024*1024)
try:
    denied=bytearray(256*1024*1024)
except MemoryError:
    Path(__file__).with_name('allocation.json').write_text(json.dumps({'denied':True,'cap':limit}))
else: raise AssertionError('OS allocation cap was not enforced')
