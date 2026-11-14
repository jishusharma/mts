# PRE-REGISTRATION: "idea fade @ Europe high" (Live Aid flag), full-history re-test, frozen 2026-11-13 before any outcome is computed

Card europe-high-fade-full-1113. Question: is the 60 % / n 30 hit rate in `research/live_aid_learning/2026-11-13.md` real? Nothing is tuned: the rule is the Live Aid code run unchanged (levelstory.js, pulse.js lane, replay.js `levels()`/`ladder()`) over all BTCUSDT history on disk. SOURCED = cited file, OURS = chosen here, frozen. Changing any parameter after a result = a new trial. No outcome (return, hit) had been computed when this file was committed.

## Context
- Why: MTS has 0 of 44 fee-net backtests passing; the Live Aid 28-day replay (descriptive, no fees, 1h hit = r1h > 0) shows only this flag above the learner's own rule (n >= 30, hit >= 10 points from 50 %). Seventeen flag groups were looked at and the others sit at 41-53 %, so one group at 60 % with n 30 is what chance can give (multiple looks); a long history decides.
- Phase: pooled 2019-2026, all phases. The regime split is reported, never judged on its own.
- Regime rule (OURS): per UTC day, prior-day close vs SMA20 of prior daily closes (no look-ahead): > +2 % = up, < -2 % = down, else range. Regime mix is computed over ALL days of each cell's data.
- Regime mix: not known before the run; REPORT.md prints `Regime mix: up x % / down y % / range z %` per cell (rule above). Gate: a PASS must show the VALIDATION result per regime; a positive result carried by one regime while the others have n < 30 is reported as PASS-ONE-REGIME and does not count as PASS.

## Rule, reproduced exactly (parameters)
| Item | Value | Label |
|---|---|---|
| Europe session | UTC 07:00 to 13:00; Europe high/low = max high / min low of 15m bars with open >= day 07:00 and close < day 13:00; the level exists from 13:00 UTC to day end | SOURCED replay.js levels(), map.js SESSIONS |
| Other levels in the ladder (they decide which level is nearest) | Yesterday H/L, 2-day-ago H/L (15m bars), last week H/L, day open, Asia H/L (00-08Z, from 08:00), exactly as replay.js; week H/L taken from 15m bars instead of 4h bars (same values, same UTC grid) | SOURCED replay.js |
| Step | every 5 min, closed bars only; px = last closed 5m close (= last 1m close before t) | SOURCED replay.js |
| Level story | levelstory.js `story()` unchanged, P = {touch 0.0005, near 0.003, wick 0.5, relVol 1.5, bbNear 0.1, look 3, idea 3}; wt15 from pulse.js `lane('15m',60,t)`; up to two levels considered: at / nearest above / nearest below (below only if fewer than 2) | SOURCED levelstory.js, pulse.js, replay.js (the P values are OURS in origin, untested) |
| Flag | an idea exists (considered levels agree, not mixed) with name "Europe high" and state REJECTED or FAILED BREAK; a flag event fires when the (side + name) run key changes at a 5-min step | SOURCED replay.js events + live_aid_learn.py score() |
| Direction | the idea's side: SHORT when Europe high is resistance, LONG when price came from above and the high acts as support. "Fade" = the story's own idea; both sides are in the origin's 30 and in the headline | SOURCED levelstory.js |
| Entry | open of the 5m bar starting at the step time t (= the 1m open at t) | SOURCED replay.js fwd() |
| Exit / horizon | close of the last 1m bar of the 60 minutes = close of the 5m bar starting t+55 min; no stop, no target (time exit only) | SOURCED replay.js fwd(t,side,60) |
| Hit | gross r1h > 0 (side-signed), as live_aid_learn.py | SOURCED |
| Event skipped | if any 5m bar in [t, t+60 min) is missing (counted and reported) | OURS |

## Data (all on disk; no outcome loaded)
- BTCUSDT 5m, F:/MTS/data/edge_1111_5m, 2019-01-01 .. 2026-11-10: Binance spot 2019, USD-M perp 2020 onward (field `src`; the switch is reported as a sub-cut). Columns t,o,h,l,c,volume,taker-buy volume (taker buy feeds the story's delta/absorb evidence). 15m bars are folded from three 5m bars on the UTC grid. (DATA_MAP.md labels this folder ETHUSDT; the prices are BTC, e.g. 3,696 on 2019-01-01 and 42,314 on 2024-01-01.)
- ETHUSDT and SOLUSDT: 1m perp csv in F:/MTS/data/tom_raw/klines_eth (2022-01 .. 2026-09) and klines_sol (2022-01 .. 2024-06), folded to 5m (sum of volume and taker buy). Separate pre-declared cells; replication only, BTC is the cell that decides.
- fapi is not used; no top-up is needed (history covers the replay window).

## Split (chosen before running, by calendar day, per cell)
DEV = first 70 % of calendar days of the cell's span, VALIDATION = the last 30 %. Cutoff dates (floor(0.7 x days)): BTC 2019-01-01..2026-11-10, VALIDATION from 2024-07-02; ETH 2022-01-01..2026-09-30, VALIDATION from 2025-04-28; SOL 2022-01-01..2024-06-30, VALIDATION from 2023-10-01. An event belongs to the day of its step time. The story warm-up (first 300 15m bars, about 3 days) is dropped.

## Cost and R
- Fee: 4 bps round trip (maker, auction_context.DEFAULT_MAKER_RT_BPS = 2 x BINANCE_MAKER x 10,000 = 4.0, SOURCED). Net bps = gross bps - 4. Also reported at 10 bps round trip (all-taker, pessimistic row, never judged). No funding, no slippage in the headline; entry is a market-style open of the next bar, so 4 bps is the optimistic bound (stated).
- R (OURS): 1R = distance entry to the idea's own `voidAt` (the wick extreme the idea is voided beyond, SOURCED levelstory.js), in bps of entry, floored at 10 bps so a tiny distance cannot blow R up. Net R = net bps / 1R. Mean net bps is reported next to it (no floor effect).
- Confidence interval: bootstrap of events resampled in UTC-day blocks (events on one day move together), 5,000 draws, seed 1113, 95 % percentile.

## Placebo (one, stated)
Same trade at a random time in the same session: for each event, 200 draws of a random 5m step in the SAME UTC day inside 13:00 to 23:00 UTC (the hours when the Europe-high level exists and a 60-min exit fits), same side, same 1R distance in bps, same 60-min time exit, same 4 bps fee. A draw-set mean = mean net R over all events (one random step per event); 200 draw-sets (seed 1113). The set "beats placebo" if its mean net R exceeds the 95th percentile of the draw-set means.

## Pass criterion and verdicts
- PASS: BTC VALIDATION cell has n >= 30 AND fee-net mean R with 95 % CI lower bound > 0 AND beats the placebo AND the regime gate above. DEV is reported next to it; DEV positive and VALIDATION negative is FAIL (no re-fit).
- UNDERPOWERED: BTC VALIDATION n < 30 (never called a pass or a fail). Any sub-cut (side, regime, source, DEV) with n < 30 is printed UNDERPOWERED and not judged.
- FAIL: n >= 30 and the criterion is not met.
- ETH and SOL cells use the same criterion as replication; they cannot rescue a BTC FAIL, and a failed replication of a BTC PASS is stated plainly.
- One headline verdict line only (BTC VALIDATION). Pooled n, hit rate and the replay-window (last 28 days) comparison are descriptive. No parameter search of any kind; nothing is promoted by this test. A PASS would only earn a testnet-forward slot (phase-first method).

## Run
`run.py` (this folder) exports the 5m series to a scratch JSON, runs `replay_events.js` (this folder; it `require`s the unchanged tools/live_aid levelstory.js, pulse.js, live_aid_indicators.js) to get the flag events with their `voidAt`, then scores them in Python. `test_run.py` holds the outcome, Europe-session and bootstrap tests. Writes `REPORT.md` and `events_*.json`. This file's commit precedes every result file.
