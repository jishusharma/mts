# PRE-REGISTRATION: pre-US failed-break short, DEV run pooled on 10 USD-M symbols (frozen 2026-11-06)

Card `pre-us-failed-break-10sym-dev-run`. Rule = `research/pre_us_failed_break_2026-10/PRE_REG.md` sections 2-4 and 6-7, copied by reference,
unchanged (the 2-symbol study code was never shipped to trunk, only that PRE_REG; `run_10sym.py` implements its tables as written).
This file is committed before any return is computed. Status: EXPLORATORY TRIAL; a PASS is only a candidate for a VALIDATION step.

## Context
Regime: all regimes pooled; the weekly regime mix of DEV (research_kit.regime_tag on BTC spot 1d context) is reported in RESULT.md, never used as a gate.
Phase: DEV only, 2022-01-01..2024-06-30 (splits.assert_dev_only; no VALIDATION or HOLDOUT bar is opened).
Session: pre-US 07:00-13:00 UTC (research_kit.session_tag is not used; the window is the frozen PRE_REG s2 W).
Entry: level break fail (short): first break of a resistance level by 0.10 ATR, bar closes back below it within 3 bars; entry at the next open.

## Single cell
One cell: the frozen rule on the 10-symbol pool BTC ETH SOL BNB XRP DOGE ADA AVAX LINK LTC. No variant, no parameter search.

## Parameters
| Item | Value | Label |
|---|---|---|
| Window, ATR14 1h Wilder, levels PDH / ASH / 5-day swing high, break 0.10 ATR, failure 3 bars, dead above 1.5 ATR, 4 tranches of 0.25 K at +0.5 ATR steps, target = nearest support at least 1 ATR below else 1.5 ATR, time cap at 13:00 open | PRE_REG 2026-10 s2-4 | OURS (as frozen there) |
| Tick (trade-through margin) | BTC 0.1 SOURCED PRE_REG 2026-10 s3. ETH 0.01, SOL 0.01, BNB 0.01, XRP 0.0001, DOGE 0.00001, ADA 0.0001, AVAX 0.001, LINK 0.001, LTC 0.01 | OURS (Binance USD-M tick sizes, from memory, not fetched) |
| Costs | fees.py regime A, all-taker: FEES_ALL_TAKER 0.0005 per leg SOURCED `backtest/fees.py` + 2 bps slippage per leg OURS = 7 bps a leg, 14 bps round trip on every filled tranche. Deviates from PRE_REG 2026-10 s5 (Binance maker legs) by order of this card: the stricter all-taker books limit fills as taker. Funding: flat 1 bp on weight held across 08:00 UTC, `funding NOT_IN_DATA` | SOURCED fee, OURS slip and funding |
| Same-bar order | a bar that trades through the target fills only the target; tranche limits crossed in that same bar are not counted | OURS (conservative, no intrabar order in 1m bars) |
| Fills start | tranche limits and target are live from the bar after the entry bar | OURS |
| Break bar b | must lie in W (07:00..12:59), signal bar t <= 12:58 so t+1 is in W; one level consumed once crossed (no re-break); ATR for break/E taken at bar b, for entry/target at t | OURS |
| Swing high/low usable | when the next hour has closed (2h after the swing hour starts); last 5 UTC days incl. today's closed hours | OURS (PRE_REG: "usable only 2 hours after it formed") |
| Missing data | SOL, XRP, LTC each miss 7200 bars (10 days, per the card in 2022-02/2022-04): any day lacking a bar in 00:00..13:00 is no-signal; an hour with a missing minute has no ATR/swing; nothing interpolated | OURS |
| Pooled SE | day-clustered by UTC day (symbols traded the same day are correlated); plain SE also printed | OURS |
| Regime weeks | research_kit.weekly_regimes on BTCUSDT spot 1d context, pooled DEV weeks | SOURCED research_kit |

## Gate (run before this file was committed)
Event counts first (`run_10sym.py count`, no return column built): per symbol BTC 177, ETH 186, SOL 141, BNB 128, XRP 124, DOGE 131, ADA 106, AVAX 115, LINK 137, LTC 148; pooled n = 1393.
```
$ python scripts/dev/verdicts.py check "pre-US failed break short session high ATR"
no prior row matches ... Safe to pre-register
$ python scripts/dev/prereg_gate.py --n 1393 --sd 60 --sd-source "pre_us_failed_break_2026-10/PRE_REG.md:74 (OURS estimate, unmeasured)" --cost 14 --m auto --new-cells 1
n 1393 sd 60 m 221 z_holm 3.688 MDE 7.279 R + cost 14 = 21.279 vs max plausible gross 0.3; n needed inf
BLOCK: do not freeze   <- the default max-gross 0.3 is in percent; sd and cost here are bps (unit mismatch)
$ python scripts/dev/prereg_gate.py ... same ... --max-gross 30
n 1393 sd 60 m 221 z_holm 3.688 MDE 7.279 R + cost 14 = 21.279 vs max plausible gross 30; n needed 288
PASS: may freeze
```
The first call is the card's literal command; its BLOCK is a unit artefact. The 2-symbol freeze used `--max-gross 30` with the bps mapping (PRE_REG 2026-10 s10, OURS); the same mapping is used here. The sd 60 is unmeasured (OURS); RESULT.md prints the measured sd and re-runs the gate with it.

## Pass rule (PRE_REG 2026-10 s7, unchanged, with the pooled SE)
Episode = one entered position (symbol-day). Statistic: mean net bps of K, day-clustered SE, t = mean/SE.
PASS iff n >= 250 and mean net > 0 and t >= 2.0 and the summed loss of time-cap days < the summed gain of target-hit days and MDD of the cumulative net <= buy-and-hold BTC MDD over DEV.
n < 250 is INCONCLUSIVE. Otherwise FAIL. t >= 3.688 (Holm z at m 221) is also printed. Verdict word UNDERPOWERED if the re-run gate with the measured sd BLOCKS.
