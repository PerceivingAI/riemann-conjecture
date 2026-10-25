"""Exact rational geometry countercontrols; toy shifts are not a support probe."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def integral_product(a: tuple[Q, Q], b: tuple[Q, Q], left: Q, right: Q) -> Q:
    coefficients = (a[0]*b[0], a[0]*b[1]+a[1]*b[0], a[1]*b[1])
    return sum((v*(right**(k+1)-left**(k+1))/(k+1)
                for k,v in enumerate(coefficients)), Q())


def controls() -> dict:
    shifts = (Q(3,4), Q(7,5), Q(3,2))
    signed = tuple(s*direction for s in shifts for direction in (-1,1))
    points = sorted({Q(-1), Q(1)} | {Q(-1)-s for s in signed if -1 < -1-s < 1}
                    | {Q(1)-s for s in signed if -1 < 1-s < 1})
    if points != [Q(-1),Q(-1,2),Q(-2,5),Q(-1,4),Q(1,4),Q(2,5),Q(1,2),Q(1)]:
        raise ValueError('seven-cell rational topology failed')
    cell_square = [[Q() for _ in range(2)] for _ in range(2)]
    cell_low = [[Q() for _ in range(2)] for _ in range(2)]
    counts = []
    basis = ((Q(1),Q()), (Q(),Q(1)))
    for left,right in zip(points,points[1:]):
        midpoint = (left+right)/2
        active = [s for s in signed if -1 < midpoint+s < 1]
        counts.append(len(active))
        images = ((Q(-len(active)),Q()), (-sum(active,Q()),Q(-len(active))))
        for i in range(2):
            for j in range(2):
                cell_square[i][j] += integral_product(images[i],images[j],left,right)
                cell_low[i][j] += integral_product(basis[i],images[j],left,right)
    pair_square = [[Q() for _ in range(2)] for _ in range(2)]
    missing_central = Q()
    surviving = 0
    for alpha in signed:
        for beta in signed:
            left = max(Q(-1),Q(-1)-alpha,Q(-1)-beta)
            right = min(Q(1),Q(1)-alpha,Q(1)-beta)
            if left >= right:
                continue
            surviving += 1
            images_a = ((Q(1),Q()),(alpha,Q(1)))
            images_b = ((Q(1),Q()),(beta,Q(1)))
            for i in range(2):
                for j in range(2):
                    pair_square[i][j] += integral_product(images_a[i],images_b[j],left,right)
            if alpha == -beta and abs(alpha) == shifts[0]:
                missing_central += right-left
    if cell_square != pair_square or surviving != 20:
        raise ValueError('direct pair reconstruction disagrees with cell square')
    if cell_low[0][0] != Q(-47,10) or cell_square[0][0] != Q(121,10):
        raise ValueError('constant-polynomial physical values failed')
    if counts != [3,2,1,2,1,2,3] or missing_central != 1:
        raise ValueError('new central image-pair countercontrol failed')
    if cell_square[0][1] != 0 or cell_low[0][1] != 0 or cell_low[1][0] != 0:
        raise ValueError('unforced full-sum reflection parity failed')
    gram = cell_square[0][0]-cell_low[0][0]**2/2
    wrong_mass = cell_square[0][0]-cell_low[0][0]**2
    if gram != Q(211,200) or not wrong_mass < 0:
        raise ValueError('ordinary-mass consumer countercontrol failed')
    return {'toy_shifts':[str(s) for s in shifts], 'selected_support':False,
            'breakpoints':[str(p) for p in points], 'cell_counts':counts,
            'ordered_image_pairs':36, 'positive_length_pairs':surviving,
            'low_matrix':[[str(v) for v in row] for row in cell_low],
            'square_from_cells':[[str(v) for v in row] for row in cell_square],
            'square_from_pairs':[[str(v) for v in row] for row in pair_square],
            'omitted_central_pair_loss':str(missing_central),
            'wrong_omission_square':str(cell_square[0][0]-missing_central),
            'correct_mass_tail_Gram':str(gram), 'wrong_identity_mass_tail_Gram':str(wrong_mass),
            'off_parity_checked_before_projection':True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = {'format':'m4-rational-geometry-countercontrols-v1', 'controls':controls(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'positive_length_pairs':20,'correct_mass_tail_Gram':'211/200',
                      'omission_detected':True,'mass_error_detected':True,'support_probe':False}))
