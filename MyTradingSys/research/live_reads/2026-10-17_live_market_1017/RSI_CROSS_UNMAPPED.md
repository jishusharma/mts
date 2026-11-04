# RSI cross events: map or leave unmapped (card rsi-cross-unmapped-and-pivot-stack)

Date 2026-11-04. Read-only note; auto_trader.py is unchanged.

## Decision: LEAVE UNMAPPED (fail closed), feed as confluence flags instead

Rule (OURS, set in the card before looking): map `rsi:cross` only if the fee-net mean R per day is > 0 with at least 100
independent days on DEV. Result: every cell is negative, so no `layer_rules` entry is added.

## DEV number (BTCUSDT, DEV = first 70% of bars, 2022-01-01 .. 2025-05-13)

Method: `rsi_events` cross events at level 40 / 60 (tolerance 0.5 OURS = live RSI_TOL), RSI(14). Side only where a source
exists, `CROSS_SIDE_BY_LEVEL` (MLK-R1, SOURCED in malkan_40_60.py): 40 down = short, 60 up = long. Entry at the close of the
signal bar, generic live bracket stop 1% / target 2% / max 8 bars (OURS, live default), one position at a time, fees from
`bt` simulate_trade (taker 5 bps, target pays maker), no funding. R = net return / 1% stop.

| TF @ level | all cross events | mapped events | trades | event days | mean R per trade | mean R per day |
|---|---|---|---|---|---|---|
| 15m @ 40 | 7087 | 3471 | 2649 | 1082 | -0.102 | -0.249 |
| 15m @ 60 | 6913 | 3369 | 2614 | 1081 | -0.072 | -0.174 |
| 1h @ 40 | 1633 | 808 | 692 | 538 | -0.089 | -0.114 |
| 1h @ 60 | 1677 | 812 | 678 | 560 | -0.065 | -0.079 |

All four cells have far more than 100 days and all are negative: the sample is big enough to say "no edge" under the live
bracket, not "insufficient n". The unmatched cross directions (40 up, 60 down) have no source for a side at all.

## Counts of live rejections by TF and week

NOT produced here: `live_mirror.py brief` refused (the mirror copy is from JIS-NB, owner is desktop-f7iu69n; read it on
desktop-f7iu69n). The only committed count is from T09 (T09_live_parity.md section 5, audit 2026-10-16): unmapped
`rsi:cross` alerts 265 (5m) / 90 (15m) / 12 (1h) over the audit window. A per-week table needs the host file
`runtime_data/auto_trades.jsonl` on the owner machine (counts only, the repo is public). Not needed for the decision.

## What changed instead (code)

`MyTradingSys/backtest/layers/alerts/live_confluence_feed.py` (layer `confluence_feed`, 1h): RSI 40/60 cross / support /
rejection / failure events become alert-only flags (`cf_rsi_cross_up_60`, ...) next to the Malkan R-BULL / R-BEAR / PRD / NRD (window 12 STRONG / 18 OK, closes only; operator spec d-malkan-divergence-window-1104)
and Krown K-HBULL / K-HBEAR divergence flags. No side, `collection_only`, no `layer_rules` entry; a test pins that
`auto_trader.layer_side` returns None for all of them and for the raw `rsi:cross`.

## Part B: pivot stack (level touch + RSI/WT divergence + delta/OI exhaustion)

Evidence: SHOT_4ae992130268.md. No layer stacks these three today. The first two inputs now exist as causal flags:
levels first-touch events (`live_levels_confluence.py`) annotated with divergence flags via
`annotate_levels_events` (a flag counts only after its bar has closed). The delta / OI exhaustion leg and the WT
divergence are still missing; their features belong to card oi-pivot-reversal-probability-by-tf. No new detector was written here.
