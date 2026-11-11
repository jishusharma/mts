# PREREG: BTC order-flow map, card 1/4 (btc-of-map-prereg-1112), written 2026-11-12 before any result

Operator decision 2026-11-12 (OPERATOR_DECISIONS.md): Tom and Fabio give the order-flow idea only (who is forced, where size trades, absorption). Their index-futures clocks (cash open, candle close, settlement) are NOT carried to BTC; BTC is read on its own clocks and flows.
Nothing below was run. No event was counted and no return was computed on any event; the only price statistic used is the standard deviation of non-overlapping 60-minute closes (see Gate).
All numbers are labelled SOURCED (from a file or the card) or OURS (chosen here, cannot be called the traders').

## Context
Regime: none as a gate, because the question is what flow does in whatever regime BTC is in; each RESULT reports `Regime mix:` (bull / bear / range share of DEV and VALIDATION) and a per-regime split (OURS).
Phase: none as a gate (cycle phase is read once in the RESULT from research/btc_cycles_2026-11, never tuned on).
Session: reported, not gated: every event is tagged Asia 00-08Z, Europe 08-14Z, US 14-21Z, Late 21-24Z (OURS, same cut as edge_views_2026-11-11/TIME) plus UTC hour, weekday and funding clock (nearest of 00, 08, 16Z).
Entry: next 1m bar open after the event bar closes (A1, A2); open of the 1m bar starting one minute after the funding timestamp (A3); taker fee both sides.

## Not repeated (read before writing; this map must differ)
| Earlier work | What it did | How this map differs |
|---|---|---|
| fabio_cvd_2026-10-30 RESULT.md (U7, U8) | Box CVD sign vs break side (U7: price drift, no CVD information); CVD lower low at equal 15m lows (U8: reverses less than control). DEV only, no fees. | Not repeated. A2 is bar-level delta vs the same bar's price move; no equal-low or box rule. |
| orderflow_views_2026-10-14 RESULT.md | Price-vs-CVD divergence on 1m/5m with OI split, 60 min net: 0 of 12 arms pass; first DEV label contaminated, DEV-only rerun: NEGATIVE. | Not repeated. No divergence rule, no OI split. |
| large_trade_absorption_2026-10-30 RESULT.md | Descriptive 5m large-buy / large-sell bars, +-0.5 % first, no fees, 2024-12..2025-12. | A1 is the same idea made testable: fee-net, 15m/60m, de-clustered, DEV from 2022, frozen split. Its window 2024-12..2025-12 was already read, so 2025-07..2025-12 is dropped here (see Splits). |
| edge_views_2026-11-11 TIME and FLOW | 44 clock cells, unsigned (none beyond Bonferroni); funding bottom 5 % long for 3 days (fails). | A3 conditions on a funding extreme, signs against the payers, horizon 15m/60m after settlement, not 3 days. Clock cells are not re-run: clocks only tag events here. |
| TESTED_MAP.md | 100 counted studies; forced-flow family 7, descriptive. | First fee-net, split-disciplined forced-flow family; the repo-wide m below counts it. |

verdicts.py check "btc order flow clock absorption forced flow" returned: no prior row matches (need 3 of absor, clock, flow, force, order); safe to pre-register.

## Events (fixed family; nothing added after a result)
Bars are UTC-aligned 5m bars built from the 1m klines (A2) or from aggTrades (A1). Every trailing window looks backwards only and may reach into earlier splits (past data only).

| Id | Event | Trade side | Definition |
|---|---|---|---|
| A1 | Large aggressor print | WITH the sign of L | Print threshold = 99.9th percentile of aggTrade quantity over the previous 7 full UTC days (OURS; card "top 0.1 % trade size per day", made point-in-time). Per 5m bar L = sum(qty of buyer-aggressor prints >= threshold) - sum(seller-aggressor prints >= threshold). Event = \|L\| >= 98th percentile of \|L\| over the previous 30 days of 5m bars (OURS, same 2 % tail as large_trade_absorption). Long if L > 0. The opposite sign is not a separate arm. |
| A2 | Absorption | AGAINST the sign of delta | delta5 = sum over the five 1m bars of (2 x taker_buy_volume - volume). Event = \|delta5\| >= 98th percentile of \|delta5\| over the previous 30 days of 5m bars AND \|close - open\| / open < 0.1 % for that 5m bar (card definition). Long if delta5 < 0. |
| A3 | Funding extreme at settlement | AGAINST the funding payers | Settlement at 00, 08, 16Z. Event = \|last_funding_rate\| >= 90th percentile of \|rate\| over the previous 90 days (270 settlements, OURS). Short if rate > 0, long if rate < 0. |

De-clustering (OURS): within each event family, scan in time order and accept an event only if it is at least 60 minutes after the previous accepted event; the same accepted set serves both horizons. An event with any missing 1m bar in its window is dropped.

## Clocks (BTC own; tags and placebo matching only, never a trigger)
Funding 00/08/16Z (SOURCED: Binance 8h funding, fundingRate files); UTC hour 0-23; weekday Mon-Sun (UTC); sessions Asia 00-08Z, Europe 08-14Z, US 14-21Z, Late 21-24Z (OURS). No DST adjustment. No index-futures clock is used.

## Outcomes
Forward return of the signed trade from the entry open to the close of the 1m bar 15 minutes and 60 minutes later, minus 0.10 % round trip (SOURCED: 0.05 % per side taker, repo fee; the 10 bp of the operator brief). Reported in percent. Cells = 3 events x 2 horizons = 6 (family m = 6). No stop, no target, no sizing.

## Splits (OURS; dates follow SPLIT_ALIGNMENT_2026-10-17.md, DEV before 2024-07-01)
| Split | Window (UTC) | Rule |
|---|---|---|
| warm-up | 2022-01-01 .. 2022-01-31 | trailing windows fill; no events |
| DEV | 2022-02-01 .. 2024-05-31 | the only split read in card 2 |
| GAP | 2024-06-01 .. 2024-06-30 (30 days) | dropped, not read |
| VALIDATION | 2024-07-01 .. 2025-06-30 | read once, only for cells that clear DEV |
| RESERVE | 2025-07-01 .. 2025-12-31 | dropped: large_trade_absorption_2026-10-30 already read 2025-07..12 descriptively, so it cannot be sealed |
| HOLDOUT | 2026-01-01 .. latest file (sealed) | opened once, only for a cell that passes VALIDATION, by card 4; never in cards 2-3; the read is logged in holdout_reads.csv |

DECISION (OURS, conservative): the card text had DEV to 2024-06-30 with no gap; the 30-day gap and split discipline of the 11-11 views are applied instead, and 2025-H2 is reserved because it was read.

## Placebo and mark rule (fixed now)
Placebo: per cell, 1,000 draws (seed 1112) of as many entry times as accepted events, sampled uniformly from DEV 5m bars with the same UTC-hour histogram, signed with the same long/short count and passed through the same de-clustering. Report the placebo mean 1st and 99th percentile.
Per cell report: n, mean net %, sd, t = mean / (sd / sqrt(n)), share positive, the same on VALIDATION, mean by session tag, `Regime mix:`.
Minimum n (OURS, from the gate below): DEV n >= 180 per cell, VALIDATION n >= 30; else the cell is INSUFFICIENT_N and gets no verdict.

| Mark | Rule |
|---|---|
| PASS | DEV \|t\| >= 3.71 (Holm z for the gate's repo-wide m = 243) AND DEV mean net > 0 AND outside the placebo 1-99 % band AND VALIDATION mean net > 0 with t >= 1.65. |
| LEAD | DEV \|t\| >= 2.64 (Bonferroni, 0.05 / 6 cells) AND DEV mean net > 0 AND VALIDATION mean net > 0. A LEAD may go to a paper slot only; it is never called an edge. |
| none | anything else. Positive gross with negative net is written "gross only". |

A1 is NOT_RUN (not failed) while aggTrades are not on disk; its two cells stay in the family count (m stays 6, conservative).

## Gate (measured values, outputs pasted)
sd of non-overlapping 60-minute closes: BTCUSDT 1m klines 2022-01-01 .. 2024-05-31 (21,167 returns) = 0.583 % (15-minute: 0.296 %). This is a price statistic over all bars, not an event result.
Command and output (units are percent, cost 0.10 %, max plausible gross 0.30):

    prereg_gate.py --n 175 --sd 0.583 --cost 0.10 --m auto --new-cells 6 --sd-source "PREREG.md sd of 60m closes"
    n 175 sd 0.583 m 243 z_holm 3.712 MDE 0.201 R + cost 0.1 = 0.301 vs max plausible gross 0.3; n needed 176
    BLOCK: do not freeze   (exit 1)
    prereg_gate.py --n 180 ... (same other arguments)
    n 180 sd 0.583 m 243 z_holm 3.712 MDE 0.198 R + cost 0.1 = 0.298 vs max plausible gross 0.3; n needed 176
    PASS: may freeze   (exit 0)

So the frozen floor is 180 accepted DEV events per cell (the gate's own n is a planning floor, not a count). Cells below it are INSUFFICIENT_N.

## Checkers
verdicts.py check: ran, no prior row. prereg_gate.py: exit 0 at n 180. prereg_context_lint.py scans only files named PRE_REG*.md, so it was run on a scratch copy of this file named PRE_REG.md: Context removed gives exit 1, this file gives exit 0 (outputs in the commit message).
