# RESULT: level-approach prep base rates (U1 absorption, U2 OI tell, U3 wick count)

Regime mix: bull 29% / bear 21% / range 50% (887 prior-day H/L approaches, trailing 30-day return +-10 %, OURS)

Verdict: descriptive only, fee-free, no edge. Absorption (delta share >= +0.3 into the level, under 0.1 % extension) marks a STALL,
not a reversal: it reverses 18 % vs 27 % for distance-matched non-absorption approaches, and breaks 22 % vs 45 %. The OI tell does
not separate absorption outcomes (15-23 %, n 67-88 per group). Any wick rejection before the first touch lifts the hold rate from
18 % (no TF) to 23-25 % (1+ TFs); more TFs add nothing.

Data: Binance USD-M BTCUSDT 1m klines + Binance metrics 5m sum_open_interest, DEV 2022-01-02..2024-06-30 (loader drops bars at or after
2024-07-01). ETH not run: no ETHUSDT 1m or ETH metrics on disk. Command: `python MyTradingSys/research/level_approach_prep_2026-11-05/study.py`
(writes `MyTradingSys/tools/live_aid/level_approach_rates.js`). Thresholds OURS, fixed in PRE_REG.md before the run.

## U1 absorption at the approach (outcome over 60 bars after close of t+3)

| Approach | n | reversal 0.5 % first | break close first |
|---|---|---|---|
| absorption | 228 | 18% | 22% |
| non-absorption | 659 | 27% | 45% |
| non-absorption, reweighted to the absorption distance mix | 659 | 27% | - |

## U2 OI tell during the absorbed push (absorption events only)

| OI over the push | n | reversal |
|---|---|---|
| UP (positions opening against the push) | 67 | 18% |
| FLAT (under 0.1 %) | 88 | 15% |
| DOWN (passive side or profit-taking) | 73 | 23% |

## U3 wick-rejection TF count (1m/2m/3m/5m) in the 15 min before the first touch

| TFs with a wick rejection | n | hold (no 0.1 % close beyond in 60 min) |
|---|---|---|
| 0 | 280 | 18% |
| 1 | 129 | 25% |
| 2 | 137 | 23% |
| 3+ | 187 | 23% |

## Open
- U4 (5m vs 1m confirm close) not run; open ledger row in CARD_SPECS.md UNKNOWNS.
- One symbol, one level type (prior-day H/L); 2-day, weekly, range-floor and last-lower-high levels are shown live with these rates labelled as prior-day rates.
