FAIL

# Pre-US failed-break short, DEV run on 10 USD-M symbols (2022-01-01..2024-06-30), fee-net

Rule frozen in `research/pre_us_failed_break_2026-10/PRE_REG.md` s2-7; this run's choices in `PRE_REG.md` here (committed before any return was computed). One run, `run_10sym.py dev` then `analyze.py`. Binance USD-M 1m tape, research only, no fill claim, DEV only. Costs: fees.py regime A all-taker, 14 bps round trip on every filled tranche (OURS 2 bps slippage per leg), funding flat 1 bp across 08:00 (`funding NOT_IN_DATA`).

Regime mix: 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%) (research_kit.regime_tag, BTC spot 1d context, DEV weeks; episode days: bull 255, range 1138, bear 0)

## Pooled
| n | mean net bps of K | SE (day-clustered) | t | 95% CI | SE plain / t plain | measured sd |
|---|---|---|---|---|---|---|
| 1393 | -2.47 | 4.39 | -0.56 | -11.08 .. +6.14 | 3.21 / -0.77 | 119.99 |

| Check | Value | Rule | Result |
|---|---|---|---|
| n >= 250 | 1393 | yes | ok |
| mean net > 0 | -2.47 | yes | **fails** |
| t >= 2.0 (Holm z 3.688 also printed) | -0.56 | yes | **fails** |
| Time-cap days | 1270 days, sum -16,400 bps | loss < target gain | target 123 days, sum +12,963 bps: **fails** |
| MDD of cumulative net (pooled, % of K) | 97.9 | <= BTC buy-and-hold 66.9 | **fails** |
| Win rate / mean winner / mean loser | 60.7% / +45.96 / -77.36 bps | printed | wins small, loses big |
| MAE % of K (p50 / p90 / p99 / max) | 0.21 / 1.87 / 6.22 / 22.25 | printed | |
| Tranches filled 1 / 2 / 3 / 4 | 553 / 310 / 190 / 340 | printed | |

## Per symbol (net bps of K per episode)
| Symbol | n | mean | sd | win | time-cap days | sum bps |
|---|---|---|---|---|---|---|
| BTCUSDT | 177 | -3.24 | 68.96 | 0.60 | 155 | -573 |
| ETHUSDT | 186 | -2.51 | 87.23 | 0.58 | 171 | -466 |
| SOLUSDT | 141 | -24.04 | 152.02 | 0.61 | 136 | -3390 |
| BNBUSDT | 128 | +3.47 | 61.81 | 0.61 | 120 | +445 |
| XRPUSDT | 124 | -0.07 | 81.52 | 0.57 | 109 | -9 |
| DOGEUSDT | 131 | +1.65 | 232.59 | 0.66 | 122 | +216 |
| ADAUSDT | 106 | +11.86 | 118.06 | 0.58 | 95 | +1258 |
| AVAXUSDT | 115 | +3.05 | 121.71 | 0.62 | 101 | +351 |
| LINKUSDT | 137 | +9.68 | 92.63 | 0.64 | 125 | +1327 |
| LTCUSDT | 148 | -17.53 | 109.19 | 0.61 | 136 | -2594 |

By regime week: bull n=255 mean -2.43; range n=1138 mean -2.48. By year: 2022 n=552 +3.64; 2023 n=573 -8.29; 2024 n=268 -2.59. No cell is read as evidence (five of ten symbols positive, none individually tested).

## Gate output
The sd assumed at freeze (60, OURS) was low: the measured sd is 120. Re-run with the measured sd:
```
$ python scripts/dev/prereg_gate.py --n 1393 --sd 120 --sd-source "analysis.json (measured sd of net bps)" --cost 14 --m auto --new-cells 1 --max-gross 30
n 1393 sd 120 m 221 z_holm 3.688 MDE 14.558 R + cost 14 = 28.558 vs max plausible gross 30; n needed 1153
PASS: may freeze
```
Powered at the measured sd (n 1393 >= 1153 needed), so the FAIL is not UNDERPOWERED. The first freeze call with the default `--max-gross 0.3` BLOCKed by a percent/bps unit mismatch; see PRE_REG.md.

## Reading
- The pre-US failed-break short with scale-in does not pay after all-taker costs: mean -2.5 bps of K per episode (t -0.56); a 91% time-cap exit rate with a losing sum (-16.4k bps) against target-hit gains (+13.0k bps); 98% pooled drawdown.
- Per PRE_REG 2026-10 s7: FAIL, stop, no layer or management work on this family (session-high failed-break short with scale-in). The 2-symbol INCONCLUSIVE n=235 is superseded by this powered result.
- Limits: BTC-led regime context only (no bear weeks in DEV); one pre-set rule; Binance tape, not Deribit; all-taker costs are stricter than the maker-limit reading of the operator's behaviour, which could change the sign of a few bps but not the 91% time-cap pattern.

Files: `run_10sym.py`, `test_run_10sym.py`, `analyze.py`, `ledger.csv` (one row per episode), `per_symbol.csv`, `analysis.json`, `COUNT.json`.
Next: END: powered FAIL on 10 symbols DEV, no edge in the frozen pre-US failed-break short, family closed per PRE_REG s7
