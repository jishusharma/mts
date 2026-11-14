# PRE_REG: T9 weekly-trend pullback LONG (2026-11-14), frozen before any outcome

Design: `EDGE_WAVE3_DESIGN_1114.md` (side-session notes folder), section "T9 WEEKLY-TREND PULLBACK LONG" plus SHARED RULES (T7-T12). The design is frozen; this file restates it with the implementation readings. Nothing here is computed from outcomes; only file lists and sidecars were looked at. Research, not advice; nothing is an edge until a fee-net out-of-sample result passes. SOURCED = named source; OURS = our choice, stated here. BIBLE.md has no line on weekly pullbacks; the touch rule, slope, stop, exit and cooldown are OURS.

## Context

Question: inside an intact weekly uptrend of a coin, does a week that tags the weekly 21 EMA and closes back above it add anything over simply being in the trend (placebo and basket row separate trigger from drift)?
Regime: BTC smoothed cycle state BULL or BASE (from the MTS brain `cycle` column of `phase_daily.csv`, OURS smoothing: a new state counts only after 10 consecutive days, until then the prior state holds), read on the entry day (the brain builds the row of day d from closes through d-1, so the entry-day row holds no entry-day close). Coin gate at the completed week: EMA21w > EMA55w, EMA55w above its value 4 weeks earlier, weekly close > EMA55w. The BTC BULL/BASE split is reported as two strata; BEAR is not traded (gate) and is printed as an empty row.
Phase: BTC cycle BULL or BASE (MARKUP-type conditions); brain 6-phase label reported as a descriptive cut only.
Session: none, because weekly bars and a Monday 00:00 UTC entry on a 24/7 market; no session gate tested.
Entry: the Monday 00:00 UTC open (daily bar open) right after a completed ISO week whose low <= EMA21w and close >= EMA21w, with the coin and BTC gates true at that week and the T6 DD20 rule false.
Regime mix: filled in RESULT from the data (shares of DEV and VAL trades in BTC smoothed BULL / BASE / BEAR, and of calendar Mondays). By construction no trade is in BEAR; the design notes VAL has 321 MARKUP days.

## Rules (one frozen cell, no grid, no second pass)

| Item | Rule | Label |
|---|---|---|
| Daily bars | Binance spot `<COIN>USDT` 1d UTC. Per coin the longest contiguous run of days, starting at its first Monday 00:00 UTC; whole 7-day weeks only (complete ISO weeks Monday 00:00 to Sunday 23:59). Rows outside the run are dropped and counted (this removes any LUNA / FTT hole: no trade spans a hole) | SOURCED (design shared rules; run rule copied in pattern from T6) |
| Weekly bar | close = Sunday close, high / low = over the 7 days. A weekly value is usable only from the following Monday bar (signal on completed week w, entry at the Monday open that follows) | SOURCED (design shared rules) |
| EMA | alpha = 2/(N+1), seeded by the SMA of the first N weekly closes, per MyTradingSys/backtest/layers/FORMULAS.md section 4 (EMA). EMA21w valid from weekly index 20, EMA55w from index 54 | SOURCED (FORMULAS.md) |
| EMA pair 21 / 55 | weekly closes | SOURCED pair (BIBLE line 50 Krown 21/55/200 moving averages); weekly timeframe and EMA type OURS |
| Coin trend flag | EMA21w(w) > EMA55w(w) and EMA55w(w) > EMA55w(w-4) and close(w) > EMA55w(w). First week with the flag defined is index 58 (55 bars + 4-week slope), so a coin enters only after 55 weekly bars (stricter in practice: 59 weekly bars) | OURS (slope > 0 over 4 weeks OURS; 55-bar entry SOURCED from the design) |
| Alive coin | >= 260 daily bars of history on the signal date (implied by the 59-weekly-bar rule). Signal dates with fewer than 30 alive coins are excluded from the verdict and counted separately | SOURCED (design shared rules) |
| BTC gate | smoothed cycle (above) is BULL or BASE on the entry day | SOURCED idea (BIBLE s5), thresholds and smoothing OURS |
| Touch rule | week w: low(w) <= EMA21w(w) and close(w) >= EMA21w(w) | OURS |
| T6 exclusion | skip the signal if the T6 DD20 rule is true at week w: close(w) <= 0.80 x max weekly close(w-8 .. w-1) | OURS (rule per the T6 PRE_REG, so T6 and T9 cannot double count) |
| Cooldown | per coin, a new trade only if entry day >= previous TRADE entry day + 56 days. Signals skipped by the T6 exclusion do not start the clock. Trades of one coin may overlap in time (cooldown 56 d < hold cap 84 d); the number of overlapping trades is reported | OURS (literal reading of the design) |
| Entry | Monday open after the signal week, price = daily open. No look-ahead: every flag uses data through the Sunday bar | SOURCED (design shared rules) |
| Stop | stop = min(week low(w) - 0.5 x ATR14(1d, Wilder at the Sunday bar), entry x (1 - 0.015)); so distance >= 1.5% of entry (floor). Risk unit R = (entry - stop) / entry. ATR per FORMULAS.md (first TR uses its own close as previous close, seed = mean of first 14 TR). A daily bar whose low <= stop stops the trade: fill at the open if the open <= stop (gap), else at the stop. Stop wins ties (checked before any other exit on the same bar) | OURS (0.5 ATR and 14 OURS; 1.5% floor SOURCED from design shared rules) |
| Exit | first of: stop; first completed weekly close below EMA55w of the trade's own weeks (exit at the next Monday open); 84 days cap (12 weeks, exit at the Monday open 84 days after entry). Trend exit is evaluated on week w+1 and later (entry week onward) | OURS |
| Data end | a trade unresolved at the coin's last bar: if the coin ended (last bar more than 30 days before the data pull 2026-11-14) it exits at the last close, flagged ENDED; if the coin still trades the trade is excluded (counted) | OURS |
| Fee | 12 bp round trip = 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 imported from `MyTradingSys/backtest/fees.py`, subtracted from the return; fee in R = fee / (stop distance %) | SOURCED (fees.py) |
| Funding | a perp is implied: real signed funding per 8h print with entry_open < print_time <= end of the exit instant, paid by the long (negative = credit), on entry notional. Where the coin's funding cache does not cover the window NO funding is imputed: funding = 0, the trade is flagged FUNDING NOT_IN_DATA and counted per split; a descriptive sensitivity row charges a flat 1 bp / 8h on those trades (never a verdict row). Basis between spot and perp is not modelled and flagged | SOURCED (design: "No funding imputed ... reported as NOT_IN_DATA row"); flat sensitivity OURS |
| Primary metric | net R per trade = (gross return - fee - real funding) / risk unit. Gross R, net R, fee R and net % are all reported. The 3R-capped row = min(net R, 3) per trade (the exit is trend-shaped), used for bar 5 | OURS (row definition) |
| Seed | 1114 | OURS |

## Data

Public Binance spot klines in `F:\MTS\data_cache\binance\wave2-1114\spot_1d` (50 coins) and `F:\MTS\data_cache\binance\combo-edge-miner-1114\spot_1d` (20 coins); funding in the `funding` folder next to each (columns ts, rate). Universe = the union of the two folders' file lists read at run time (BTC and ETH once; the wave2 file is used when a coin is in both), the named list of coins is written into `coverage.json` by `t9_trades.py` and quoted in RESULT. Coins are not added, swapped or dropped for performance; a coin is kept if it ever has the flag defined (>= 59 complete weekly bars). Delisted coins stay to their last bar. Phase file: `F:\MTS\data_cache\mts_brains\phase_daily.csv` (BTC only). Committed tests never read the cache.
Survivorship: the universe is a hindsight list of coins alive in 2019-2021 that stayed large enough to be fetched; longs are biased UP. RESULT carries an ex-ENDED row and an ex-LUNA/FTT row (coins LUNA and FTT removed).

## Splits

DEV = signal bar (completed Sunday week) <= 2023-12-31; VAL = signal bar >= 2024-01-01. The entry Monday follows its signal bar by one day, so a week whose Sunday is 2023-12-31 is DEV and the Monday 2024-01-01 entry belongs to DEV by signal bar. Weeks are ISO weeks of the ENTRY Monday for clustering.

## Pass bars (primary row: net R per trade, uncapped, unless stated)

Statistic: mean net R per trade. Cluster unit = ISO entry week, moving-block bootstrap, block length 4 weeks (overlapping blocks over the calendar series of weeks from the first to the last entry week of the split, empty weeks included with zero sum and zero count; concatenate ceil(W/4) random blocks, trim to W weeks; resampled mean = sum of R / number of trades), 2000 resamples, seed 1114. The episode (4-week block with at least one trade) count is the second unit.
1. VAL fresh: n >= 30 trades and >= 20 distinct entry weeks, else UNDERPOWERED (never FAIL, never KILL).
2. VAL mean net R > 0 and the bootstrap 95% CI low (2.5th percentile) > 0. One-sided p = (resampled means <= 0, plus 1) / 2001.
3. DEV mean net R > 0 (sign agreement; DEV n < 10 leaves bar 3 UNDERPOWERED).
4. Placebo (like-for-like): for each real VAL trade draw one random Monday of the SAME coin, SAME split, inside +/- 8 ISO weeks of the real entry (the real trade's own entry excluded only when an alternative exists), where the weekly coin flag is true at the preceding completed week, the T6 DD20 rule is false, and the BTC smoothed state equals the real trade's state (so only the touch trigger is removed); trade it with the SAME stop distance in % of entry, the same exit rule, fee and funding rule; R uses the real trade's risk unit. Draw = mean over the matched set; 1000 draws, seed 1114. Real mean must be >= the 97.5th percentile of draw means and excess (real minus mean of draws) > 0. Global variant (any flagged Monday of the coin in the split, no window) is reported next to it, not a bar. Real trades with an empty candidate set are skipped and counted.
5. Ex-best-5 entry weeks of VAL on the 3R-capped row: drop the 5 ISO weeks with the largest summed capped R; the mean of the rest must be > 0 (ex-best-2 when VAL entry weeks < 30). The uncapped ex-best row is reported next to it.
6. Baseline: mean NET daily return in position of the strategy (pooled sum of trade net % divided by pooled days held) must be >= the mean daily return of the equal-weight basket of flagged coin-weeks (coin flag true at the preceding completed week, T6 DD20 false, BTC state BULL/BASE), over the same split, taken over the calendar days of the ISO weeks in which at least one strategy trade is open; basket days are charged real funding where covered and no fee (buy-and-hold side matched). Both splits are printed.
7. Top-3-coin removal (sequential, by summed VAL net R): the mean must stay > 0 after removing the top 3 coins, else FRAGILE (blocks PASS).
8. Leave-one-year-out on VAL entry years (2024, 2025, 2026): the mean net R stays > 0 after dropping any one year, else FRAGILE. The same over DEV+VAL pooled is reported. A result positive only in DEV (2020-21) is flagged FRAGILE.
9. Rows by BTC cycle state (BULL / BASE / BEAR) and by year (DEV and VAL separately) are always printed. A result positive only in the phase opposite to its gate (BEAR) is SIGN-FLIP, not PASS (no trade can be in BEAR by the gate; an empty BEAR row is printed).
Family: 9 cells over T7-T12; the Holm adjustment over the family is reported as the worst case min(1, 9 x p) next to the per-study value (m = 1, equal to p).

## Kill criteria

KILL if any of (and only when bar 1 holds): (a) VAL mean net R <= 0; (b) placebo (same-window) excess <= the 97.5th percentile with >= 60 VAL trades; (c) mean daily net return in position is below the basket on both DEV and VAL. A killed line cannot be PASS.

## Verdict vocabulary

PASS = bars 1-8 all hold and no kill fires. FAIL = bar 1 holds and one of bars 2-6 or a kill criterion fails (first failing bar named, KILL added when a kill fired). FRAGILE = bars 1-6 hold and bar 7 or bar 8 fails. UNDERPOWERED = bar 1 fails (reads UNTESTED, never proof of no edge). Others: SIDE-SPLIT, CARRY-ONLY, NOT-A-PASS (descriptive) are not expected for this single-side cell. Any PASS stops the line: blind review and testnet-forward need the operator's go.

## Seen results

Only inventory counts from the design note (coin-weeks in the flag about 25% of VAL coin-weeks; weeks with >= 5 flagged coins about 86 of 150; estimate 50-60 entry weeks, 25-35 waves, about 150 trades). No outcome of any T9 trade, return or placebo has been seen. Related failed studies named in the design: edge7/edge8 (daily breakout trend following, below buy and hold), edge9 (weekly streak, no trend gate), T3 (early uptrend), T6 (20% dip). Nothing was tuned against them.

## Known weaknesses

- Drift and beta: DEV (2020-21) is a 10x alt bull while VAL (2024+) is an alt-weak bull, so DEV dominates; any long in a flagged trend wins in a bull. Only the placebo and the basket row separate trigger from drift.
- Weeks, not trades, are the sample: coins move together; expect few independent units and a wide CI. The gate below is expected to BLOCK on VAL alone.
- Survivorship (hindsight universe, longs biased up); collapsed coins exit at a last close that may not be tradable.
- Spot prices stand in for perps; funding is real only where cached, otherwise NOT_IN_DATA (zero); no fill, borrow or liquidity model.
- Same-coin trades can overlap (cooldown 56 d < cap 84 d).
- Stop 0.5 ATR, slope window, cooldown, 10-day BTC smoothing and the exclusion are OURS.

## Deviations

Written before any outcome was computed.
- D1: the design asks for `prereg_gate --sd` from the DEV week-level sd of the counting step, but the counting step holds no outcomes (signal and unit counts only), so a week-level sd of R cannot exist yet. The floor 1.0 R is used. The measured sd is reported in RESULT.
- D2: longest-contiguous-run rule per coin (T6 pattern) is how the LUNA / FTT holes are honoured; shorter runs of a coin are dropped and counted in `coverage.json`.
- D3: gate `--n` = number of non-overlapping 4-week blocks (starting at the first VAL entry week) that contain at least one counted VAL signal ("effective 4-week blocks"); `--cost` = mean fee in R over VAL signals (12 bp / stop %, known at signal time, not an outcome).
- D4: counting step counts signals (before the data-end exclusion of unresolved open trades, which needs the exit path); the final trade count can be lower by the number of excluded open trades at the end of data.
- D5: psutil is not installed on this machine; the priority class is set through ctypes SetPriorityClass 0x4000 (the stated fallback).

## Counting step (signal and unit counts only, no outcomes)

Measured by `t9_count.py` (output `counts.json`, no outcomes): universe 68 coins, all 68 reach a defined flag.

| Split | Signals | Entry weeks | Effective 4-week blocks | Signals on dates with >=30 alive coins | BULL / BASE signals | Mean fee in R | Median stop % | Weeks with >=5 flagged coins |
|---|---|---|---|---|---|---|---|---|
| DEV | 133 | 45 | 24 | 131 | 68 / 65 | 0.0078 | 20.9 | 78 |
| VAL | 103 | 54 | 24 | 103 | 93 / 10 | 0.0096 | 15.2 | 83 |

Signal counts are before the data-end exclusion (D4). VAL meets bar 1 on counts (>=30 trades, >=20 entry weeks) provided about 100 trades survive.

## Power gate

Command: `python scripts/dev/prereg_gate.py --n 24 --sd 1.0 --cost 0.00955 --m 1` (n = effective 4-week VAL blocks, sd floor 1.0 R per D1).

```
n 24 sd 1 m 1 z_holm 1.960 MDE 0.572 R + cost 0.00955 = 0.581 vs max plausible gross 0.3; n needed 93
BLOCK: do not freeze (write BLOCKED.md with these numbers)
```

Reported BLOCK: the run still goes ahead as ordered (design: a BLOCK is reported, not hidden). A VAL result can only clear bar 2 with a very large effect; a miss is more likely UNTESTED-in-spirit than evidence of no edge.

## Protocol

1. This PRE_REG, `t9_core.py`, `t9_stats.py`, `t9_trades.py`, `t9_count.py` and `test_t9_core.py` are committed together before any outcome is computed.
2. `t9_trades.py` writes the trade list and coverage; `t9_stats.py` computes the pass bars, RESULT.md and results.json. Rules and parameters are never changed after the freeze commit; a mechanical bug is fixed and logged in RESULT.
3. A later stage re-derives the verdict from this file's bars and runs the adversarial look-ahead / fee audit.
