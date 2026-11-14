# PRE_REG: T11 breadth washout LONG (market-wide, 1d), 2026-11-14, frozen before any outcome

Source: `EDGE_WAVE3_DESIGN_1114.md` (notes folder), section "T11 BREADTH WASHOUT LONG" and SHARED RULES (T7-T12). The spec is frozen and implemented as written; every reading of an unclear point is listed under Deviations and was fixed BEFORE any return, R or placebo number was computed. Only signal counts, unit counts and stop-distance percentages (non-outcome) are looked at in the counting step. Research, not advice; no order, no forecast.

## Context

Question: when many coins are oversold at the same time and the first washout day has passed, does buying the oversold coins at the next daily open pay over the next 10 days, net of 12 bp and funding, on an out-of-sample (2024+) sample, with the episode (not the trade, not the coin) as the unit?
Regime: ungated primary cell, with a pre-registered strata prediction: episode mean > 0 when BTC close (signal day, i.e. the prior close of the entry open) > SMA200d, and mean <= 0 when below. Secondary row (second family cell): BTC prior close > SMA200d only. BTC smoothed BEAR/BASE/BULL rows (cycle column of `phase_daily.csv`, state counts only after 10 consecutive days) are always printed; a BEAR-state result is "not tradable if negative". A result positive only in the phase opposite to the prediction is labelled SIGN-FLIP.
Phase: MTS brain `cycle` (BTC only; row of day d built from closes through d-1, so the row of the entry day is free of entry-day information) is the BTC state for strata and placebo matching; the 6-phase label is not used. Smoothing (10 days) is OURS.
Session: none, because daily bars on a 24/7 market; entry at 00:00 UTC open of the day after the event signal bar, no session gate tested.
Entry: event day = first day with breadth B >= 15% after >= 7 consecutive days with B < 15%; on the event day every alive coin whose RSI14 (1d, Wilder) is <= 35 at that close gets a long at the next 1d open.
Regime mix: measured in RESULT (share of DEV and VAL events and episodes in BTC smoothed BULL/BASE/BEAR and above/below SMA200d); expected from the design note a BEAR-heavy DEV (2022) and a mixed VAL. No result is generalised beyond the mix seen.

## Rules (one frozen cell, no grid, no second pass)

| Item | Rule | Label |
|---|---|---|
| RSI | Wilder RSI14 on daily closes, FORMULAS.md section 1 (seed = mean of first 14 deltas; avg_loss 0 gives 100, flat gives 50) | SOURCED (Wilder; FORMULAS.md) |
| Breadth | B(d) = (number of alive coins with RSI14 <= 30 at close d) / (number of alive coins at d) | SOURCED level 30 (Wilder, NK RSI 70/30 per postmortem table, NK note not opened); the ratio is OURS |
| Alive | coin has a bar on day d, at least 200 daily bars of history through d (T11 section; the shared 260 is overridden by it) and a defined RSI | OURS |
| Event day | first day d with B(d) >= 15% and B(d-7..d-1) all < 15% (a day with no alive coin counts as below). Events on days with fewer than 30 alive coins are counted separately and excluded from verdicts | OURS (power-measured counts in the design note) |
| Episode | events within 14 days of the previous event (chain) merge into one episode; legs are averaged within an episode first. Episodes are built per cell from the cell's own events | OURS |
| Entry RSI | alive coin with RSI14 <= 35 at the event-day close | OURS |
| Entry | next 1d open (t+1), all flags use data through t | design |
| Stop | entry - max(2.5 x ATR14 at the signal bar, 8% of entry); ATR Wilder (first TR uses its own close as previous close, seeded by the mean of the first 14 TR) | OURS |
| Exit | first of stop or the close of day 10, entry day = day 1 (close of the bar d0 + 9). Stop checked on the daily low from the entry bar through day 10; a bar whose open is at or below the stop fills at the open; any bar with low <= stop exits at the stop (STOP WINS TIES, the close of that bar never rescues the trade) | OURS (hold set to 10 d in wave 3) |
| Fee | 12 bp round trip = `2 * BINANCE_TAKER + SLIPPAGE_RT_S13` imported from `MyTradingSys/backtest/fees.py`; no private cost constant | SOURCED (fees.py) |
| Funding | real signed 8h prints charged to the long on spot prices as perp proxy: sum of cached `rate` with entry_open < print <= end of the exit day (UTC midnight after the exit bar), expressed on entry notional. NO imputation: if the funding file does not cover the full nominal window the leg is flagged NOT_IN_DATA and its funding is 0 (reported as a count and as a REAL-only row) | SOURCED rule shape (shared rules); data-coverage handling OURS |
| R unit | risk = stop distance / entry (>= 8%, so fee in R <= 0.015); gross R = gross return / risk; net R = (gross - fee - funding) / risk; fee in R = 0.0012 / risk | OURS |
| Statistic | mean of episode means of net R (primary metric is R; percent is also printed) | OURS |
| Hole / ENDED | no leg may overlap the LUNA (2022-05-13..2022-05-31) or FTT (2022-11-15..2023-09-22) holes: such a leg is dropped (counted). A leg open at the last bar of a coin whose data ended more than 30 days before the pull (2026-11-14) exits there at the close, flagged ENDED-EXIT. A leg whose window runs past the data end of a coin that still trades is skipped (counted) | SOURCED (shared rules) |
| Seed | 1114 for every bootstrap and placebo | SOURCED (shared rules) |

## Data

Public Binance spot klines, root `F:/MTS/data_cache/binance`: `wave2-1114/spot_1d` (50 coins) and `combo-edge-miner-1114/spot_1d` (20 coins); BTC and ETH are in both, the wave2 file is used (68 distinct coins). Funding from `wave2-1114/funding` and `combo-edge-miner-1114/funding` (same preference). The named coin list is the union of the two folders' file lists, read at run time and written to `coins.json` next to RESULT. BTC cycle state: `mts_brains/phase_daily.csv` column `cycle`. Delisted coins are kept to their last bar. Survivorship direction: longs are biased UP (hindsight list of coins that were large enough to be cached; collapsed coins exit at their last close which a real trade may not reach). Data files and anything under `F:/MTS/data_cache` are never committed.

## Splits

DEV = event signal bar <= 2023-12-31; VAL = event signal bar >= 2024-01-01. An episode is assigned by its first event's signal bar and all its legs follow it. Fee 12 bp + signed funding.

## Pass bars (wave-2 bars 1-7 adapted by the T11 section, plus wave-3 bars 8-9)

Statistic for every bar: mean over episodes of the episode mean of net R, unless stated.
1. At least 8 VAL episodes (pooled DEV+VAL is a power row only, never the verdict), else UNDERPOWERED (never FAIL, never KILL).
2. VAL mean > 0 and episode-cluster bootstrap 95% CI low > 0 (2000 resamples of VAL episodes with replacement, seed 1114). Event-level and ISO-week-cluster CIs are printed as extra rows.
3. DEV mean > 0 (sign agreement).
4. Excess over the like-for-like placebo (1000 draws). Primary placebo: each real leg is replaced by a random entry of the same coin, same split, same smoothed BTC state, a day on which the coin's own RSI14 <= 35 and market breadth < 10%, the real leg's stop distance in %, the same 10-day exit rule and fees and funding, one placebo entry per real leg (same number of coins per draw). One draw = the mean over episodes of the episode means (episode membership of the real legs kept). Real mean must exceed the 97.5th percentile of the draws. The shared-rules same-window version (+/- 8 ISO weeks = 56 days of the real signal day, fallback to the whole split with the same state, then same coin and split without the state; fallbacks are counted) is the one used for the bar; the global version (whole split) is reported next to it. Secondary placebo: random days of the same coin, same split, same BTC state, no RSI or breadth condition (window and global).
5. Ex-best-2 episodes (drop the two highest VAL episode means) mean > 0 AND leave-one-event-out (drop each event, recompute the episode mean) stays > 0 for every dropped event.
6. Baseline: mean net return per day in position (leg net / days held, episode means) >= the equal-weight basket of ALL alive coins bought at the same entry open and held the same 10 days (no stop), same fee and funding, per day (net / 10; fewer for ENDED), same events.
7. Ex-LUNA/FTT (the two coins removed) > 0 and the top-3 coin removal (remove the coin with the largest summed VAL net R, three times in succession) > 0 at every step; failure = FRAGILE (reported, blocks PASS). Ex-ENDED row is reported too.
8. Leave-one-year-out (VAL years) stays > 0; failure = FRAGILE.
9. Rows by BTC smoothed state (BEAR/BASE/BULL), by BTC > SMA200d, and by year, DEV and VAL, always printed.
10. Dose-response: VAL events binned by event-day breadth (15-30%, 30-50%, >= 50%); the mean net R of the populated bins must rise (weakly monotone) with breadth; fewer than 2 populated bins = NOT_TESTABLE and blocks PASS (pooled DEV+VAL row also printed).
11. Pre-registered strata prediction on VAL (events): mean > 0 above SMA200d and <= 0 below; a missing stratum = NOT_TESTABLE and blocks PASS.
Family: 9 cells in wave 3 (T11 contributes 2: primary and the BTC > SMA200d row). Holm over the two T11 one-sided bootstrap p-values and the worst-case family adjustment (9 x p, capped at 1) are printed next to the verdict.

## Kill criteria

VAL episode mean <= 0 with >= 8 VAL episodes; or leave-one-event-out flips the sign of the VAL mean with fewer than 12 VAL episodes; or the real VAL mean is not above the 97.5th percentile of the primary placebo. Under 8 VAL episodes: UNDERPOWERED, descriptive only.

## Verdict vocabulary

PASS, FAIL, UNDERPOWERED, FRAGILE, SIGN-FLIP, NOT-A-PASS (descriptive). Order: fewer than 8 VAL episodes = UNDERPOWERED; any kill = FAIL; positive VAL mean with the strata prediction reversed = SIGN-FLIP; bars 1-6, dose-response and strata all met but bar 7 or 8 failed = FRAGILE; all met = PASS (still needs blind review); anything else = NOT-A-PASS. UNDERPOWERED is never called FAIL.

## Seen results

Only the design-note inventory counts (power designer's gate-day counts: about 19 VAL and 35 DEV events at the 7-day gap, 13-15 VAL episodes after the 14-day merge) and the file inventory of the cache. No outcome of this study or of any washout study was used to set a parameter. Known context from earlier studies (edge6_capitulation_breadth 28 events on 1h with DEV -1.7%; seven single-coin or intraday washout studies with 15-19 independent days) is cited only as the reason this daily market-wide version exists.

## Known weaknesses

Crash-date concentration (2020-03-12, 2022-05 LUNA, 2022-11 FTX, 2024-08-05, 2025-04-07, 2025-10-10) carries the winners in every washout study; this is a longer sample of the same event, not a fix. Cannot reach 20 independent units: UNDERPOWERED by design, run as a descriptive power row. Legs inside one event are highly correlated (same day, same market); they are averaged first. Survivorship biases longs up. Funding before 2020 is NOT_IN_DATA. Spot prices proxy a perp.

## Deviations

Readings of unclear points (all fixed before any outcome; none changes a frozen number of the spec):
1. Funding is not imputed (NOT_IN_DATA flag, funding 0) instead of the flat 1 bp/slot used in T6; the spec says no imputation.
2. Alive = 200 bars (T11 section) not 260 (shared rule): the T11 section is the more specific text.
3. Hold: "close of day 10" read as the close of the 10th daily bar with the entry bar as day 1.
4. Episodes are built per cell; an episode's split and all its legs' split follow its first event's signal bar.
5. The shared-rules same-window placebo (+/- 8 weeks) is applied to the T11 primary placebo (the T11 section states no window); the global variant is reported beside it.
6. Statistic: net R (stop-based simulation) averaged over episodes; percent is printed. Stop level uses ATR at the signal bar t (through t).
7. Dose-response and the strata prediction are evaluated on VAL events (pooled shown); the leave-one-event-out unit is the event.
8. ATR is Wilder as in T6 (the MTS core ATR is a plain SMA, FORMULAS.md section 12; this study's stop is OURS and follows T6).
9. Sd for the power gate: the counting step has no outcomes, so the DEV week-level sd is not available; the floor 1.0 R is used.
10. Events whose every leg has an incomplete window (last 10 days of data) are excluded and counted.
No data-driven deviation so far (all 68 coins present); any later one is appended here before outcomes.

## Power gate

Counting step (signals and units only, no outcome; `python t11_run.py count`, files `counts.json`, `coins.json`; priority class printed 0x4000 = BELOW_NORMAL):
- Universe: 68 coins (wave2 50 + miner 20, BTC/ETH once), daily bars 2017-08-17 .. 2026-11-13.
- Events found at B >= 15% with the 7-day gap: 49. Excluded because fewer than 30 alive coins (all 2018 to 2019-09): 9 (dates in `counts.json`). Events with no valid leg: 0. Events used: 40 (DEV 21, VAL 19).
- Episodes after the 14-day merge, primary cell: DEV 18, VAL 17. Secondary row (BTC close > SMA200d at the event): DEV 7 events / 7 episodes, VAL 6 events / 6 episodes (VAL has 13 events with BTC below SMA200d).
- Legs (alive coins with RSI14 <= 35 at the event close, valid 10-day window): 1540 (DEV 780, VAL 760). Legs skipped for hole or incomplete window: 0.
- VAL events by breadth bin: 15-30% 12, 30-50% 3, >= 50% 4 (dose-response is thin in the upper bins).
- Events by BTC smoothed state: DEV BEAR 12 / BASE 7 / BULL 2; VAL BEAR 7 / BASE 1 / BULL 11.
- Stop distance (non-outcome): median 23.0% of entry (ATR14 is large after a washout), minimum 8.0% (floor); fee in R at the median stop = 0.0052 R.

Gate inputs: n = 17 = VAL episodes of the primary cell (independent units, not trades or legs); sd = 1.0 R (the counting step has no outcomes, so the DEV week-level sd is not available; floor 1.0 R used, OURS); cost = 0.0052 R (measured median fee in R); m = 2 (T11 cells in the wave-3 family).

    python scripts/dev/prereg_gate.py --n 17 --sd 1.0 --cost 0.0052 --m 2 --sd-source "t11 counting step has no outcomes; floor 1.0 R (EDGE_WAVE3_DESIGN_1114.md shared rules)"
    n 17 sd 1 m 2 z_holm 2.241 MDE 0.747 R + cost 0.0052 = 0.753 vs max plausible gross 0.3; n needed 109
    BLOCK: do not freeze (write BLOCKED.md with these numbers)

Decision (OURS): BLOCK reported, not hidden. The run goes ahead because the wave-3 order says a BLOCK is reported and the run is still ordered (design shared rules, "Splits and statistics"). The spec already labels T11 UNDERPOWERED by design (cannot reach 20 independent units); a FAIL or UNDERPOWERED result is read as UNTESTED at this power, never as proof of no edge. A PASS would still need the blind review.

## Protocol

1. This file, the code (`t11_core.py`, `t11_stats.py`, `t11_run.py`) and the synthetic-bar tests (`test_t11_core.py`) are committed together BEFORE any outcome is computed.
2. Counting step: `t11_run.py count` prints signal, leg, event and episode counts and median stop % (no outcome), pasted below with the gate output.
3. Trades step: `t11_run.py trades` writes the trade list; then `t11_run.py stats` computes every bar above, `results.json`, `RESULT.md`.
4. Nothing is tuned after outcomes; no extra cells. A found mechanical bug is fixed, logged in RESULT, and rules and parameters are never changed.
