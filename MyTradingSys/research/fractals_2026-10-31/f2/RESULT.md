# F2 RESULT: rolling 1h DFA Hurst regime gate on RSI-DIV-MTF and the F1 pivot fade (fee-net, DEV)

**Verdict: NEGATIVE.** No test passes. A low-H (mean-reverting) gate does not lift either mean-reversion layer; on the F1 fade it points the wrong way (borderline). The trend-drop gate (keep H <= 0.55) lifts nothing reliably. PRE_REG.md was committed (d94529dce) before any event outcome was joined to H; nothing was tuned after. Data: BTCUSDT 1m 2022-01-01..2025-06-30 (files after 2025-06 never opened). r_net columns already carry the all-taker round trip (P1b, F1). H = DFA-1, W = 480 hourly returns, scales 8..160, known at the close of its last bar (FORMULAS.md s27). Output of `run_f2.py`: `output.md`.

## Numbers (lift = mean net R kept minus removed; CI = week-block bootstrap 95 %)
| test | layer | gate | n kept | n removed | kept net R [CI] | lift [CI] | lift S1 / S2 | C1 shuffled-H p | C2 random p | C3 flag | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F2-1 | RSI-DIV-MTF | keep H < 0.45 | 119 | 515 | -0.305 [-0.524, -0.101] | -0.092 [-0.345, +0.145] | -0.154 / +0.026 | 0.761 | 0.765 | no | NOT_DECIDABLE (kept n < 200) |
| F2-2 | RSI-DIV-MTF | keep H <= 0.55 | 484 | 150 | -0.201 [-0.325, -0.067] | +0.123 [-0.109, +0.358] | +0.241 / -0.308 | 0.188 | 0.170 | no | INCONCLUSIVE |
| F2-3 | F1 fade | keep H < 0.45 | 1614 | 5678 | -0.289 [-0.347, -0.229] | -0.062 [-0.129, -0.0006] | -0.113 / -0.009 | 0.975 | 0.987 | no | FAIL (CI upper < 0, borderline) |
| F2-4 | F1 fade | keep H <= 0.55 | 6032 | 1260 | -0.244 [-0.276, -0.212] | -0.020 [-0.090, +0.047] | -0.018 / -0.015 | 0.723 | 0.744 | no | INCONCLUSIVE |

- Regime switches (runs >= 24 h) per split: 74 / 109 (gate A), 109 / 73 (gate B): the >= 10 switches gate is met everywhere, so a thin-regime story does not explain the null.
- C3 family-wise (1,000 circular shifts of the H series, max over 4 tests): 95th percentile of the null max lift = +0.271 R; the largest observed lift is +0.123. Nothing is flagged.
- Every kept side stays negative after fees (best kept side -0.20 R), so even a real lift would not make a tradable gate.
- Events: RSI 634 of 640 and F1 fade 7,292 of 7,416 had an H value (the rest fall in the 20-day warm-up).
- Power: sd of net R per event 1.33 (RSI) and 1.01 (fade); n per cell for a 0.17 R effect at 80 % power = 483 (RSI) and 276 (fade).

## Planted-edge check (cells demeaned first, real H and event times)
| scenario | C3 flags | planted CI |
|---|---|---|
| no plant | none | - |
| +0.25 R on RSI gate A kept (pre-registered) | none (threshold 0.279 vs lift 0.250) | F2-1 [-0.004, +0.487] |
| +0.50 R on RSI gate A kept (extra) | F2-1 | [+0.246, +0.737] |
| +0.25 R on F1 fade gate A kept (extra) | none by C3 (threshold 0.279 vs 0.250) | F2-3 [+0.183, +0.311] |

The pre-registered plant (+0.25 R on RSI) was NOT flagged by C3 and its CI just touches zero: with only 119 kept RSI events the pipeline cannot see a 0.25 R lift, so the RSI verdicts say "not shown", not "absent". The raw-lift family-wise max is also dominated by the noisy RSI tests (threshold 0.28 R), which makes C3 weak for the fade tests too; for the fade the per-test CI is the better yardstick and it detects the same plant cleanly (CI +0.18..+0.31, n = 7,292). A studentised max would fit better and is a NEW trial if anyone wants it.

## Reading
- Kept events at low H (H < 0.45, anti-persistent hours) do slightly worse for the fade: lift -0.062 R, CI upper bound -0.0006. With 4 tests that borderline FAIL is not a finding on its own; both splits point the same way (-0.113, -0.009) and the shuffled-H p is 0.975 on the wrong side, so no claim of a reverse effect either.
- The vendor cut-offs 0.45 / 0.55 (ANECDOTE) on a 20-day DFA window show no fee-net value for these two layers on DEV. The DFA window understates H (R1 s1b), thresholds were not bias-corrected, and a different window or surrogate-based quantile thresholds would be new trials with new pre-regs; none was run.
- No gate, layer or rule is added.

Noticed: the reusable gate harness (lookup of a past-only series at event times, shuffled / random / circular-shift nulls) lives in `run_f2.py` and fits any other regime variable (e.g. the phase tags) with a different `TESTS` list.
