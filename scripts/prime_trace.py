"""High-precision cutoff study for the generalized prime-Laguerre trace.

This script computes P_n(X) and the pole-subtracted *cutoff diagnostic*
S_n(X)=P_n(X)-(1-q^n). S_n(X) is NOT the exact infinite S_n until cutoff
convergence has been demonstrated. The output therefore emphasizes cutoff
stability rather than presenting S_n(X) as a proof object.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, localcontext

if __package__:
    from scripts.rh_tools import nth_root_abs, pole_parameters, pole_term, prime_trace_snapshots
else:
    from rh_tools import nth_root_abs, pole_parameters, pole_term, prime_trace_snapshots


def fmt(value: Decimal, digits: int = 14) -> str:
    return f"{value:.{digits}E}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", default="3")
    parser.add_argument("--n-max", type=int, default=16)
    parser.add_argument("--cutoffs", default="10000,100000,1000000")
    parser.add_argument("--precision", type=int, default=60)
    args = parser.parse_args()

    try:
        s0 = Decimal(args.s0)
    except InvalidOperation:
        parser.error("s0 must be a decimal number")
    try:
        cutoffs = [int(v.strip()) for v in args.cutoffs.split(",") if v.strip()]
    except ValueError:
        parser.error("cutoffs must be comma-separated integers")
    if not s0.is_finite() or s0 <= 1:
        parser.error("s0 must be finite and > 1")
    if args.n_max < 1:
        parser.error("n-max must be >= 1")
    if args.precision < 1:
        parser.error("precision must be >= 1")
    if not cutoffs or any(cutoff < 2 for cutoff in cutoffs):
        parser.error("cutoffs must contain integers >= 2")

    with localcontext() as ctx:
        ctx.prec = args.precision
        A, q = pole_parameters(s0)
        snapshots = prime_trace_snapshots(
            s0=s0, n_max=args.n_max, cutoffs=cutoffs, precision=args.precision
        )
        cuts = sorted(snapshots)

        print(f"s0={s0} A={A} q={q} precision={args.precision}")
        print(f"cutoffs={','.join(str(c) for c in cuts)}")
        print("n cutoff P_n(X) S_n(X)=P-h root_abs_S delta_from_previous_cutoff")
        previous: dict[int, Decimal] = {}
        for cutoff in cuts:
            values = snapshots[cutoff]
            for n, pval in enumerate(values, start=1):
                h = pole_term(n, q)
                sval = pval - h
                root = nth_root_abs(sval, n)
                delta = sval - previous[n] if n in previous else Decimal("NaN")
                print(
                    f"{n:2d} {cutoff:9d} {fmt(pval)} {fmt(sval)} {fmt(root)} "
                    f"{fmt(delta) if delta.is_finite() else 'NA'}"
                )
                previous[n] = sval

        print("NOTE: S_n(X) is a cutoff diagnostic, not the exact infinite S_n.")
        print("Use stabilization across increasing cutoffs before interpreting a row numerically.")


if __name__ == "__main__":
    main()
