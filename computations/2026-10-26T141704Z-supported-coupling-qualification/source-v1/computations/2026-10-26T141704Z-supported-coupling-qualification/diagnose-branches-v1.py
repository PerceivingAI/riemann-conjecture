"""Compare exact cell/shift branches with widened Arb storage branches."""
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path
from flint import arb,ctx


def aq(x):
    x=Q(x);return arb(x.numerator)/x.denominator


def endpoints(x):
    m=x.mid().fmpq();r=x.rad().fmpq()
    return Q(int((m-r).p),int((m-r).q)),Q(int((m+r).p),int((m+r).q))


def branch(lo,hi,T):
    return 'outside' if hi < -T or lo > T else 'inside' if lo >= -T and hi <= T else 'overlap'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    raw=args.source.read_bytes();packet=json.loads(raw);ctx.prec=384;T=Q(3,4)
    shifts=[sign*arb(m).log() for m in [2,3,4] for sign in [-1,1]];rows=[]
    for cell in packet['positive_half_cells']:
        left=Q(cell['left']);right=Q(cell['right']);u=aq(left).union(aq(right))
        for index,shift in enumerate(shifts):
            sl,sh=endpoints(shift);exact=branch(left-sh,right-sl,T);bl,bh=endpoints(u-shift);widened=branch(bl,bh,T)
            if exact!=widened:
                rows.append({'left':str(left),'right':str(right),'shift_index':index,'exact_branch':exact,'stored_ball_branch':widened})
    result={'format':'supported-source-branch-diagnostic-v1','source_sha256':hashlib.sha256(raw).hexdigest(),'precision_bits':384,'branch_disagreements':rows,
            'cause':'Arb interval storage may widen an exact partition endpoint across a jump. This makes the whole ball ambiguous although the exact cell is on one side. It is conservative, not an invalid source enclosure.'}
    with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'branch_disagreements':len(rows),'overlap_due_only_to_storage':sum(r['stored_ball_branch']=='overlap' and r['exact_branch']!='overlap' for r in rows)}))


if __name__=='__main__':main()
