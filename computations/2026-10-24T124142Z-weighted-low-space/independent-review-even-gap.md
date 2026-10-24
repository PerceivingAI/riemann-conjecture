Confirmed from `even-gap-v1.py`: the normalization and gap implication are correct.

The exact witness is nonsingular and establishes \(WL_{\mathrm{even}}W^T\succeq\eta I\). The script correctly computes
\[
t=\operatorname{tr}(WD_{\mathrm{even}}W^T)
=\sum_{i,j}W_{ij}^{2}\frac{2}{2\,\mathrm{degree}_j+1},
\]
using degrees \(0,2,\ldots,190\). Since \(WD_{\mathrm{even}}W^T\preceq tI\), invertible congruence yields
\[
S_{0,\mathrm{even}}\succeq L_{\mathrm{even}}
\succeq \frac{\eta}{t}D_{\mathrm{even}}.
\]

Transfer to the true Schur even block follows under C-0072’s hypotheses. The exact rational receipt certifies \(g=\eta/t\); the decimal is display-only unless explicitly rounded downward. This establishes no odd-block, full-Weil, admission, or RH conclusion. No execution performed.
