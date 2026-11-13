# PRE-REGISTRATION: all Live Aid idea-flag groups, full-history test, frozen 2026-11-13 before any outcome is computed

Card live-aid-flags-full-1113. Follows `research/europe_high_fade_2026-11-13/` (the learner's one "keeper", fade @ Europe high, FAILED on full history: BTC VALIDATION n 1327, fee-net -5.2 bps). The 28-day table in `research/live_aid_learning/2026-11-13.md` therefore cannot be trusted for any flag. This pass runs every other idea-flag group through the same method, once, with a multiple-look correction. SOURCED = cited file, OURS = chosen here, frozen. Changing any parameter after a result = a new trial. No outcome (return, hit) had been computed when this file was committed.

## Context
- Why: 0 of 44 fee-net backtests pass; Live Aid shows flags to the operator while only a 28-day, no-fee, hit-rate table backs them. With 17 groups looked at, one group at 60 % / n 30 is what chance gives. Full history plus a correction decides which flags may stay as signals.
- Phase: pooled 2019-2026, all phases. The regime split is reported and gated, never judged alone.
- Regime rule (OURS): per UTC day, prior-day close vs SMA20 of prior daily closes (no look-ahead): > +2 % up, < -2 % down, else range.
- Regime mix: not known before the run; REPORT.md prints `Regime mix: up x % / down y % / range z %` per cell. Gate: a PASS must have VALIDATION n >= 30 in at least two regimes; otherwise PASS-ONE-REGIME, which does not count as PASS.

## Flag groups (exactly the learner's, `scripts/dev/live_aid_learn.py score()`; no new rules, no parameter search)
Each event = a new run of (side + level name) of the idea flag (`replay_events.js`, the Live Aid code unchanged, as in the Europe-high study). Groups overlap (an event sits in `idea`, its state group and its fade group); that is how the learner counts them.
1. `idea` (all events)  2. `idea REJECTED`  3. `idea ACCEPTED`  4. `idea FAILED BREAK`
5-15. `idea fade @ <level>` = state REJECTED or FAILED BREAK at: Day open, 2-day-ago low, 2-day-ago high, Asia low, Asia high, Yesterday low, Yesterday high, Europe low, Europe high (re-run inside this family for the correction), Last week low, Last week high.
Cells = group x side (LONG, SHORT) = 30 cells. The family size for the correction is always 30, whatever n is.
NOT COVERED (stated now): groups `setup` and `timing`. Their code (pulse.js setup/timing) needs 1m/2m/3m lanes, 1h/4h RSI votes and VWAP from 1m bars; the history on disk is 5m for BTC, so they cannot be reproduced without a different data set. They stay unjudged and Live Aid keeps them labelled "28-day descriptive only".

## Outcome (same as the origin, SOURCED live_aid_learn.py / replay.js)
Entry = open of the 5m bar starting at the step time; exit = close of the 5m bar starting t+55 min (time exit 60 min, no stop, no target); side-signed gross bps; hit = gross > 0. Fee 4 bps round trip (maker, auction_context.DEFAULT_MAKER_RT_BPS, SOURCED); net = gross - 4. 10 bps all-taker shown, never judged. Event skipped if a 5m bar in the 60-min window is missing (counted).

## Data and split (identical to the Europe-high study)
BTC 5m: F:/MTS/data/edge_1111_5m (labelled ETH in DATA_MAP.md; prices are BTC), 2019-01-01 .. 2026-11-10. DEV = first 70 % of calendar days, VALIDATION from 2024-07-02. The first 300 15m bars are dropped. ETH replication (only for BTC passes): F:/MTS/data/tom_raw/klines_eth 1m folded to 5m, 2022-01-01..2026-09-30, VALIDATION from 2025-04-28. SOL likewise (klines_sol, VALIDATION from 2023-10-01).

## Statistic, placebo, correction
- Statistic (OURS): mean fee-net bps of the cell's VALIDATION events; 95 % CI and one-sided p = P(mean <= 0) from a UTC-day-block bootstrap (5,000 draws, seed 1113; p = (count + 1) / (5000 + 1)).
- Placebo (OURS): per event, 200 draws of a random 5m step on the SAME UTC day (any time with a full 60-min window), same side, same 60-min exit, same 4 bps fee; draw-set mean over the cell's events; 200 draw-sets (seed 1113). Beats placebo = cell mean > 95th percentile of draw-set means. Placebo p = (#sets >= mean + 1) / 201.
- Correction: Benjamini-Hochberg at q = 10 % over the bootstrap p of all 30 cells (cells with n < 100 enter with p = 1.0). A cell survives if BH rejects it.
- Verdict PASS: VALIDATION n >= 100 AND CI lower bound of fee-net mean bps > 0 AND beats placebo AND survives BH AND regime gate. Else FAIL (n >= 100) or UNDERPOWERED (n < 100; never a pass or a fail). DEV positive with VALIDATION negative = FAIL, no re-fit.
- Replication: a BTC PASS is replicated on ETH (and SOL) with the same cell and the same criterion minus BH; replication cannot rescue a BTC FAIL. A PASS only earns a testnet-forward slot (phase-first method); nothing else is promoted.

## Run
`run.py` (this folder) runs `replay_events.js` (all idea events, Live Aid code unchanged), scores them, writes `REPORT.md` and `cells_*.json`. `test_run.py` tests the grouping, outcome, BH and verdict logic. This file's commit precedes every result file.
