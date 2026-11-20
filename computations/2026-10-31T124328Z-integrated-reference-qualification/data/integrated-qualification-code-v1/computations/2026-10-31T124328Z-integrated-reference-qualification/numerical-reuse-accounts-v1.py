"""Record legal source geometry accounts without importing numerical libraries."""
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source import pipeline,resources
from scripts.whole_source.contract import bind_problem,canonical_bytes
from scripts.whole_source.execution import _write
from scripts.whole_source.reuse import PREPARED_BYTES,SOURCE_DECODED_BYTES


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--origin-commit',required=True)
    args=parser.parse_args()
    output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    allocator=resources.auto_plan
    def allocate(template,*,parallel,memory_mib=None,helper_root=ROOT):
        return allocator(template,parallel=parallel,cpus=1,memory_mib=2048,helper_root=helper_root)
    rows=[]
    with patch.object(resources,'auto_plan',allocate):
        for tile in (16,32):
            inputs=pipeline.prepare_source_inputs(bind_problem('retained-t081'),output/f'tile-{tile}',
                tile_modes=tile,origin_git_commit=args.origin_commit,origin_git_dirty=True)
            problem,_,roles=pipeline._bind(inputs['problem'],inputs['execution'],ROOT)
            for role,(spec,plan) in roles.items():
                requirements=(pipeline._producer_requirements if role=='producer' else pipeline._analytic_requirements)(spec,False)
                rows.append({'tile_modes':tile,'role':role,'precision_bits':plan.precision_bits,
                    'private_mib':plan.worker_private_mib,'native_mib':plan.native_workspace_mib,
                    'derived_requirements':requirements,'catalog_bytes':spec.bounds.max_decoded_bytes,
                    'prepared_bytes':PREPARED_BYTES,'decoded_source_bytes':SOURCE_DECODED_BYTES})
    assert 'flint' not in sys.modules and 'numpy' not in sys.modules
    result={'status':'BOUND_LEGAL_SOURCE_REUSE_ACCOUNTS_ONLY','accounts':rows,
        'numerical_libraries_imported':False,'numerical_workers_started':False,
        'full_source_evaluated':False,'production_admission':False}
    _write(output/'result.json',canonical_bytes(result))
    print(json.dumps({'status':result['status'],'accounts':rows},sort_keys=True))


if __name__=='__main__':main()
