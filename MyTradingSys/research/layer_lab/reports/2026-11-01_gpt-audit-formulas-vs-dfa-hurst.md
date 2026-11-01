# Audit: FORMULAS.md s27 Rolling DFA Hurst vs dfa.py (2026-11-01)

Verdict: **SAME** (3 hand values re-derived from mathematical specification and compared with code). Report only; no code edited.

## Formulas

| Formula / Concept | FORMULAS.md | Code (`research/fractals_2026-10-31/f2/dfa.py`) | Status |
|---|---|---|---|
| Demeaned profile $y_j = \sum_{i \le j} (x_i - \bar{x})$ | s27 (lines 594) | `dfa.py:19` | SAME |
| Box partitioning: $nb = \lfloor n / s \rfloor$ boxes of $s$ points | s27 (lines 594) | `dfa.py:20-21` | SAME |
| Box least-squares line fit: $a + b(t - \bar{t})$, $b = \frac{\sum (y - \bar{y})(t - \bar{t})}{\sum (t - \bar{t})^2}$ | s27 (lines 594, 596) | `dfa.py:22-24` | SAME |
| Mean squared residual: $F^2(s) = \frac{1}{nb} \sum_{k=1}^{nb} \frac{1}{s}\sum_{t=0}^{s-1} (y_t - \hat{y}_t)^2$ | s27 (lines 594, 596) | `dfa.py:25-26` | SAME |
| Scaling sizes: $s \in \{8, 16, 32, 60, 96, 160\}$ | s27 (lines 594) | `dfa.py:8` | SAME |
| Exponent $\alpha = H$: OLS slope of $\ln F(s) = 0.5 \ln F^2(s)$ on $\ln s$ | s27 (lines 594) | `dfa.py:30-32, 46-47` | SAME |
| Window length $W = 480$ (20 days) and no look-ahead causality | s27 (lines 594) | `dfa.py:7, 35-48` | SAME |

## Hand Re-Derivations

Toy test series: alternating increments $x = [+1, -1, +1, -1, +1, -1, +1, -1, +1, -1, +1, -1, +1, -1, +1, -1]$ (length $n = 16$, mean $\bar{x} = 0$).
Cumulative demeaned profile: $y = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]$.
For any even scale $s$, $y$ repeats $[1, 0]$ with mean $\bar{y} = 0.5$. With $tm = t - \frac{s-1}{2}$, $\sum tm^2 = \frac{s(s^2-1)}{12}$, and $\sum (y - \bar{y}) tm = -\frac{s}{4}$, the closed-form box MSE simplifies analytically to:
$$F^2(s) = \frac{s^2 - 4}{4(s^2 - 1)}$$

### Output 1: Scale $s = 4$ worked example
- Analytical value: $F^2(4) = \frac{4^2 - 4}{4(4^2 - 1)} = \frac{12}{60} = \frac{1}{5} = 0.20$.
- Step-by-step:
  - $t = [0, 1, 2, 3]$, $\bar{t} = 1.5$, $tm = [-1.5, -0.5, 0.5, 1.5]$, $\sum tm^2 = 5.0$.
  - $\sum (y \cdot tm) = 1(-1.5) + 0 + 1(0.5) + 0 = -1.0$.
  - Slope $b = -1.0 / 5.0 = -0.2$.
  - Fitted line: $\hat{y} = [0.8, 0.6, 0.4, 0.2]$.
  - Residuals: $y - \hat{y} = [0.2, -0.6, 0.6, -0.2]$.
  - Squared residuals: $[0.04, 0.36, 0.36, 0.04]$, mean $= 0.80 / 4 = 0.20$.
- Code output (`dfa.fluct2(x, 4)[0]`): $0.2000000000000000$.

### Output 2: Scale $s = 8$ box fit on 16-point toy series
- Number of boxes: $nb = 16 // 8 = 2$ identical boxes.
- Analytical value: $F^2(8) = \frac{8^2 - 4}{4(8^2 - 1)} = \frac{60}{252} = \frac{5}{21} \approx 0.2380952380952381$.
- Step-by-step:
  - $t = [0, \dots, 7]$, $\bar{t} = 3.5$, $\sum tm^2 = 42.0$.
  - $\sum (y \cdot tm) = -3.5 - 1.5 + 0.5 + 2.5 = -2.0$.
  - Slope $b = -2.0 / 42.0 = -1/21 \approx -0.0476190476190476$.
  - Residuals: $y - \hat{y} = [1/3, -13/21, 3/7, -11/21, 11/21, -3/7, 13/21, -1/3]$.
  - Residual sum of squares: $2 \times (1/9 + 169/441 + 9/49 + 121/441) = 2 \times (420 / 441) = 40/21$.
  - Mean square per box: $\frac{1}{8} \times \frac{40}{21} = \frac{5}{21} \approx 0.2380952380952381$.
- Code output (`dfa.fluct2(x, 8)[0]`): $0.23809523809523814$ (diff $= 5.55 \times 10^{-17}$).

### Output 3: Log-log slope (DFA Hurst exponent $\alpha$) over two scales
- Scales: $s_1 = 4, s_2 = 8$.
- Derivation:
  $$\alpha = \frac{\ln F(s_2) - \ln F(s_1)}{\ln s_2 - \ln s_1} = \frac{\frac{1}{2}\ln F^2(8) - \frac{1}{2}\ln F^2(4)}{\ln 8 - \ln 4} = \frac{\frac{1}{2}\ln\left(\frac{5/21}{1/5}\right)}{\ln 2} = \frac{\ln(25/21)}{2\ln 2} = \frac{\ln(25/21)}{\ln 4}$$
- Hand calculation: $\alpha = \frac{\ln(1.19047619047619)}{1.38629436111989} \approx 0.1257693834979822$.
- Code output (`dfa.dfa_alpha(x, scales=(4, 8))`): $0.1257693834979819$ (diff $= 3.05 \times 10^{-16}$).

## Comparison Summary

| Output | FORMULAS.md | Code Reference | Hand Value | Code Value | Result |
|---|---|---|---|---|---|
| $s=4$ worked example $F^2(4)$ | s27 (line 596) | `dfa.py:11-26` (`fluct2`) | $0.200000000000$ | $0.200000000000$ | **SAME** |
| $s=8$ box fit on 16-pt series $F^2(8)$ | s27 (lines 594, 596) | `dfa.py:11-26` (`fluct2`) | $5/21 \approx 0.238095238095$ | $0.238095238095$ | **SAME** |
| Log-log slope $\alpha$ over $s \in (4, 8)$ | s27 (lines 594, 596) | `dfa.py:29-33` (`dfa_alpha`) | $\frac{\ln(25/21)}{\ln 4} \approx 0.125769383498$ | $0.125769383498$ | **SAME** |

Noticed: the closed-form formula $F^2(s) = \frac{s^2-4}{4(s^2-1)}$ governs any even scale $s$ on alternating $+1, -1$ returns and approaches $1/4 = 0.25$ asymptotically as $s \to \infty$.
