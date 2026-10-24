"""Standard-library endpoint replay, not fresh transcendental reconstruction."""
import copy
from fractions import Fraction as Q
import json
from pathlib import Path


def verify(result):
    source = result['source']
    den = 1 << source['publication_bits']
    count = 0
    for row in source['receipts']:
        for name in ('V','P','R32'):
            lo,hi = (Q(x) for x in row['reference'][name])
            left,right = (Q(x,den) for x in row[name])
            if not left <= lo <= hi <= right:
                raise ValueError('reference interval not contained')
            if (row['row']-row['column']) % 2 and (left != 0 or right != 0):
                raise ValueError('reflection parity mismatch')
            if name == 'R32' and row['row'] >= 224 and (left != 0 or right != 0):
                raise ValueError('residual polynomial degree mismatch')
            count += 1
    lo,hi = (Q(x) for x in source['delta_reference'])
    left,right = (Q(x,den) for x in source['delta'])
    if not 0 <= left <= lo <= hi <= right:
        raise ValueError('residual bound not contained')
    expected = [str(Q(2,2*j+1)) for j in (0,1,190,191)]
    if source['masses'] != expected:
        raise ValueError('physical-degree mass mismatch')
    return count+1


if __name__ == '__main__':
    result = json.loads((Path(__file__).parent/'data/probe-v1.stdout.json').read_text())
    count = verify(result)
    bad = copy.deepcopy(result)
    bad['source']['receipts'][0]['V'] = [0,0]
    try:
        verify(bad)
    except ValueError:
        rejected = True
    else:
        raise AssertionError('altered nonzero potential interval accepted')
    print(json.dumps({'status':'PASS','scalar_component_containments':count,
                      'altered_interval_rejected':rejected,
                      'scope':'serialized rational interval consequences only'}))
