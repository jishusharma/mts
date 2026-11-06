# RESULT: pre-US failed-break short, BTCUSDT 1m DEV 2022-01..2024-06 (card backtest-pre-us-failed-break-dev-run)

**INCONCLUSIVE (PRE_REG section 7): n = 235 episodes < N_min 250. The outcome columns below are descriptive, not a finding.**
Regime mix: 130 weeks DEV: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%) (episodes: range 195, bull 40, bear 0)
Context: Regime: weekly RSI band + daily 200-bar side, as-of 00:00 UTC (research_kit.regime_tag) | Phase: failed break (level break fail) | Session: window 07-13Z (london + pre-NY) | Entry: short at open of the bar after the failing close
Fee regime: Binance research tape, tranche 1 taker 5 bp + 2 bp slip, later tranches and target maker 2 bp, time-cap exit taker 5 + 2 bp (fees.py), funding from the DEV archive (strict loader). Splits: DEV only, loader refuses open >= 2024-07-01, 0 VALIDATION/HOLDOUT reads.

## Primary cell (window 07-13Z), every number
| item | value |
|---|---|
| n episodes (signal days; signals incl. later ones) | 235 (235; 322), 0 skipped, 0 missing minutes |
| mean net per episode | -0.36 bps of K (gross +5.18, cost 5.64, funding -0.10) |
| sd / SE / t | 62.6 / 4.08 / -0.09 |
| win rate; mean winner; mean loser | 62.1%; +25.5; -42.8 bps |
| MAE % of K (p50/p90/p99/max) | 0.11 / 0.92 / 2.62 / 5.49 |
| time-cap (forced-flat) days | 206, sum -1518.6 bps |
| target-hit days | 29, sum +1434.9 bps |
| MDD of cumulative net vs buy-and-hold | 13.2 %K vs 67.8 % (ok) |
| by level: ASH / PDH / SWH (n, mean bps) | 116, +0.4 / 105, -1.8 / 14, +4.4 |
| by episode regime: range / bull | 195, +2.9 / 40, -16.5 (descriptive, small n) |

Section 7 bars: n>=250 FAIL (235), mean>0 FAIL, t>=2 FAIL, cap loss < target gain FAIL (1518.6 > 1434.9), MDD<=BH ok. Verdict word: INCONCLUSIVE because n < 250 (never NEGATIVE). Nothing here adopts or rejects the family.

## Variant (reported, not the verdict): window and time cap end 12:00Z
n 188, mean -2.88 bps, t -0.87, cap days 173 (sum -1075.6), target days 15 (+534.3), MDD 11.5 %K. The PRE_REG section 10 "window end 13:00" variant is the primary cell itself (identical).

## Gate re-run with the real n and measured sd (PRE_REG section 10 said do this)
`prereg_gate.py --n 235 --sd 62.6 --cost 14 --m auto --new-cells 3 --max-gross 30` -> m is now 223 (repo-wide ledger count, was 68 at freeze), MDE 18.5 + cost 14 = 32.5 vs 30, n needed 314 (289 at the estimated sd 60): BLOCK. So even a larger DEV n on BTC alone would not clear the gate; BLOCKED for the verdict path, INCONCLUSIVE for the run. More power needs more symbols/years (ETH 1m exists under klines_eth; not pulled here by the card's scope) or a looser level definition, both a new PRE_REG.

## Parameter labels
All SOURCED items: fees (fees.py:27-28), splits (splits.py DEV_END), 08:00 funding settlement. Everything else OURS as listed in PRE_REG sections 2-5. DECISION (OURS) readings where PRE_REG was silent are listed at the top of run_dev.py (ATR at break vs signal bar, ASH validity, swing lag 3h and 5-day lookback, break window b..b+3, fills only after the entry bar, target-first on a both-touch bar, gap fills at open, re-break after an expired track allowed). Output file names follow the card (run_dev.py), not PRE_REG section 9 (screen.py).

Files: run_dev.py, test_run_dev.py (11 tests, loader guard + hand-value net), COUNT.md (n committed first), ledger.csv, DATA_MANIFEST.csv, sim_desk/results/backtest-pre-us-failed-break-dev-run.json.
