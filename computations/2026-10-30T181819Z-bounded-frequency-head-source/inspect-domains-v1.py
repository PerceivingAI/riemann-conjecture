"""Inspect both supported full-source tile layouts without importing numerical libraries."""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import QuantityKey, bind_problem, canonical_bytes
from scripts.whole_source.pipeline import prepare_source_inputs, _bind, _tiles, _admit_transport, FAMILIES
from scripts.whole_source.artifacts import _coordinates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    problem = bind_problem('retained-t081')
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    layouts = []
    for width in (16,32):
        inputs = prepare_source_inputs(problem,args.output_dir/('tile-'+str(width)),
            origin_git_commit=revision,origin_git_dirty=True,tile_modes=width)
        _,_,roles = _bind(inputs['problem'],inputs['execution'],ROOT)
        spec,plan = roles['producer']
        _admit_transport(args.output_dir/('source-'+str(width)),spec,plan,False)
        count = 0
        for name in FAMILIES.values():
            for parity in (0,1):
                expected = {(m,n) for m in range(parity,problem.N,2) for n in range(m,problem.N,2)}
                seen = set()
                for task in _tiles(spec,QuantityKey(name,parity)):
                    for pair in _coordinates(task,True):
                        if pair in seen:
                            raise ValueError('overlapping canonical source tiles')
                        seen.add(pair)
                if seen != expected:
                    raise ValueError('incomplete canonical upper source domain')
                count += len(seen)
        if count != 512946:
            raise ValueError('incorrect complete source coordinate count')
        d,h = problem.N//2,(problem.M-problem.N)//2
        kernel_tiles = len(list(_tiles(spec,QuantityKey('kernel_complete',0))))
        row_blocks = (d+width-1)//width
        layouts.append({'tile_modes':width,'source_entries':count,'head_modes_per_parity':h,
            'kernel_tiles_per_parity':kernel_tiles,
            'kernel_anchor_passes':len(problem.frequency_edges),
            'kernel_tile_publications_per_parity':kernel_tiles,
            'kernel_tile_rereads_per_parity_for_full_Y':d*kernel_tiles,
            'final_cache_column_decodes_per_parity':3*row_blocks*d,
            'compact_cache_records_per_role':2*((d+h)*d+2*h*d+h*(h+1)//2),
            'scope':'EXACT_LOGICAL_DOMAIN_AND_DERIVED_TRAVERSAL_COUNTS_ONLY'})
    if any(name in sys.modules for name in ('flint','numpy','scipy')):
        raise RuntimeError('metadata inspection imported numerical libraries')
    result = {'status':'PASS_COMPLETE_SOURCE_DOMAIN_AND_TRANSPORT_INSPECTION','layouts':layouts,
              'native_verification_executed':False,'resource_admission_executed':False,
              'full_source_run':False,'matrix_positivity':False,'production_admission':False}
    (args.output_dir/'inspection.json').write_bytes(canonical_bytes(result))
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
