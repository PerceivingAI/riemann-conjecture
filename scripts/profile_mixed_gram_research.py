"""Research-only timing and Arb-width profile for the combined mixed Gram."""
from __future__ import annotations
import argparse
import time
from fractions import Fraction
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.mixed_gram_research import (
    assemble_truncated_mixed_gram, rigorous_full_gram_upper,
)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--dimension",type=int,required=True)
    parser.add_argument("--precision",type=int,default=384)
    parser.add_argument("--order",type=int,default=32)
    args=parser.parse_args()
    start=time.perf_counter()
    r=assemble_truncated_mixed_gram(
        n=args.dimension,prec=args.precision,residual_order=args.order)
    print("N",args.dimension,"SECS",round(time.perf_counter()-start,3),flush=True)
    for name in ("VP","PRk","VRk","Gk"):
        a=r[name]
        widths=[
            arb_to_rational_enclosure(a[i][j])[1]-arb_to_rational_enclosure(a[i][j])[0]
            for i in range(args.dimension) for j in range(i,args.dimension)]
        width=max(widths)
        print("PART",name,"MAX_WIDTH_APPROX",float(width),
              "DIAG00",a[0][0],flush=True)
    bound=rigorous_full_gram_upper(r,eta=Fraction(1,1<<24))
    print("FULL_MAJORANT_00",float(bound["upper"][0][0]),flush=True)


if __name__=="__main__":
    main()
