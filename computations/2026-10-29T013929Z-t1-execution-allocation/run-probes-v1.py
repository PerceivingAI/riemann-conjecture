"""Run only named nonproof T=1 probes under the retained neutral containment.

The existing supervisor's READY/GO, log capture, resource accounting and owned
cleanup are reused. Only the run identity is specialised here, so it cannot
mislabel this measurement as the frozen .81 proof computation.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'computations/2026-10-28T034134Z-t081-resource-execution'
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(ROOT))


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


supervisor = module(BASE / 'execution_supervisor_v1.py', 't1_probe_containment')
policy = module(BASE / 'execution_resources_v2.py', 't1_probe_resource_policy')


class ProbeExecution(supervisor.Execution):
    def __enter__(self):
        self.lock = supervisor.OutputDirectoryLock.acquire(
            self.output, command='t1-execution-probe-v1', support='1')
        try:
            commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout.strip()
            supervisor.write_run_identity(self.lock, driver_version='t1-execution-probe-v1',
                dimensions=[5564], git_commit=commit, git_dirty=True)
            self.writer = supervisor.RunStatusWriter.start(self.output,
                command='t1-execution-probe-v1', support='1', output_lock=self.lock)
            self.config = self.output / 'execution-budget.json'
            self.config.write_bytes(supervisor.encode(self.budget))
            self.config_sha = supervisor.sha(self.config.read_bytes())
            self.writer.event('RESOURCE_BUDGET', budget=self.budget)
            return self
        except BaseException:
            self.lock.release()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', choices=('storage', 'product'), required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--memory-mib', type=int, default=1536)
    parser.add_argument('--threads', type=int)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    inputs = json.loads(args.inputs.read_bytes())
    for binding in inputs['bindings'].values():
        path = ROOT / binding['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError('changed measurement dependency: ' + binding['path'])
    budget = policy.resolve_resources(memory_mib=args.memory_mib, threads=args.threads,
                                     required_bytes=512 * policy.MIB)
    program = HERE / ('probe-' + args.probe + '-v1.py')
    with ProbeExecution(args.output_dir, budget) as execution:
        execution.run(args.probe, program,
            ['--inputs', args.inputs.resolve(), '--output', (args.output_dir / 'result.json').resolve()],
            kind='fixture')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
