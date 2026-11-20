"""Retain fresh short lifecycle software controls, never mathematical approval."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    from scripts.whole_source import supervision as s
    from scripts.whole_source.lifecycle_observations import lifecycle_resources
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    if output.exists():
        raise FileExistsError('qualification output must be fresh')
    output.mkdir(parents=True)
    settings = {'format': s.POLICY, 'wall_seconds': 15, 'active_seconds': 120,
                'grace_seconds': 1, 'memory_mib': 128, 'sample_milliseconds': 100,
                'stale_milliseconds': 2000, 'observation_bytes': 16*s.MIB}
    cases = []

    def execute(name, source, *, expected, cancel=False, deadline=None):
        base = output/name
        base.mkdir()
        script = base/'control.py'
        script.write_text(source, encoding='utf-8', newline='\n')
        operation, observations = base/'operation', base/'operation.lifecycle'
        policy = dict(settings)
        if deadline is not None:
            policy['wall_seconds'] = deadline
        trigger = threading.Event() if cancel else None
        thread = None
        if cancel:
            def request():
                until = time.monotonic()+20
                while not (base/'ready').exists() and time.monotonic() < until:
                    time.sleep(.02)
                trigger.set()
            thread = threading.Thread(target=request, daemon=True)
            thread.start()
        receipt = s.supervise([], observation_root=observations, operation_root=operation,
            policy_document=policy, script=script, cancel_event=trigger)
        if thread is not None:
            thread.join(1)
        summary = lifecycle_resources(observations)
        passed = (receipt['status'] == expected and receipt['cleanup_verified'] and
                  receipt['final_job']['active_process_ids'] == [])
        row = {'name': name, 'passed': passed, 'status': receipt['status'],
               'receipt': str((observations/'receipts'/(receipt['invocation_id']+'.json')).relative_to(output)),
               'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
               'summary': summary}
        cases.append(row)
        return base, receipt

    base, receipt = execute('caller-memory', '''from pathlib import Path
import json
from scripts.whole_source.supervision import require_current
limit=require_current()['memory_limit_bytes']
kept=bytearray(16*1024*1024)
try:
    denied=bytearray(256*1024*1024)
except MemoryError:
    Path(__file__).with_name('allocation.json').write_text(json.dumps({'denied':True,'cap':limit}))
else: raise AssertionError('OS allocation cap was not enforced')
''', expected='COMPLETED')
    cases[-1]['passed'] &= json.loads((base/'allocation.json').read_bytes()) == {'denied': True, 'cap': 128*s.MIB}

    base, receipt = execute('cooperative-cancel', '''from pathlib import Path
import time
from scripts.whole_source.supervision import require_current
Path(__file__).with_name('ready').write_text('ready')
try:
    while True: time.sleep(.05)
except KeyboardInterrupt:
    try: require_current()
    except ValueError: Path(__file__).with_name('clean').write_text('cancelled admission and cooperative cleanup')
    else: raise AssertionError('new work was admitted after cancel')
''', expected='INTERRUPTED', cancel=True)
    cases[-1]['passed'] &= (base/'clean').read_text() == 'cancelled admission and cooperative cleanup'

    base, receipt = execute('stuck-descendant', '''from pathlib import Path
import subprocess,sys,time,json
child=subprocess.Popen([sys._base_executable,'-B','-c','import time;time.sleep(60)'])
Path(__file__).with_name('descendant.json').write_text(json.dumps({'pid':child.pid}))
while True:
    try: time.sleep(.05)
    except KeyboardInterrupt: pass
''', expected='INTERRUPTED', deadline=8)
    cases[-1]['passed'] &= receipt['reason'] == 'wall_or_cumulative_deadline'

    base, receipt = execute('bounded-output', '''import os,time
os.write(1,b'x'*100000)
time.sleep(5)
''', expected='INTERRUPTED')
    log = base/'operation.lifecycle/stdout'/(receipt['invocation_id']+'.log')
    cases[-1]['passed'] &= log.stat().st_size <= 65536

    report = {'format': 'whole-source-lifecycle-qualification-v1',
        'created_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'status': 'PASS_SOFTWARE_CONTROLS_ONLY' if all(row['passed'] for row in cases) else 'FAILED_SOFTWARE_CONTROLS',
        'python': sys.version, 'program_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases': cases, 'scope': 'REAL_SHORT_WINDOWS_PROCESSES_NOT_MATHEMATICAL_QUALIFICATION',
        'full_case_feasibility': False, 'scientific_acceptance': False, 'production_admission': False}
    with (output/'qualification.json').open('xb') as stream:
        stream.write(s._wire(report))
    print(json.dumps({'status': report['status'], 'cases': len(cases)}, sort_keys=True))
    return 0 if all(row['passed'] for row in cases) else 1


if __name__ == '__main__':
    raise SystemExit(main())
