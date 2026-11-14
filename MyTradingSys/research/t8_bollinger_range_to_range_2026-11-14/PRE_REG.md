# PRE_REG: T8 Bollinger range-to-range, 68 coins, 1d primary and 4h secondary (2026-11-14), frozen before any outcome

Design: `EDGE_WAVE3_DESIGN_1114.md` (notes folder), section "T8 BOLLINGER RANGE-TO-RANGE" and SHARED RULES (spec frozen; implemented as written, deviations listed under "Deviations"). Frozen BEFORE any trade, return, placebo or mirror number is computed. Only availability checks (file lists, `.meta.json` sidecars) and signal / unit counts (no outcome) were looked at. Research, not advice; nothing is an edge until a fee-net out-of-sample result passes. SOURCED = named source; OURS = our choice, stated here. The Bollinger range-to-range claim is the operator's own; BIBLE.md has no line on Bollinger, so every parameter not tagged SOURCED below is OURS and is never called the trader's.

## Context

Question: inside a ranging coin, does a close outside the Bollinger band that closes back inside travel to the opposite band within 20 days (7 days on 4h) by more than a stop of at least 1.5% (2.5% on 4h) costs, after fees, on 68 coins and out of sample?
Regime: coin-level range gate known at the signal bar close: ADX14 (1d, Wilder) < 20 AND (highest high minus lowest low of the last 30 daily bars) / mean close of those 30 bars <= 0.30. BTC phase label in {ACCUM-RANGE, DISTRIBUTION} and the ACCUM-RANGE-only subset are reported strata, not gates (the label gate alone leaves about 22 VAL weeks).
Phase: no BTC phase gate. Strata printed per cell from `F:\MTS\data_cache\mts_brains\phase_daily.csv`, row of the entry date (the brain builds day d from closes through d-1, so it holds no signal-bar-future information): (a) label ACCUM-RANGE / DISTRIBUTION / other, (b) BTC smoothed cycle BEAR / BASE / BULL (a cycle state counts only after 10 consecutive days, until then the prior state holds, OURS), (c) calendar year.
Session: none; 24/7 market, 1d and 4h bars, no session gate tested.
Entry: signal on completed bar t (close back inside the band after a close outside), entry at the OPEN of bar t+1 (never earlier).
Regime mix: filled in RESULT from the data (share of DEV and VAL trades by BTC label, smoothed cycle and year, and the share of VAL range-gated coin-days). Not known at freeze; no result is generalised beyond the mix seen. VAL (2024+) holds the 2024 bull, 2025 and the 2026 slide.

## Rules (one frozen cell per timeframe, no grid, no second pass)

| Item | Rule | Label |
|---|---|---|
| Universe | 68 distinct coins = union of the file lists of `binance/wave2-1114/spot_1d` (50) and `binance/combo-edge-miner-1114/spot_1d` (20), BTC and ETH once (wave2 copy). The list is read at run time and written to `coverage.json`. Delisted coins kept; a trade open at a coin's last bar closes there, flagged ENDED. Coin ENDED = final segment's last bar closes more than 30 days before the newest bar in the universe | OURS (design note) |
| Segments | per coin, each maximal run of consecutive bars (no gap) is a segment; indicators restart in each segment and nothing spans a gap (a trade whose window would cross a segment end is skipped, counted GAP_SPAN) | OURS |
| LUNA / FTT holes | no trade whose entry..planned-exit span intersects LUNA 2022-05-13..2022-05-31 or FTT 2022-11-15..2023-09-22 (coins LUNA, FTT only); counted HOLE | OURS (design note) |
| Alive | coin alive at bar t when its segment holds >= 260 daily bars up to and including t (1d); 4h cells use the 1d count at the last completed 1d bar. Signal dates with fewer than 30 alive coins are excluded from verdicts and counted separately | OURS (design note) |
| Bollinger | mid = SMA20 of closes, sd = POPULATION sd of the same 20 closes, upper/lower = mid +/- 2 sd; tested bar's own values; FORMULAS.md section 22 | SOURCED (Bollinger standard, TradingView ta.bb; the claim "never spoken as numbers") |
| ADX gate | Wilder ADX 14 on 1d bars < 20; FORMULAS.md section 30 (first defined at bar 27) | SOURCED (Wilder 1978); threshold 20 SOURCED as the textbook "no trend" line |
| Range gate | (max high - min low over last 30 daily bars incl. t) / mean close of those 30 bars <= 0.30 | OURS |
| 4h gate | the 1d gate and alive flag of the last COMPLETED 1d bar at the signal bar's close (1d bar with open D counts when D + 1d <= close time of the 4h bar) | OURS (design note) |
| Raw re-entry (long) | close[t] > lower[t] AND some bar j in t-3..t-1 has close[j] < lower[j] (each against its own band). First re-entry only: also NOT (the same condition held at t-1). Short: mirror at the upper band (close[t] < upper[t] and an earlier close above upper in t-3..t-1) | OURS (window 3 and first-re-entry reading OURS) |
| Width filter | (upper - lower) / mid at t >= 0.10 | OURS |
| Signal | raw re-entry AND gate AND alive AND width. Cooldown per coin and side: a new signal bar must be >= 10 bars (1d) / 12 bars = 2 days (4h) after the previous signal bar of that coin and side; the clock starts when a signal fires, whatever later filter drops it. Same-coin, same-side trades may overlap in time | OURS |
| Entry | open of bar t+1. No t+1 bar = no trade | SOURCED (shared rules) |
| Stop | long: lowest low of the bars from the FIRST bar of the consecutive outside-close run (the run containing the most recent outside close in t-3..t-1) through t, minus 0.5 x ATR14[t] (own timeframe, Wilder, FORMULAS.md first-TR rule); then stop = min(that, entry x (1 - floor)); floor 1.5% (1d) / 2.5% (4h). Short mirror (highest high + 0.5 ATR, max(that, entry x (1 + floor))) | OURS |
| Target | opposite band value at signal bar t, frozen at entry (long: upper[t]; short: lower[t]). Entry open already at or beyond the target = no trade, counted TARGET_BEHIND | OURS (operator's claim) |
| Exit | first of: stop, target, time cap. Bars from t+1 (entry bar) through t+20 (1d) / t+42 (4h); time exit at the close of the last bar. Per bar, the stop is checked first (STOP WINS TIES): long stop hit when low <= stop, fill at the stop, or at the bar open when the open is at or below it (STOP_GAP, bars after the entry bar); target hit when high >= target, fill at the target (no gap improvement, conservative). Short mirrored | OURS |
| Data end | window check by availability only (no outcome): planned last bar beyond the segment end = skip INCOMPLETE if the coin is not ENDED, skip GAP_SPAN if another segment follows, exit at the last close flagged ENDED if the coin is ENDED | OURS |
| Fee | 12 bp round trip = 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 imported from `MyTradingSys/backtest/fees.py`; no private cost constant | SOURCED (fees.py) |
| Funding | real signed funding per 8h print, longs pay positive rate, shorts receive it (a perp is implied for every trade), prints with entry_open < print_time <= end of the exit bar, on entry notional. Coverage rule: first print <= entry and last print >= exit end, else the trade is NOT_IN_DATA: funding is NOT imputed (term = 0) and the count is reported. Verdict row = net of fee and real funding where available; rows reported side by side: gross, fee-only net, fee + funding net, and a funding-covered-only subset | OURS (row definition) |
| R | R = (return) / (stop distance as a fraction of entry). gross R, fee R = 0.0012 / stop%, net R = (gross - fee - funding) / stop%. Net R is the primary metric, percent returns are reported next to it | OURS |
| Mirror (negative control, primary number) | for every real trade, the reflected trade: opposite side at the same entry bar and price, stop distance and target distance (in %) equal to the real trade's, mirrored (a real short at the upper band re-entry gives a long with stop below and target above at the same percentages), same exit rules, same fee, same funding rule. Real minus mirror = per-trade difference in net R | OURS (design note) |
| Weekly bars | NOT used anywhere in this study (the shared weekly-resample Sunday-spike unit test therefore does not apply; an ISO-week assignment test replaces it) | -- |
| Seed | 1114 | OURS |

## Data

Public Binance spot klines, root `F:\MTS\data_cache` (never committed): 1d `binance/wave2-1114/spot_1d`, `binance/combo-edge-miner-1114/spot_1d`; 4h `.../spot_4h` in the same two folders; funding `binance/wave2-1114/funding`, `binance/combo-edge-miner-1114/funding` (wave2 first, then miner); phase `mts_brains/phase_daily.csv` (BTC only). Newest bar in the 1d files is 2026-11-12 00:00 UTC (checked in the `.meta.json` sidecars, whose fetched_utc is 2026-11-14), no partial bar. Survivorship: the universe is a hindsight list of coins that were liquid enough to be fetched; collapsed coins (LUNA, FTT and any ENDED coin) exit at their last close, which a real position might not have got, so LONGS ARE BIASED UP and SHORTS BIASED DOWN. Every RESULT carries an ex-ENDED row and an ex-LUNA/FTT row. Short side priced on spot as a proxy for a perp (basis not modelled).

## Splits

DEV = signal bar <= 2023-12-31; VAL = signal bar >= 2024-01-01 (by signal bar open date; 4h likewise). Per design (deliberately not `splits.py`, whose DEV/VAL/HOLDOUT dates differ).

## Statistics

- Unit: ISO entry week over all coins (a week index counted on the calendar, empty weeks inside the sample kept with zero trades), moving-block bootstrap, block 2 weeks, 2000 resamples, seed 1114; resampled mean = sum of trade values in the drawn weeks / number of trades in them. One-sided p = (resampled means <= 0, plus 1) / 2001. Second unit (descriptive): BTC range episode = a maximal run of consecutive days whose BTC label is ACCUM-RANGE or DISTRIBUTION; trades are assigned by entry date.
- Placebo (bar 4), same-window variant: for each real VAL trade the candidates are bars t' of the SAME coin and segment, same split, gate true, alive, date-ok, within +/-56 days of the real signal bar (t' != t), with entry t'+1 passing the same availability rules (no band trigger, no width filter), simulated with the SAME side, SAME stop % and SAME target % as the real trade and the same time cap, same fee and funding rule; net R divides by the real trade's stop %. If a trade has more than 100 candidates, 100 are drawn once (seed 1114). One draw = the mean over trades of one random candidate each; 1000 draws, seed 1114. Global variant: the same with candidates = any gate-true day of the coin and split (capped at 100). Trades with no candidate are dropped from the placebo set and counted. Real mean must exceed the 97.5th percentile of the draw means (bar 4), and the excess CI low must be > 0 where excess_i = real net R_i minus the mean over that trade's candidates, block-bootstrapped as above.
- Baselines (bar 6), per trade over the same candidates: (a) random-day symmetric 1:1 bracket (stop % = target % = the real stop %, same cap); (b) hold-the-range: same coin held the cap length from t'+1 open to the last bar close in the same direction. Daily net return = net % return / days in position (days = bars held x bar length in days). Real trade's daily net return, averaged over trades, must be >= the average of each baseline (side matched by construction).

## Pass bars (VAL, primary cell 1d, net R unless stated; the 4h cell uses the same bars)

1. VAL n >= 200 trades AND >= 40 distinct entry weeks, else UNDERPOWERED (never FAIL, never KILL).
2. VAL mean net R > 0 and block-bootstrap 95% CI low > 0.
3. DEV mean net R > 0.
4. Placebo: real mean > 97.5th percentile of the same-window draws, and excess CI low > 0.
5. Ex-best-5 entry weeks (by summed net R) mean > 0 (ex-best-2 when VAL weeks < 30).
6. Baseline: real daily net return >= random-day bracket and >= 20-day hold (above).
7. Top coin removal keeps the mean > 0; removing the top 3 coins one after another is also reported and a result <= 0 there is FRAGILE (shared rule 7; wave-2 wording is the single top coin, this reading satisfies both).
8. Leave-one-year-out (VAL years 2024, 2025, 2026): every remaining mean > 0, else FRAGILE.
9. Rows by BTC cycle state (BEAR/BASE/BULL), by BTC label and by year are always printed. There is no cycle gate in this study, so the SIGN-FLIP label cannot arise and is reported as not applicable.
T8 extras: M. real minus mirror mean net R > 0 (CI reported). S. both sides' VAL means > 0, else SIDE-SPLIT. W. worst entry week sum of net R > -4 R (loss-tail guard), else FRAGILE. Holm: m = 2 (1d cell, 4h cell); this study reports the Holm-adjusted p of the two bootstrap p-values and the worst-case family value min(1, 9 p); a PASS with an adjusted p > 0.05 is labelled MULTIPLICITY-FLAGGED.

## Kill criteria

Primary VAL net R <= 0, OR real minus mirror <= 0, OR placebo excess not above the 97.5th percentile with >= 200 VAL trades. Then 1d range-to-range is dead. 4h is untested-then-dead only if its own row also fails.

## Verdict vocabulary

PASS, FAIL, UNDERPOWERED, FRAGILE, SIDE-SPLIT, CARRY-ONLY, NOT-A-PASS (descriptive). Assembly, applied in this order to each cell: bar 1 fails -> UNDERPOWERED; else any kill criterion or any of bars 2-6 or M failing -> FAIL; else S failing -> SIDE-SPLIT; else bars 7, 8 or W failing -> FRAGILE; else PASS (plus MULTIPLICITY-FLAGGED where it applies). The headline verdict is the 1d cell; 4h is a second row.

## Seen results

Only the design note's inventory counts (power designer: about 2117 raw coin-signals under a proxy flag in VAL, 45-90 expected VAL entry weeks, 400-700 trades) and file availability. No outcome of this rule set has been computed.

## Known weaknesses

Short-volatility payoff (many small wins, rare breakout losses). Shared regimes: in a bull VAL range-flagged alts break up, so longs may win and shorts lose (SIDE-SPLIT is a real possibility). Spot stands in for perps. Overlapping same-side trades inside one coin are not independent (the week-block bootstrap absorbs part of it). The 15m BTC fee-dominated failures (bb_range_to_range, bb_long_window) say nothing about 1d either way.

## Deviations

(Written before outcomes; none forced by missing data at freeze time unless listed.)
1. Power gate sd: the design asks for the DEV week-level sd measured in the counting step; the counting step holds no outcomes, so the floor 1.0 R is used with --sd-source naming this line. The realised sd is reported in RESULT.
2. `weekly bars` are unused, so the weekly Sunday-spike test is replaced by an ISO-week assignment test.
3. `splits.py` dates are not used (design DEV/VAL dates are used instead).
4. 4h cache gaps: the 4h files miss bars for many coins; segments restart indicators (see Rules, Segments) and the 4h cell inherits fewer usable bars than the 1d cache implies. Not a rule change.
5. psutil is not installed on this machine, so the BelowNormal priority is set with the ctypes SetPriorityClass fallback (class printed by every data script).

## Power gate

Inputs: n = independent units = VAL ISO entry weeks of the cell (1d: 76, 4h: 99; never trades), sd 1.0 R = the floor from the design (deviation 1: no DEV outcome exists at the counting step; realised sd reported in RESULT), cost = 12 bp / median planned stop % (1d median stop 7.24% -> 0.0166 R; 4h median stop 3.93% -> 0.0305 R; funding not in the gate cost), m = 2 (Holm family of the T8 cells). Commands run in the worktree:

    python scripts/dev/prereg_gate.py --n 76 --sd 1.0 --cost 0.0166 --m 2 --sd-source "EDGE_WAVE3_DESIGN_1114.md shared rules: floor 1.0 R (no DEV outcomes at counting step)"
    n 76 sd 1 m 2 z_holm 2.241 MDE 0.353 R + cost 0.0166 = 0.370 vs max plausible gross 0.3; n needed 118
    BLOCK: do not freeze (write BLOCKED.md with these numbers)      (exit 1)

    python scripts/dev/prereg_gate.py --n 99 --sd 1.0 --cost 0.0305 --m 2 --sd-source "EDGE_WAVE3_DESIGN_1114.md shared rules: floor 1.0 R (no DEV outcomes at counting step)"
    n 99 sd 1 m 2 z_holm 2.241 MDE 0.310 R + cost 0.0305 = 0.340 vs max plausible gross 0.3; n needed 131
    BLOCK: do not freeze (write BLOCKED.md with these numbers)      (exit 1)

Both cells print BLOCK. Per the design ("a BLOCK is reported, not hidden, and the run is still ordered") the run goes ahead and no BLOCKED.md stops it; the BLOCK is carried into RESULT: a small positive effect can be below the minimum detectable effect at this many independent weeks, so a non-significant result here is UNDERPOWERED-in-spirit even when bar 1's count (200 trades, 40 weeks) is met.

## Counts (counting step, no outcomes)

Counting step, no outcome computed (`python t8_trades.py count`, output `counts.json`; availability and signal conditions only):

| item | 1d | 4h |
|---|---|---|
| coins loaded | 68 | 68 |
| raw signals (all filters, cooldown applied) | 697 | 1740 |
| dropped: signal date with < 30 alive coins | 27 | 83 |
| dropped: TARGET_BEHIND / INCOMPLETE / GAP_SPAN | 1 / 3 / 0 | 0 / 1 / 1 |
| trades (both sides) | 666 | 1655 |
| DEV trades (long / short) | 335 (157 / 178) | 817 (366 / 451) |
| VAL trades (long / short) | 331 (149 / 182) | 838 (402 / 436) |
| DEV entry weeks | 84 | 121 |
| VAL entry weeks (independent unit, gate n) | 76 | 99 |
| planned stop % p10 / p50 / p90 | 4.48 / 7.24 / 11.43 | 2.50 / 3.93 / 7.67 |
| planned target % p10 / p50 / p90 | 9.00 / 13.38 / 20.28 | 9.18 / 11.59 / 17.38 |

Universe: 68 coins on 1d and 68 on 4h; newest bar 2026-11-13; dates with fewer than 30 alive coins: 618 calendar days (first date with >= 30 alive coins: 2020-01-10); ENDED coins: EOS, FTM, ICX, MATIC, MKR, OCEAN, OMG, STORJ, WAVES, XMR. The 1d cache has gaps only for LUNA and FTT (2 segments each); the 4h cache has missing bars for many coins (up to 10 segments for BTC, listed in counts.json), so 4h indicators restart after each gap and no 4h trade spans one (1 trade dropped GAP_SPAN). Fewer VAL trades than the design's 400-700 expectation (1d: 331) because the frozen gate, width filter and cooldown cut them; bar 1 (>= 200 trades, >= 40 weeks) is still met on count.

## Protocol

1. Write this file, code and synthetic-bar tests; tests pass. 2. Counting step: signals and units only, pasted here with the gate output; commit PRE_REG + code + tests before any outcome. 3. Trades list (one row per trade with mirror columns, no pooled statistic), then statistics and RESULT.md / results.json. 4. A later stage ships and adversarially checks. No parameter is changed after an outcome is seen; no extra cells.
