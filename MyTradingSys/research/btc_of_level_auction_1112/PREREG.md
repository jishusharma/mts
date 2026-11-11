# PREREG: BTC order flow at a level and unfinished auction, family 2 (of-family-level-and-auction-prereg-1112), written 2026-11-12 before any result

Operator decision 2026-11-12 (OPERATOR_DECISIONS.md): Tom and Fabio give the order-flow idea only; BTC runs on its own clocks and flows. This family is the two transferable ideas that the frozen map (research/btc_orderflow_map_1112/PREREG.md, not edited here) does not hold: T3 flow only matters at a level, T7 an unfinished auction at a high or low (research/analyst_video_status_1112/TRANSFER_TO_BTC.md, verified quotes; research/orderflow_extracts_1112/ORDERFLOW_RULES_DRAFT.md).
Nothing below was run. No event was counted and no return was computed on any event; no VALIDATION, GAP or HOLDOUT data and no result file of the map was opened. The only statistic used is the sd of 60-minute closes already measured in the map's Gate.
Labels: SOURCED (file or card) or OURS (chosen here, never the traders').

## Context
Regime: none as a gate, because the question is what flow does at a level in whatever regime BTC is in; each RESULT reports `Regime mix:` (bull / bear / range share of DEV and VALIDATION) and a per-regime split (OURS).
Phase: none as a gate (cycle phase read once in the RESULT from research/btc_cycles_2026-11, never tuned on).
Session: reported, not gated: tags Asia 00-08Z, Europe 08-14Z, US 14-21Z, Late 21-24Z plus UTC hour, weekday and funding clock (OURS, same as the map). No index-futures clock is used.
Entry: B1 next 1m bar open after the 5m event bar closes; B2 next 1m bar open after the 15m event bar closes; taker fee both sides.

## Not repeated (this family must differ)
| Earlier work | What it did | How this family differs |
|---|---|---|
| btc_orderflow_map_1112 A2 | Absorption anywhere, any price | B1 requires a prior-day level at the bar extreme; B1 vs the same events away from the level is the reported contrast |
| btc_orderflow_map_1112 A1, A3 | Large prints, funding extreme | not used |
| fabio_cvd_2026-10-30 U8 | CVD lower low at equal 15m lows | no CVD, no equal-low rule |
| large_trade_absorption_2026-10-30 | Descriptive 5m big-print bars | B2 uses per-price volume inside a 15m bar and a 24h extreme |

verdicts.py check "btc order flow level absorption unfinished auction": no prior row matches (need 4 of absor, aucti, flow, level, order, unfin); safe to pre-register.

## Levels (from klines only; for UTC day D computed from day D-1, so point-in-time)
| Level | Definition |
|---|---|
| PDH, PDL | high and low of the previous UTC day, 1m klines |
| VAH, VAL | previous UTC day volume profile (OURS): each 1m bar's volume goes to the bucket of its typical price (high+low+close)/3; bucket width 0.05 % of the previous day's close; POC = bucket with most volume; the value area grows from the POC by adding the larger of the next two buckets above or below until it holds 70 % of the day's volume (standard rule); VAH/VAL = outer edges of that area |

"At a level" (OURS): low-type touch = the 5m bar's low is within 0.10 % of PDL or VAL (above or below it); high-type touch = the 5m bar's high is within 0.10 % of PDH or VAH.

## Events (fixed; nothing added after a result)
| Id | Event | Trade side | Definition |
|---|---|---|---|
| B1 | Absorption at a level (T3) | AGAINST delta | UTC-aligned 5m bar from 1m klines; delta5 = sum over the five 1m bars of (2 x taker_buy_volume - volume). Event = abs(delta5) >= 90th percentile of abs(delta5) over the previous 30 days of 5m bars AND abs(close - open) / open < 0.15 % AND the bar is at a level of the matching type: delta5 < 0 (sellers absorbed) with a low-type touch = long; delta5 > 0 with a high-type touch = short. Delta against the level type (delta5 < 0 at a high) is not an event |
| B2 | Unfinished auction at a 24h extreme (T7) | FADE the extreme | UTC-aligned 15m bar from aggTrades. Price buckets 0.01 % of the bar open; top bucket = bucket holding the bar high, bottom bucket = bucket holding the bar low. High event: bar high >= highest high of the previous 96 15m bars (24h) AND the top bucket holds both buyer-aggressor and seller-aggressor volume (each > 0, card wording) AND the top bucket total volume >= 95th percentile of top-bucket volume over the previous 30 days of 15m bars; trade short. Low event: mirror with the bottom bucket and the 24h low; trade long. A bar that is both is dropped |

DECISION (OURS, conservative): B1 uses the 90th percentile and a 0.15 % body (map A2: 98th and 0.1 %) because the level condition already thins events; a cell still short of the floor is INSUFFICIENT_N, with no loosening after seeing counts.
DECISION (OURS): T7 says size at a high/low means the auction is unfinished and price comes back; the direction after the bar is not stated, so B2 trades the standard fade (against the extreme) as the single arm; the opposite sign is not a second arm. Diagnostic only, not marked: share of B2 events whose bar extreme is revisited within 24h, against the placebo.
De-clustering (OURS): within each family accept an event only if at least 60 minutes after the previous accepted one; one accepted set serves both horizons. Events with any missing 1m bar in their window are dropped. All trailing windows look backwards only (they may reach into earlier splits).
Data status: B1 needs 1m klines (LOCAL 2022-01..2025-12 and 2026; map DATA_INVENTORY.md). B2 needs aggTrades, NOT on disk for DEV (folder empty; F:/MTS/data/orderflow_1m starts 2024-12-02): B2 is NOT_RUN (not failed) until a card fetches aggTrades for the whole DEV window 2022-02-01 .. 2024-05-31; a partial or hand-picked window is not allowed. Its two cells stay in the family count.

## Clocks
BTC own clocks only, as tags and placebo matching: funding 00/08/16Z, UTC hour, weekday, the four session tags above. Never a trigger.

## Outcomes
Forward return of the signed trade from the entry open to the close of the 1m bar 15 minutes and 60 minutes later, minus 0.10 % round trip (SOURCED: 0.05 % per side taker, repo fee; the brief's 10 bp), in percent. Cells = 2 events x 2 horizons = 4 new cells. No stop, target or sizing.

## Splits (identical to btc_orderflow_map_1112/PREREG.md)
| Split | Window (UTC) | Rule |
|---|---|---|
| warm-up | 2022-01-01 .. 2022-01-31 | trailing windows fill; no events |
| DEV | 2022-02-01 .. 2024-05-31 | the only split read in the DEV card |
| GAP | 2024-06-01 .. 2024-06-30 | dropped, not read |
| VALIDATION | 2024-07-01 .. 2025-06-30 | read once, only for cells that clear DEV |
| RESERVE | 2025-07-01 .. 2025-12-31 | dropped (already read descriptively elsewhere) |
| HOLDOUT | 2026-01-01 .. latest file (sealed) | opened once, only for a cell that passes VALIDATION, logged in holdout_reads.csv |

## Placebo and marks (fixed now)
Placebo per cell: 1,000 draws (seed 1112) of as many entry times as accepted events, uniform over DEV bars of the same bar size with the same UTC-hour histogram, same long/short count, same de-clustering. Report the placebo mean and 1st/99th percentiles.
Contrast (reported, not marked): B1 events versus the same thresholds applied NOT at a level, same horizons; the level is useful only if the at-level mean net exceeds the away mean net.
Per cell report: n, mean net %, sd, t = mean / (sd / sqrt(n)), share positive, the same on VALIDATION, mean by session tag, `Regime mix:`.
Minimum n: DEV n >= 180 per cell, VALIDATION n >= 30; else INSUFFICIENT_N, no verdict.

| Mark | Rule |
|---|---|
| PASS | DEV abs(t) >= 3.72 (Holm z at the gate's m = 251, below) AND DEV mean net > 0 AND outside the placebo 1-99 % band AND VALIDATION mean net > 0 with t >= 1.65 |
| LEAD | DEV abs(t) >= 2.50 (Bonferroni, 0.05 / 4 cells) AND DEV mean net > 0 AND VALIDATION mean net > 0; paper slot only, never called an edge |
| none | anything else; positive gross with negative net is written "gross only" |

## Gate (measured values, outputs pasted)
sd of 60-minute closes, BTCUSDT 1m klines 2022-01-01 .. 2024-05-31 = 0.583 % (from btc_orderflow_map_1112/PREREG.md Gate; a price statistic over all bars, not an event result). The map's 6 cells are counted as well as these 4 (m = ledger + 10, conservative).

    prereg_gate.py --n 180 --sd 0.583 --cost 0.10 --m auto --new-cells 10 --sd-source "btc_orderflow_map_1112/PREREG.md Gate sd of 60m closes"
    n 180 sd 0.583 m 251 z_holm 3.720 MDE 0.198 R + cost 0.1 = 0.298 vs max plausible gross 0.3; n needed 177
    PASS: may freeze   (exit 0)

With --new-cells 4 (this family alone) the gate gives m 245, z_holm 3.714, n needed 176, PASS. Frozen floor: 180 accepted DEV events per cell.

## Checkers
verdicts.py check: no prior row. prereg_gate.py: exit 0 at n 180. prereg_context_lint.py: exit 0 on this file (output in the commit message). btc_orderflow_map_1112/PREREG.md is unchanged (git diff empty).
