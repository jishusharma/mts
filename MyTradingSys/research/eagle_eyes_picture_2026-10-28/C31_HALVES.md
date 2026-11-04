# C31 halves: daily BB-edge short, 50-day trend down (2026-11-04)

**Verdict: UNDERPOWERED.** The lead parks; nothing trades. 14 of 15 trades sit in 2022-23, 1 in 2024-25: there is no second half to test.

Context: BTCUSDT daily from 1m, 2022-01..2025-06 (HOLDOUT sealed). Rule = a close above the upper BB(20,2) within the last 3 candles, then short; trend = prior close under the 50-day SMA. Stop = prior high, target = BB middle, 20-candle hold (all OURS, operator teaching 11-03).
Regime mix: 2022 bear 9 trades, 2023 range 5, 2024 bull 0, 2025 H1 1; the filter fires almost only in a downtrend, so the lead is a bear-market trade. Unfiltered (trend up) trades are 2023-25, mostly bull.

Script: `c31_halves.py` (asserts the reference numbers first, exit 1 if not reproduced). Fee-net per FORMULAS.md 18.5: taker per side from fees.py + 2 bps slip round trip (FORMULAS section 13, slip = OURS), divided by the stop distance.

## Reference (reproduced)
LEAD trend down: 73% to middle, +1.10 R fee-free, n=15. Unfiltered edge short: 21%, -0.07 R, n=165.

## Rule A (original: entry = price trades under the prior close, stop prev high)
| Set | Half | n | target | gross R | fee-net R | sd R |
|---|---|---|---|---|---|---|
| edge, trend down (LEAD) | 2022-23 | 14 | 71% | +1.17 | +1.09 | 1.88 |
| | 2024-25 | 1 | 100% | +0.06 | +0.04 | - |
| | total | 15 | 73% | +1.10 | +1.02 | 1.83 |
| edge, trend up | 2022-23 | 77 | 18% | +0.10 | -0.02 | 3.07 |
| | 2024-25 | 73 | 14% | -0.49 | -0.65 | 1.64 |
| | total | 150 | 16% | -0.19 | -0.32 | 2.49 |
| base (no edge), trend down | 2022-23 | 63 | 44% | -0.20 | -0.39 | 1.15 |
| | 2024-25 | 27 | 48% | +0.18 | +0.01 | 1.67 |

## Rule B (entry = first close back inside the band, stop = highest high of the walk, target = BB middle)
| Set | Half | n | target | gross R | fee-net R |
|---|---|---|---|---|---|
| edge, trend down | 2022-23 | 4 | 100% | +1.51 | +1.46 |
| | 2024-25 | 1 | 100% | +0.06 | +0.04 |
| | total | 5 | 100% | +1.22 | +1.17 |
| edge, trend up | total | 34 | 24% | -0.25 | -0.31 |

## Power
One-sided alpha 0.05, power 0.80: n = ((1.645+0.842) x sd / effect)^2, sd from the sample.
- Rule A lead: the observed +1.02 R needs n=20 (we have 15, 14 from one regime). The sd is 1.83, so a +0.30 R effect needs n=230.
- Rule B: observed effect needs n=5 but n=5 is noise; +0.30 R needs n=79 (5 here).
- Neither half-split is testable: 2024-25 holds 1 trade. At about 5 trend-down edge trades a year, n=230 needs ~45 years of BTC daily.
- Unfiltered rule fails fee-net in both halves (-0.02 / -0.65), so the filter carries all of the claim.

## Conclusion
Decision: UNDERPOWERED (a 15-trade, one-regime lead, selected after seeing the data). Park; no live or testnet use. Re-open only with more symbols (daily BB-edge shorts in downtrends across other pairs) or a longer BTC history; the 2024-25 half has to contain at least ~10 trend-down edge trades before a halves test means anything. DECISION (OURS): slip 2 bps on; Rule B stop = walk high; hold 20 candles unchanged; no tuning.
