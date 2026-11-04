# PRE_REG_LONG: WaveTrend c30 retest, second DEV pass on the long SPOT window (amendment to PRE_REG.md; frozen 2026-11-04 BEFORE any return was computed)

Amends `PRE_REG.md` (ship 09215469e, run 1: INCONCLUSIVE, prereg_gate BLOCKed 15m / 30m / 1h with MDE + cost 0.38 / 0.60 / 1.02 vs 0.30). Reason: power. Public SPOT klines now cover
2017-08..2026-10 (`F:/MTS/Dumps/backtest/spot_2017`, README `research/klines_history_2017/README.md`, shipped aa8d1b81), so the DEV window can be
lengthened by pre-2022 history. Code `study_long.py` (imports `study.py` unchanged: dots, RSI, divergence, retest, session, trend gate, cell stats,
survivor rule), tests `test_wiring_long.py` (written first; first run failed with `FileNotFoundError: ...study_long.py`, then 6 pass).
Only event COUNTS (`counts_long.csv`, `regime_mix_long_count.txt`) were read before this freeze.

## What is reused, what changes
| Item | Run 1 | This pass |
|---|---|---|
| Arms and parameters | PRE_REG.md table | IDENTICAL (band 53, RSI 40/60, divergence 3..12 closes + 3-bar proximity, retest N=6 midpoint, H=12, cost 0.14, sessions 08/13/21, SMA200 gate, day-clustered CI, drift control, survivor rule n>=30, >=20 days, net>0, Holm<0.05, excess t>=2) |
| Prices | USD-M futures 1m resampled | **SPOT** BTCUSDT native 15m / 30m / 1h / 1d klines (`bt_data.load_klines`); spot and futures are NOT spliced; the 2022-2024 overlap is a different price series from run 1, so per-cell numbers there will differ slightly |
| DEV window | bar closes 2022-01-01 .. 2024-06-30 | bar closes **2018-04-01 .. 2024-06-30** (2017-08 .. 2018-03 = warm-up: SMA200 of daily bars is defined from about 2018-03, 200 bars for WT) |
| New arm | none | exactly ONE proxy arm (below), per coordinator decision d-bear-proxy-1104 |
| Holm | m=24 pooled, m=96 by session | **m=48 pooled, m=192 by session** (24 strict-gate cells + 24 proxy cells, x4 sessions); the proxy arm counts in the family |

## DEV, VALIDATION, HOLDOUT (backtest/splits.py, honest definition)
- splits.py: DEV = [2022-01-01, 2024-07-01), VALIDATION = [2024-07-01, 2025-07-01), HOLDOUT >= 2025-07-01 sealed. `assert_dev_only` would reject anything before 2022-01-01; this pass does not call it, because the operator brief for this pass defines history BEFORE 2022-01 as NEW DEV data (it was never inspected by any study).
- **fresh** = bar closes 2018-04-01 .. 2021-12-31: new DEV data, never seen. **old** = 2022-01-01 .. 2024-06-30: the run 1 DEV window, ALREADY SEEN in run 1 (results published in RESULT.md); the pooled **long** DEV = fresh + old is therefore partly re-used data. The survivor rule is applied to the pooled long window as pre-registered; the fresh and old splits are shown beside it, and a lead that exists only in `old` is reported as run-1 information, not new evidence.
- VALIDATION 2024-07-01 .. 2025-06-30 read ONCE, only for long-DEV survivors (rule: n>=15, net>0, raw p<0.05); untouched otherwise. HOLDOUT never loaded (every loader call has end_ms <= window end, asserted in `study_long.py`).
- Longer history does not give a bear regime under the strict Malkan definition (weekly AND monthly RSI14 <= 40): the strict `Regime mix` has 0 bear weeks; reported as a finding, definition unchanged.

## The ONE added arm (proxy, OURS, never called Malkan's)
`reg_bearp`: bear = **weekly RSI14 <= 40 alone (monthly ignored) AND close below daily SMA200** (the strict arm's side condition is kept). Gate label `reg_bearp`; tested for the same 3 TF x 2 sides x 2 conf (rsi, div) x 2 entries = 24 pooled cells and x4 sessions = 96 session cells, same survivor rule. The strict arms (gate `with`, daily-SMA200 side agrees with the trade; reg_bull/reg_range/reg_bear descriptive) stay the primary, untouched. No other new arm or parameter.
Extra descriptive splits (no new tests of significance): each confirmatory pooled cell also computed on the fresh and old segments (segment column `seg`).

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; m = 48, cost 0.14, sd OURS 0.9 / 1.3 / 1.9 as run 1)
Event-days (counts_long.csv, pooled sessions, signal entry, long window, gate `with`): conf none (optimistic bound) 15m 580 / 30m 331 / 1h 196; conf rsi 15m 413 / 30m 247 / 1h 144; proxy gate cells 15m 148-160 (rsi), 30m 85-91, 1h 53-55.
| Cell | days | MDE + cost | vs 0.30 | gate |
|---|---|---|---|---|
| 15m, none (optimistic) | 580 | 0.294 | ok | PASS |
| 15m, rsi (a real confirmatory cell) | 413 | 0.322 | over | BLOCK |
| 30m, none / rsi | 331 / 247 | 0.434 / 0.481 | over | BLOCK |
| 1h, none / rsi | 196 / 144 | 0.699 / 0.792 | over | BLOCK |
Proxy-arm cells have fewer days than the with-trend cells, so they block as well. Consequence, fixed now: still BLOCKED for every confirmatory cell (BLOCKED_LONG.md). The DEV table is DESCRIPTIVE; the verdict ceiling stays INCONCLUSIVE (underpowered) unless a cell survives the long-DEV rule AND VALIDATION; no PASS without a VERDICTS row and an independent trade-loop re-run.

## What the result will say
RESULT_LONG.md first lines: `Regime mix:` (DEV window, strict and proxy bear counts), then the verdict; per-cell comparison to run 1 (esp. 15m sell RSI>=60 below SMA200, and 1h sell + divergence + retest, n=19 in run 1); fresh vs old split; strict vs proxy side by side.

## Context
Regime: daily SMA200 side must agree with the trade (strict arm, as run 1) plus the OURS proxy arm bear = weekly RSI14 <= 40 alone and below SMA200; strict Malkan weekly-AND-monthly <= 40 stays untouched and never fires.
Phase: none as a tag; the retest entry (dot, then pullback to the dot-bar midpoint within 6 bars) is the phase device (OURS), as run 1.
Session: asia / london / ny / late by UTC dot-bar close (research_kit.session_tag), pooled in family A and per session in family B, as run 1.
Entry: signal-bar close vs retest of the dot-bar midpoint within 6 bars, both run (OURS), as run 1.
Regime mix: 326 weeks: bull 73 (22%) | bear 0 (0%) | range 222 (68%) | n/a 31 (10%) | strict bear 0 ; proxy bear (weekly RSI14 <= 40 alone, below SMA200, OURS) 57 of 326 weeks
