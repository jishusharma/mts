# PRE-REGISTRATION: Europe-low sweep in the US session, LONG after reclaim (and mirror short), pooled BTC + ETH + SOL (frozen 2026-11-13, before any outcome)

Parents: `eur_low_us_sweep_2026-10-14/RESULT.md` (short leg exploratory negative; "long after reclaim" untested) and `eur_low_us_sweep_followups_2026-10-18/BLOCKED.md` (leg A blocked by the power gate: 133 BTC DEV days, needed 864; the file names pooled instruments and maker entries as the unblock). Not a repeat of: `europe_high_fade_2026-11-13` (FAIL, fades at the Europe HIGH on a 60-min time exit, no sweep/reclaim, Live Aid flags) or `opr_weekly_low_round_sweep_2026-10-16` (weekly-low / round-1000 levels). Code `study.py`, tests `test_study.py`.

## Hypothesis
When price trades below the Europe-session low during the US session and a 5m bar closes back above that low within 60 minutes, the failed break is a stop-run that has finished and price returns toward the Europe range. Long at the next 5m open, fee-net, beats a random-entry placebo. Mirror: sweep of the Europe high and a close back below it -> short.

## Context
- Why now: the 10-14 base-rate study found ~93-95 % of US-window breaks of the Europe low reclaim within 120 minutes, but whether the reclaim is tradeable fee-net was never tested (10-18 BLOCKED on power, not killed). Pooling three coins is the unblock the BLOCKED file named.
- Phase: pooled 2020-03 .. 2026-11, all phases; the regime split is reported, never judged on its own.
- Regime rule (OURS, same as europe_high_fade): per UTC day, prior-day close vs SMA20 of prior daily closes (no look-ahead): > +2 % = up, < -2 % = down, else range.
- Regime mix: not known before the run; REPORT.md prints `Regime mix: up x % / down y % / range z %` over the event days. A PASS must show VALIDATION per regime; one regime carrying the result with the others n < 30 is PASS-ONE-REGIME, not PASS.

## Rule (all parameters; SOURCED = operator order / parent report, OURS = chosen here before any outcome)
| Item | Value | Label |
|---|---|---|
| Data | Bybit v5 public `kline`, category linear, 5m, BTCUSDT / ETHUSDT / SOLUSDT, 2020-03-01 .. fetch time (Bybit perp, not Binance) | SOURCED (brief) |
| Days | weekdays only (Mon-Fri UTC); a day needs >= 75 of 78 Europe-session bars | OURS |
| Europe session | 07:00-13:30Z: EL = lowest low, EH = highest high, MID = (EL+EH)/2 | SOURCED (brief) |
| US window | 13:30-20:00Z, fixed UTC (no DST shift) | SOURCED (brief) |
| Sweep | first 5m bar in the US window with low < EL (short: high > EH). One event per day, coin and side | SOURCED / OURS |
| Reclaim | first 5m bar from the sweep bar up to 11 bars later (60 min) whose CLOSE is back above EL (short: below EH); the sweep bar itself counts | SOURCED (60 min), OURS (sweep bar counts) |
| Entry (taker cell) | open of the next 5m bar after the reclaim bar, must open before 20:00Z | SOURCED |
| Entry (maker cell) | resting limit at the reclaimed level (EL; short EH), placed at the reclaim-bar close, lives 12 bars, fills on TRADE-THROUGH (low < EL), fill price EL, cancelled if the stop level trades first; exits of the fill bar are not scanned | OURS |
| Stop | S = lowest low from the sweep bar to the reclaim bar (short: highest high); stop-market at S, same-bar stop+target tie = stop | SOURCED (under sweep low) / OURS (no buffer) |
| Min risk | entry-to-stop >= 0.15 % of entry, else skip | OURS (10-18 precedent) |
| Exit cells | MID, HIGH (long: EH; short: EL), 2R; a target not beyond the entry is not a trade in that cell; time stop = close of the 19:55 bar | SOURCED (brief) |
| Fees | `fees.BINANCE_TAKER` 5 bp per side; maker cell = `fees.BINANCE_MAKER` 2 bp entry + taker exit; no funding, no slippage (stated; optimistic) | SOURCED (fees.py) |
| R | 1R = entry-to-stop price distance; net R = (price pnl - fees in price) / 1R | OURS |
| Cells | 2 sides x 3 exits x 2 entries = 12 | OURS |

## Splits and verdict rule
DEV 2020-03-01 .. 2024-06-30, VALIDATION 2024-07-01 .. 2025-06-30, RECENT 2025-07-01 .. now. The judged unit is a cell on VALIDATION with the three coins pooled (per-coin shown, descriptive).
- Placebo: same days and side, a random 5m bar in the same US window whose previous close is above EL (short: below EH); entry at that next open, same stop % of entry, same target in R, same time stop, same fee kind (maker placebo is filled at the open, favourable to the placebo). 200 draw-sets (seed 1113); the cell beats placebo if its mean net R exceeds the 95th percentile of the draw-set means.
- Inference: cluster (block) bootstrap by calendar day (all coins and trades of a day move together), 2000 draws, 95 % percentile CI of the mean net R; one-sided p = share of draw means <= 0. BH at 10 % over the 12 cells' VALIDATION p-values.
- PASS (a cell): VALIDATION n >= 30 AND fee-net mean R > 0 AND CI lower bound > 0 AND beats placebo AND BH-rejected AND regime gate. UNDERPOWERED: VALIDATION n < 30. FAIL: n >= 30 and not PASS. DEV positive and VALIDATION negative = FAIL (no re-fit). No parameter search; nothing promoted by this test; a PASS only earns a testnet-forward slot.
- Headline verdict: PASS if any cell PASSes, else FAIL (or UNDERPOWERED if every cell has VALIDATION n < 30).

## Power calculation (count-only, geometry before outcomes; filled by `study.py --count`)
Event counts from `python study.py --count` (decision-time geometry only: sweep bar, reclaim bar, entry open, stop; no exit or outcome was computed). Pooled BTC + ETH + SOL (ETH from 2021-03, SOL from 2021-10, Bybit listing dates), weekdays:
| split | long events | median stop % | short events | median stop % |
|---|---|---|---|---|
| DEV | 1244 | 0.495 | 1144 | 0.419 |
| VALIDATION | 423 | 0.423 | 380 | 0.401 |
| RECENT | 591 | 0.379 | 526 | 0.368 |
Pooling lifts the long leg from 133 BTC DEV days (10-18) to 1244 pooled DEV events and 423 VALIDATION events (3515 event-days in all).

`prereg_gate.py` (sd 1.4 R = the 10-18 REGATE_AUDIT precedent value, m = 12 cells, per-event units; events of different coins on one day are not independent, so these n are optimistic):
| basis | n | cost R | MDE R | MDE + cost | n needed | gate |
|---|---|---|---|---|---|---|
| VALIDATION long, taker (0.10 % / 0.423 %) | 423 | 0.236 | 0.252 | 0.488 | about 3000 | BLOCK |
| VALIDATION long, maker entry (0.07 % / 0.423 %) | 423 | 0.17 | 0.252 | 0.422 | 1592 | BLOCK |
| DEV long (reference, not judged) | 1244 | 0.20 | 0.147 | 0.347 | 2691 | BLOCK |
So pooling does not meet the 0.30 R plausible-gross cap at m = 12 on VALIDATION: the smallest effect this test can see at 80 % power is about 0.25 R net of nothing (fees add 0.17-0.24 R on top).

DECISION (OURS, logged with `tasks.py conflict`): the operator's 15:20Z order (use the full window, pool coins) outranks the repo rule "BLOCK = do not run", so the study runs, but under a verdict vocabulary fixed now: a FAIL reads "FAIL, cannot see an effect below ~0.25 R" (a failed small edge is not excluded); a cell that meets every PASS condition reads "PASS-GATE-BLOCKED: exploratory, needs testnet-forward confirmation, never a core". No cell count, level, window, exit or fee is changed after the first outcome.
