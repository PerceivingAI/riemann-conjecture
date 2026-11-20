"""Replay the byte-captured selected arithmetic; compare only outside native trees."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]


def receipt(directory):
    state = json.loads((directory/'slice-state.json').read_bytes())
    assert state['status'] == 'VERIFIED_SELECTED_COMPLETE_ARITHMETIC'
    ref = state['receipt']
    raw = (directory/ref['path']).read_bytes()
    assert len(raw) == ref['size'] and hashlib.sha256(raw).hexdigest() == ref['sha256']
    return json.loads(raw)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--resume', action='store_true')
    args = p.parse_args()
    output = args.output_dir.resolve()
    capture = HERE/'captured-code-v4'
    assert not (capture/'.git').exists()
    excluded = {REPOSITORY.resolve(), HERE.resolve(), capture.resolve()}
    sys.path[:] = [str(capture)] + [entry for entry in sys.path
        if entry and Path(entry).resolve() not in excluded]
    os.chdir(capture)
    from scripts import weil_whole_source_split as cli
    assert Path(cli.__file__).resolve().is_relative_to(capture.resolve())
    inputs = HERE/'data/inputs-v4'
    arguments = ['slice', '--source-root', str(capture), '--output-dir', str(output)]
    for name in ('problem', 'cases', 'execution'):
        arguments += ['--'+name, str(inputs/(name+'.json'))]
    if args.resume:
        arguments.append('--resume')
    code = cli.main(arguments)
    if code:
        return code
    # Neither baseline nor expected mathematical values enter owned task inputs.
    baseline, actual = receipt(HERE/'data/normal-v4'), receipt(output)
    assert actual['entries'] == baseline['entries']
    for role in ('producer', 'analytic'):
        assert actual['roles'][role]['quantity_seals'] == baseline['roles'][role]['quantity_seals']
    print('PASS_FROZEN_CAPTURE_REPLAY_SELECTED_COMPLETE_ARITHMETIC')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
