**T12 funding extreme reversal: Cell A (long) FAIL, Cell B (short) FAIL; overall KILL (dead at the daily level). VAL n 125 / 611, price-only net -0.079 R / -0.036 R.**

Regime mix: share of trades by BTC smoothed cycle state at the signal day (BULL/BASE/BEAR). Cell A DEV 5%/10%/85%; Cell A VAL 27%/5%/68%; Cell B DEV 20%/67%/13%; Cell B VAL 70%/21%/9%.

Protocol: PRE_REG.md frozen and committed before any outcome. Primary metric mean R per trade (risk unit = stop distance); price-only net = gross - 12 bp fee; total net adds real signed funding. Survivorship direction: longs biased UP, shorts biased DOWN (hindsight list of listed coins).

## Summary table

| Cell | Split | n | weeks | gross R | fee R | funding R | price-only net R | total net R | gross % | price-only net % | total net % | carry bp/trade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A long | DEV | 296 | 72 | 0.105 | 0.0054 | -0.018 | 0.099 | 0.117 | 3.18 | 3.06 | 3.47 | -40.7 |
| A long | VAL | 125 | 43 | -0.072 | 0.0065 | -0.095 | -0.079 | 0.016 | -1.54 | -1.66 | 0.40 | -205.9 |
| B short | DEV | 608 | 55 | -0.112 | 0.0071 | -0.024 | -0.119 | -0.095 | -2.41 | -2.53 | -2.03 | -50.5 |
| B short | VAL | 611 | 69 | -0.029 | 0.0070 | -0.012 | -0.036 | -0.024 | -0.68 | -0.80 | -0.56 | -23.3 |

## Bars (price-only net R, VAL unless stated)

| # | Bar | Cell A | Cell B |
|---|---|---|---|
| 1 | VAL n>=30 and >=20 weeks | PASS | PASS |
| 2 | VAL mean>0 and block-bootstrap CI low>0 | FAIL | FAIL |
| 3 | DEV mean>0 | PASS | FAIL |
| 4 | placebo (same-window, price-only): real >= p97.5 and excess>0 | FAIL | FAIL |
| 5 | ex-best-5 weeks (ex-best-2 if <30 weeks) mean>0 | FAIL | FAIL |
| 6 | baseline basket per day in position | FAIL | FAIL |
| 7 | top-3 coin removal mean>0 | FAIL | FAIL |
| 8 | leave-one-year-out all>0 | FAIL | FAIL |
| 9 | rows by cycle and year printed; SIGN-FLIP | no flip | no flip |

Verdict A: FAIL (first failing bar: 2). Verdict B: FAIL (first failing bar: 2).
Bars passed A: 1,3; failed A: 2,4,5,6,7,8. Bars passed B: 1; failed B: 2,3,4,5,6,7,8.

## Statistics detail

| Item | Cell A | Cell B |
|---|---|---|
| Block bootstrap VAL price-only (R) | mean -0.079, CI [-0.268, 0.141], p(<=0) 0.7551, weeks 43, week sd 0.745 | mean -0.036, CI [-0.309, 0.236], p(<=0) 0.5972, weeks 69, week sd 0.587 |
| Block bootstrap VAL total (R) | mean 0.016, CI [-0.189, 0.261], p(<=0) 0.4163, weeks 43, week sd 0.799 | mean -0.024, CI [-0.293, 0.244], p(<=0) 0.5677, weeks 69, week sd 0.581 |
| Block bootstrap DEV price-only (R) | mean 0.099, CI [-0.104, 0.273], p(<=0) 0.1854, weeks 72, week sd 0.707 | mean -0.119, CI [-0.373, 0.157], p(<=0) 0.8271, weeks 55, week sd 0.658 |
| Block bootstrap DEV total (R) | mean 0.117, CI [-0.085, 0.291], p(<=0) 0.1279, weeks 72, week sd 0.715 | mean -0.095, CI [-0.346, 0.181], p(<=0) 0.7866, weeks 55, week sd 0.646 |
| placebo +/-8 wk price-only | n 118 (skipped 7), real -0.096, draws -0.012, p97.5 0.080, excess -0.084, p 0.9580 | n 602 (skipped 9), real -0.035, draws -0.075, p97.5 -0.020, excess 0.040, p 0.0669 |
| placebo +/-8 wk total | n 118 (skipped 7), real 0.004, draws 0.037, p97.5 0.138, excess -0.033, p 0.7373 | n 602 (skipped 9), real -0.023, draws -0.058, p97.5 -0.003, excess 0.035, p 0.0959 |
| placebo global price-only | n 123 (skipped 2), real -0.075, draws 0.019, p97.5 0.131, excess -0.094, p 0.9570 | n 609 (skipped 2), real -0.035, draws -0.088, p97.5 -0.025, excess 0.053, p 0.0539 |
| placebo global total | n 123 (skipped 2), real 0.022, draws 0.077, p97.5 0.202, excess -0.056, p 0.8252 | n 609 (skipped 2), real -0.023, draws -0.070, p97.5 -0.006, excess 0.047, p 0.0819 |
| Ex-best weeks price-only (k, n, mean) | k 5, n 110, -0.232 | k 5, n 469, -0.287 |
| Ex-best weeks total | -0.166 | -0.272 |
| Top-3 coin removal price-only | AXSUSDT -> -0.122 (n 123); AXSUSDT+ENJUSDT -> -0.161 (n 120); AXSUSDT+ENJUSDT+ONTUSDT -> -0.191 (n 117) | ONEUSDT -> -0.045 (n 597); ONEUSDT+KAVAUSDT -> -0.054 (n 577); ONEUSDT+KAVAUSDT+ZILUSDT -> -0.061 (n 566) |
| Top-3 coin removal total | AXSUSDT -> -0.039; AXSUSDT+ENJUSDT -> -0.096; AXSUSDT+ENJUSDT+ONTUSDT -> -0.139 | ONEUSDT -> -0.033; ONEUSDT+ZILUSDT -> -0.040; ONEUSDT+ZILUSDT+KAVAUSDT -> -0.048 |
| Leave-one-year-out price-only | -2024: -0.073; -2025: -0.013; -2026: -0.181 | -2024: 0.187; -2025: -0.240; -2026: -0.007 |
| Baseline | trade price -0.984%/d vs basket -0.200%/d (ok False); trade total -0.698%/d vs basket 0.129%/d; carry basket -32.93 bp/d (326 days) | trade price -0.999%/d vs basket -0.002%/d (ok False); trade total -0.972%/d vs basket 0.033%/d; carry basket -3.52 bp/d (539 days) |
| Ex-ENDED (VAL, price/total, n) | -0.079 / 0.016, n 125, ended 0 | -0.036 / -0.024, n 608, ended 3 |
| Ex-LUNA/FTT (VAL, price/total, n) | -0.079 / 0.016, n 125, dropped 0 | -0.031 / -0.019, n 583, dropped 28 |
| Exit reasons VAL | {'TIME': 100, 'STOP': 25, 'STOP-GAP': 0, 'ENDED': 0} | {'TIME': 420, 'STOP': 188, 'STOP-GAP': 0, 'ENDED': 3} |
| Median stop % VAL | 20.4 | 17.6 |
| SIGN-FLIP read (opposite / aligned mean) | -0.332 / 0.016 | -0.055 / -0.034 |

Holm over the two cells (bar-2 one-sided p, adjusted): A 1.0000, B 1.0000. Wave-3 family (9 cells) worst case min(1, 9p): A 1.0000, B 1.0000; the coordinator completes the family Holm.
Kill criteria: (a) both VAL price-only <= 0 with bar 1: True; (b) both placebo <= p97.5 with >= 100 trades: True; killed: True.

## Cell A DEV rows by BTC cycle, year, phase label (n / price-only R / total R)

| Group | Key | n | price-only R | total R |
|---|---|---|---|---|
| cycle | BASE | 29 | 0.070 | 0.138 |
| cycle | BEAR | 252 | 0.104 | 0.116 |
| cycle | BULL | 15 | 0.076 | 0.085 |
| year | 2020 | 5 | 0.416 | 0.498 |
| year | 2021 | 52 | 0.295 | 0.303 |
| year | 2022 | 191 | 0.014 | 0.028 |
| year | 2023 | 48 | 0.191 | 0.229 |
| label | ACCUM-RANGE | 47 | 0.105 | 0.154 |
| label | CAPITULATION | 63 | 0.123 | 0.133 |
| label | MARKDOWN | 178 | 0.120 | 0.132 |
| label | RELIEF | 8 | -0.579 | -0.561 |

## Cell B DEV rows by BTC cycle, year, phase label (n / price-only R / total R)

| Group | Key | n | price-only R | total R |
|---|---|---|---|---|
| cycle | BASE | 408 | -0.115 | -0.095 |
| cycle | BEAR | 78 | -0.150 | -0.143 |
| cycle | BULL | 122 | -0.113 | -0.067 |
| year | 2020 | 37 | 0.016 | 0.067 |
| year | 2021 | 112 | -0.105 | -0.057 |
| year | 2022 | 28 | 1.274 | 1.277 |
| year | 2023 | 431 | -0.225 | -0.208 |
| label | DISTRIBUTION | 61 | 0.879 | 0.885 |
| label | MARKUP | 547 | -0.231 | -0.204 |

## Cell A VAL rows by BTC cycle, year, phase label (n / price-only R / total R)

| Group | Key | n | price-only R | total R |
|---|---|---|---|---|
| cycle | BASE | 6 | 0.010 | 0.065 |
| cycle | BEAR | 85 | 0.016 | 0.134 |
| cycle | BULL | 34 | -0.332 | -0.287 |
| year | 2024 | 12 | -0.127 | -0.120 |
| year | 2025 | 45 | -0.196 | -0.118 |
| year | 2026 | 68 | 0.008 | 0.129 |
| label | ACCUM-RANGE | 23 | 0.552 | 0.768 |
| label | CAPITULATION | 7 | -0.159 | -0.150 |
| label | MARKDOWN | 86 | -0.219 | -0.155 |
| label | RELIEF | 9 | -0.287 | -0.136 |

## Cell B VAL rows by BTC cycle, year, phase label (n / price-only R / total R)

| Group | Key | n | price-only R | total R |
|---|---|---|---|---|
| cycle | BASE | 130 | -0.505 | -0.483 |
| cycle | BEAR | 56 | -0.055 | -0.049 |
| cycle | BULL | 425 | 0.110 | 0.120 |
| year | 2024 | 309 | -0.253 | -0.235 |
| year | 2025 | 208 | 0.359 | 0.365 |
| year | 2026 | 94 | -0.195 | -0.187 |
| label | DISTRIBUTION | 146 | 0.364 | 0.368 |
| label | MARKUP | 465 | -0.161 | -0.147 |

## OI terciles (descriptive, 20 coins with OI, DEV+VAL pooled, 7-day OI change at the signal day; no verdict)

| Cell | tercile | n | price-only R | total R |
|---|---|---|---|---|
| A | low | 34 | -0.203 | -0.188 |
| A | mid | 34 | -0.051 | -0.033 |
| A | high | 34 | -0.091 | -0.077 |
| B | low | 87 | -0.312 | -0.295 |
| B | mid | 86 | 0.055 | 0.072 |
| B | high | 86 | -0.069 | -0.047 |

Skipped signals: A {'no_funding': 1}, B {'no_funding': 2}. Trades csv bytes 172739 (kept in the folder if under 1 MB).
## Mechanical notes (logged after the run, nothing re-run, no rule changed)

- Bar 6 as frozen in PRE_REG is the mean over trades of (price-only net % / days held). That mean of ratios is dominated by early stops (a stop on day 1 prints about -20% per day), so the trade figures above (-0.98 and -1.00 %/day) are not comparable to the basket in an economic sense. Descriptive recompute from trades.csv as a ratio of sums (sum of price-only net % / sum of days held), NOT used in any verdict: Cell A VAL -0.186 %/day vs basket -0.200 (would read as ok), Cell B VAL -0.092 %/day vs basket -0.002 (fails either way). The verdicts do not change: bar 2 is the first failing bar in both cells and bars 4, 5, 7, 8 also fail in both.
- Placebo Cell B reads excess +0.040 R price-only (real -0.035, draws -0.075) with real below the 97.5th percentile (-0.020): the entry bar beats random flagged days a little but still loses money; not a pass.
- Gate: measured DEV week-level sd of price-only R is 0.71 (A) and 0.66 (B), below the 1.0 floor used in the PRE_REG gate.
- run.log is the console log of t12_run.py (priority proof: BelowNormal 0x4000 took) and is not committed.

## Adversarial check

Flag: **MINOR**. Final verdict: **FAIL (both cells)** (checker re-derived the same verdict).

- Order clean (87851f68d before 7bfe1df4b); only result files changed after.
- Spec fidelity matches the design; disclosed deviations: F3 is sum/9 with >= 3 prints per day, power-gate sd floor 1.0, calendar-week moving-block bootstrap, builder-frozen baseline/LOYO definitions, measured stop 18-25% (not 6-12%).
- No look-ahead found.
- FAIL re-derived for both cells (first failing bar 2): A VAL price-only net -0.079 R, CI -0.268..+0.141; B -0.036 R, CI -0.309..+0.236; Holm 1.0.
- The ex-LUNA/FTT row is vacuous (those coins have no VAL trades). A FAIL under a BLOCKED power gate reads as untested, not proof of no edge.
- OI part not tested: daily OI exists for 20 of 68 coins only.
