INCONCLUSIVE

Regime mix: 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%) (weeks, DEV 2022-01-01..2024-06-30, BTCUSDT, OURS research_kit tag); episodes: range 152, bull 24, bear 0.

## Context
Regime: none used as a gate; mix printed above and episodes tagged in `ledger.csv` (frozen PRE_REG 2026-10-28 predates the context rule and is allowlisted, no rule changed).
Phase: failed break of a resistance level (PDH / early-session high / 5-day swing high), signal = close back below L within 3 bars.
Session: fixed window 07:00-13:00 UTC (pre-US), entry bar open inside the window.
Entry: window 07-13Z, level break fail; short, 4 tranches, S/R limit exit, no stop.

Card `backtest-pre-us-failed-break-dev-run`. BTCUSDT 1m Binance USD-M, DEV 2022-01-01..2024-06-30 only (bars >= 2024-07-01 never opened: loader raises, tested). Fee-net, taker 5 bp + 2 bp slippage, maker 2 bp (`fees.py`). Primary cell run once; code `run_dev.py`, ledger `ledger.csv`, cells `cells.json`, log `run_dev.log`.

## Verdict by PRE_REG section 7
n = 176 episodes < N_min 250 -> **INCONCLUSIVE** (not NEGATIVE). 228 signals in 176 traded days of ~912.

| Measure (primary, window 07-13Z) | Value |
|---|---|
| n episodes | 176 |
| mean net per episode | -0.0173 % of K (-1.73 bps) |
| SD / SE | 0.690 / 0.0520 % |
| t | -0.33 |
| win rate / mean winner / mean loser | 61.4% / 0.278 % / -0.487 % |
| MAE (% of K) median / p90 / max | 0.14 / 1.13 / 5.49 |
| forced-flat (time-cap) days | 154, summed net -14.41 % of K |
| target-hit days | 22, summed net 11.36 % of K |
| MDD of cumulative net / buy-and-hold | 12.6 % of K / 66.9 % |

Variant (window end 12:00, reported only): n 138, mean -2.12 bps, t -0.53, time-cap days 127 (sum -6.83 %), target days 11; INCONCLUSIVE (n < 250). The second named variant (13:00) equals the primary.

Read: 154 of 176 days hit the time cap, not a target; capped days sum -14.4 % of K vs +11.4 % from the 22 target days, so the section-7 loss-vs-gain condition also fails. Mean net is negative with t -0.33. Nothing is adopted; n shortfall means no layer decision either way. Power gate was run with n 300; the real n (176) is below its needed 250-289, so the family cannot reach PASS on DEV as specified.

## Gate output (re-run 2026-11-06 before the run)
`python scripts/dev/prereg_gate.py --n 300 --sd 60 --sd-source "OURS estimate" --cost 14 --m auto --new-cells 3 --max-gross 30` -> `n 300 sd 60 m 224 z_holm 3.691 MDE 15.696 R + cost 14 = 29.696 vs max plausible gross 30; n needed 289` / `PASS: may freeze`. Measured sd 69 bps (gate assumed 60; above its ~66 flip only if > 66: yes).

## Reading choices (OURS, conservative; PRE_REG silent)
- levels (PDH/ASH/swing) are fixed from bars BEFORE the break bar; a level counts only if >= 0.5 ATR above the day's 00:00 open
- break = first crossing per level per day with the break bar open inside W; ATR(break) used for break/E, ATR(signal bar) for the trade
- high of a bar that pushes E above 1.5 ATR kills the level even if that bar also closes below L (high precedes close)
- ATR = last 1h bar whose close time <= signal bar close; Wilder, seeded with the mean of the first 14 TR
- limit tranches and the target are active from bar t+2 (bar t+1 only holds the open fill); limit fills at its own price on trade-through of one tick
- same bar hits both the target and a higher tranche limit: target first (tranche not filled), the conservative order
- time-cap exit at the open of the window-end bar, taker, +2 bps slippage; funding: raw_fund absent -> flat 1 bp of the open size at 08:00Z (funding NOT_IN_DATA)
- one position per day: only the first signal of the day is traded; the 3-per-day cap is therefore moot
- second reported variant 'window end 13:00' equals the primary (PRE_REG s10 names it, defines nothing different): printed once as primary

Funding NOT_IN_DATA for 2022+ (flat 1 bp). Contamination: 2026-10-28 day excluded (outside DEV).
