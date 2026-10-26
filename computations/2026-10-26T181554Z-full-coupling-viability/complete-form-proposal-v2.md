# Enclosure-aware proposal in the unchanged whole constrained low space

- **Created:** 2026-10-26T18:38:45Z
- **Last updated:** 2026-10-26T18:45:46Z

The first proposal minimizes the old bounded-source low value, not its full actual-Weil upper. It is not a sign authority. The second proposal optimizes the DECLARED COMPLETE Sobolev upper minus the SAME residual floor, on the SAME degree<=311 endpoint-order4 space. No support, projection, frequency anchor, coefficient grid, precision or threshold is increased. Both proposal/source versions and outcomes remain preserved.

Use f_j=(1-x²)^4 P_j^(4,4). Rodrigues' derivative identity gives

    f_j=16(j+1)(j+2)(j+3)(j+4)P_(j+4).

Thus the physical fourth-derivative Gram is exactly diagonal, entry256[(j+1)(j+2)(j+3)(j+4)]²*2/(2j+9). Let M be its physical mass matrix and E this diagonal divided by2*192^8. The floating proposal solves the complete deficit A_H0+E-(1/30000000000)M, preconditioned by positive M+E. It generates exact40-bit rational Jacobi coefficients only. The standalone source reconstructs their exact polynomial, old actual bounded-source interval, full Sobolev and finite endpoint exterior bounds and physical Rayleigh quotient. The independent consumer must reconstruct everything afresh. A floating negative deficit is not a certificate.

## Display correction, 2026-10-26T18:45:46Z

The original displayed identity above omits the fourth derivative on the left. Its corrected form is:

    d^4 f_j/dx^4 = 16(j+1)(j+2)(j+3)(j+4)P_(j+4).

The proposal code, derivative Gram, exact scalar source and independent consumer already use this fourth-derivative identity. No program, input, bound or numerical result changes. The original display is retained as historical context, not a valid equality for f_j itself.
