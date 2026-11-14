# PRE_REG: T10 bear-phase relief-rally SHORT, 1d, 68-coin union (2026-11-14), frozen before any outcome

Spec: `EDGE_WAVE3_DESIGN_1114.md` (side-session notes), shared rules T7-T12 plus the section "T10 BEAR-PHASE RELIEF-RALLY SHORT", implemented as written. Frozen BEFORE any trade, return, placebo or pooled statistic is computed; only signal and unit counts (`counts.json`) were looked at. Research, not advice; nothing is an edge until a fee-net out-of-sample result passes. SOURCED = named source; OURS = our choice, stated here.

## Context

Question: in a BTC bear regime, does a coin in a downtrend that rallies at least 12% off its 10-day low close into its 20-day average and then prints a red rejection bar fall back to the start of the rally within 10 days, fee-net, on a 7-10% stop?
Regime: BTC prior close below its SMA200d is the gate (BIBLE s5 "daily loss of the 200-day": idea SOURCED, use OURS). The narrower BTC brain labels MARKDOWN and RELIEF and the smoothed BEAR cycle state are strata (rows), not gates. Coin flag: close < SMA50 and SMA50 below its value ten days earlier (OURS).
Phase: BTC gate days are the bear phase; strata printed from `F:/MTS/data_cache/mts_brains/phase_daily.csv` (label of day d is built from closes through d-1, so the entry-day row uses no entry-day close). Smoothed cycle state: a new state counts only after 10 consecutive days (OURS), until then the prior state holds. Count of gate days: DEV 1094, VAL 402 (402 matches the design).
Session: none, because daily bars on a 24/7 market; no intraday session is tested.
Entry: short at the open of the bar after the signal bar. Signal bar t (all values through t): rally = close_t >= 1.12 x lowest close of bars t-10..t-1; rejection = high_t >= SMA20_t, close_t < open_t, close_t < low_{t-1}; BTC gate and coin downtrend flag true at t; coin alive (>= 260 daily bars) and >= 30 coins alive that day. Per-coin cooldown 10 days.
Regime mix: filled in RESULT from the data (entries by smoothed BTC cycle state BULL / BASE(range) / BEAR for DEV and VAL, and gate-day counts). By construction every trade is on a BTC-below-SMA200d day, so the mix is "bear by the gate"; the cycle strata show how much of it is a smoothed BEAR cycle versus BASE or BULL.

## Rules (one frozen cell, no grid, no second pass)

| Item | Rule | Label |
|---|---|---|
| Data | Binance spot `<COIN>USDT` 1d, UTC, `F:/MTS/data_cache/binance/wave2-1114/spot_1d` (50 coins) union `.../combo-edge-miner-1114/spot_1d` (20 coins); BTC and ETH are in both (wave2 file used) = 68 distinct coins, read at run time (names in `counts.json`). Delisted coins kept. Perp implied, spot prices as proxy (basis flagged) | SOURCED shared rules |
| Contiguity | A coin's bars are split into contiguous runs (no missing day); indicators never bridge a gap; a trade needs its whole window inside one run | OURS |
| Alive | bar index >= 259 inside its run (>= 260 bars of history). Signal dates with fewer than 30 alive coins are excluded from verdicts and counted separately | SOURCED shared rules |
| BTC gate | BTC close_t < SMA200(close, through t); bars through t only. Gate day t is the "prior close" of entry day t+1 | SOURCED idea, use OURS |
| Coin downtrend | close_t < SMA50_t and SMA50_t < SMA50_{t-10} | OURS |
| Rally | close_t >= 1.12 x min(close_{t-10..t-1}) | OURS (BTC RELIEF +12% is SOURCED, MTS_BRAINS_SPEC line 26; alts are more volatile) |
| Rejection | high_t >= SMA20_t, close_t < open_t, close_t < low_{t-1} | OURS |
| Cooldown | per coin, a new signal needs t - t_prev >= 10 where t_prev is the last accepted signal (signals excluded by the 30-coin rule do not start it) | OURS |
| Entry | short at open_{t+1}; no look-ahead (signal bar t completed; all flags use bars through t) | SOURCED shared rules |
| Stop | stop price = max(highest high of bars t-4..t + 0.5 x ATR14_t, 1.05 x entry); stop % = stop/entry - 1 (>= 5%). ATR Wilder per FORMULAS.md (TR0 uses its own close as previous close, seed = mean of first 14 TR) | OURS (shared floor >= 1.5% satisfied) |
| Target | min(close_{t-10..t-1}) at the signal bar, frozen at entry (the "falls back to the rally start" claim). If the entry open is at or below it the signal is skipped and counted (TARGET-NOT-BELOW-ENTRY) | OURS |
| Exit | first of stop, target, or the close of the 10th daily bar (entry bar = bar 1). Stop wins ties inside a bar. After the entry bar a bar that opens at or above the stop fills at the open (STOP-GAP); the target fills at the target price (no gap bonus); the entry bar uses only its high and low | OURS |
| Ended coins | a coin whose last bar is more than 30 days before the data end is ENDED; a trade still open at its last bar closes there at the last close, flagged ENDED. A trade on a still-trading coin whose 10-bar window is not complete is skipped (counted) | SOURCED shared rules (ENDED), OURS (30 days) |
| Holes | no trade whose [signal day, exit day] span overlaps the LUNA hole (2022-05-13..05-31, coin LUNA) or the FTT hole (2022-11-15..2023-09-22, coin FTT) | SOURCED shared rules |
| Fee | 12 bp round trip = `2 x BINANCE_TAKER + SLIPPAGE_RT_S13` imported from `MyTradingSys/backtest/fees.py`; fee in R = 0.0012 / stop % | SOURCED fees.py |
| R units | gross R = ((entry - exit)/entry) / stop %; net R = gross R - fee R (PRICE-ONLY, the bar row); total R = net R + funding R | OURS (row definition) |
| Funding | real signed funding on the short: income = sum of cached `rate` prints with entry-open < print <= end of the exit day (UTC), prints rounded to the second; a short earns positive rates and pays negative ones; expressed on entry notional, divided by stop % for funding R. Funding cache: wave2 `funding` or miner `funding` (same coin name). Window not covered by the cache (first print after entry or last print before exit) = NOT_IN_DATA: no funding imputed, total R = net R for that trade, count reported | SOURCED shared rules, OURS (boundary rule) |
| Split | DEV = signal bar <= 2023-12-31; VAL = signal bar >= 2024-01-01 | SOURCED |
| Unit | ISO week of the ENTRY day, all coins pooled. Bootstrap: weeks that hold trades, in time order; moving blocks of 2 adjacent such weeks; ceil(k/2) blocks per resample; resampled mean = sum of values / number of trades in the drawn blocks; 2000 resamples, seed 1114, one-sided p = (resamples <= 0, plus 1)/(n+1). Second unit: rally episode (entry days of all coins chained, a gap of more than 14 days starts a new one), iid resample of episodes, same size and seed | spec: block 2 weeks; reading of "adjacent" is OURS |
| Placebo | per real trade, same coin, short side, a candidate signal day inside +/- 8 ISO weeks (56 days of entry) of the real entry, same split, BTC gate true and coin downtrend flag true and >= 30 alive coins, NOT conditioned on a rally or rejection, outcome simulated with the REAL trade's stop % and target % and the same 10-bar cap, price-only fee-net R. The real entry day is excluded. One draw = mean over the matched set; 1000 draws, seed 1114. Global variant: any flagged day of the coin in the same split. Real trades with no candidate are skipped and counted | spec |
| Baseline | short-and-hold of the equal-weight basket of coins with the downtrend flag, on the gated days: for each day d, mean over coins flagged at d-1 (gate, downtrend, alive, >= 30 alive coins) of -(close_d/close_{d-1} - 1); baseline = mean over the days of the split; no fee charged to the baseline (generous to it). Strategy side = sum of net % returns / sum of days held, over the split | spec (T5 style), details OURS |
| Rescue row | rally threshold 8% (spec's first stated rescue), same everything else, DESCRIPTIVE row only, never the verdict | spec |

## Data

Root `F:/MTS/data_cache` read only. 68-coin union as above. Counts only before the freeze (`counts.json`, pull day 2026-11-13): first day with >= 30 alive coins is 2020-01-10 (so every 2018 and 2019 signal day is excluded from verdicts by the shared rule; 13 raw signals were excluded this way, 2018 therefore contributes no trades to DEV).

## Splits

DEV signal bar <= 2023-12-31, VAL >= 2024-01-01. Measured counts, primary cell (rally 1.12), no outcome read:

| Count | DEV | VAL |
|---|---|---|
| raw signals before cooldown and the 30-coin rule (both splits) | 500 | 500 |
| excluded by the 30-coin rule | 13 | 13 |
| blocked by the 10-day cooldown | 128 | 128 |
| entries after screens (accepted, all feasible, none skipped) | 244 | 115 |
| distinct ISO entry weeks | 42 | 28 |
| rally episodes (14-day chaining) | 11 | 11 |
| coins with an entry | 66 | 54 |

(The raw, excluded and cooldown rows are totals over both splits, 500 / 13 / 128; the design's power count was 119 signals in 27 weeks at 12%, measured here 115 entries in 28 weeks.) Rescue row at 8%: DEV 416 entries in 52 weeks, VAL 230 entries in 33 weeks. BTC gate days: DEV 1094, VAL 402.

## Pass bars

Value = net R (price-only, fee-net). Cluster = ISO entry week, 2-week moving block (above).
1. VAL: n >= 30 trades and >= 20 distinct entry weeks, else UNDERPOWERED (never FAIL, never KILL); bars 2-8 are then reported but cannot give PASS and DEV is the main read.
2. VAL mean net R > 0 and the bootstrap 95% CI low > 0.
3. DEV mean net R > 0 (pooled over all DEV signal years that pass the 30-coin rule; n >= 10).
4. Placebo (same-window, price-only net R): real VAL mean above the 97.5th percentile of the 1000 draw means and excess over the draw mean > 0. Global variant reported next to it.
5. Ex-best-5 entry weeks mean net R > 0 (ex-best-2 when VAL weeks < 30; the ex-best-5 row is printed either way). With 28 expected weeks the ex-best-2 rule applies.
6. Baseline: strategy mean net % per day in position >= the baseline basket's mean daily short return over the VAL gated days.
7. Top-3 coin removal (sequentially, by summed VAL net R) keeps the mean > 0, else FRAGILE.
8. Leave-one-year-out (VAL entry years) every mean > 0, else FRAGILE.
9. Row by BTC cycle state (smoothed BEAR/BASE/BULL), by entry year, by brain label (MARKDOWN, RELIEF, ...) always printed for DEV, VAL and all. SIGN-FLIP = VAL mean > 0 while the BEAR-state mean <= 0 and the BULL-state mean > 0 (each >= 10 trades): not a PASS.
Also reported, not tests: sign in each of three bear periods (entries in 2018, in 2022, and from 2025-10-01 on: the BTC all-time high was in early October 2025, OURS); funding rows (price-only versus total, funding-covered subset, NOT_IN_DATA count); ex-ENDED and ex-LUNA/FTT rows; exit-reason mix; episode-unit bootstrap; Holm worst case over the 9-cell wave family = min(1, 9 x p).

## Kill criteria

KILL (verdict FAIL with KILL named) if bar 1 holds and any of: (a) VAL price-plus-funding net R <= 0 with >= 40 trades; (b) placebo: real VAL mean <= the 97.5th percentile of the same-window draws with >= 60 trades; (c) DEV mean net R < 0. Fewer than 20 VAL weeks is UNDERPOWERED, not KILL.

## Verdict vocabulary

PASS: bars 1-8 hold, no kill, no sign flip, not carry-only. FAIL: bar 1 holds and a kill fired or a bar of 2-6 fails (first failing bar named). UNDERPOWERED: bar 1 fails (never FAIL). FRAGILE: bars 1-6 hold, bar 7 or 8 fails. CARRY-ONLY: VAL price-only net R <= 0 while price-plus-funding > 0 (checked before the kills). SIGN-FLIP: bar 9. NOT-A-PASS is used for descriptive rows. Order applied in code: UNDERPOWERED, CARRY-ONLY, kills, SIGN-FLIP, first failing bar of 2-6, FRAGILE, PASS.

## Seen results

None. Only the inventory counts above (signals, entries, weeks, episodes, gate days) were read. No outcome of any T10-style trade was seen by this builder.

## Known weaknesses

- VAL holds one bear, so VAL is effectively one episode cluster (11 episodes); a DEV-bear or VAL sign flip is likely; weeks, not trades, are the sample.
- Delisted-coin collapses favour shorts (ENDED rows reported), survivor-only coin lists penalise them; the universe is a hindsight list, so the direction is stated, not removed.
- Funding history covers 2020-12 onward for most coins, so early DEV trades are NOT_IN_DATA and priced price-only.
- Spot stands in for a perp: no borrow, basis or liquidity model; target fills at the target price with no gap bonus (conservative), stop gaps fill at the open.
- Daily bars: intrabar order of stop and target is unknown, stop wins by rule.
- Every threshold (12%, SMA50/SMA20, 5-bar stop, 10 days) is OURS and untuned.

## Power gate

Command (run in the worktree, exit code 1):

    python scripts/dev/prereg_gate.py --n 28 --sd 1.0 --cost 0.017 --m 1 --sd-source "design floor 1.0 R (DEV week sd not computed before freeze: needs outcomes)"
    n 28 sd 1 m 1 z_holm 1.960 MDE 0.529 R + cost 0.017 = 0.546 vs max plausible gross 0.3; n needed 98
    BLOCK: do not freeze (write BLOCKED.md with these numbers)

n = 28 = VAL distinct entry weeks (independent unit), never trades (115). sd = the 1.0 R floor, because the DEV week-level sd needs DEV outcomes and the counting step reads none (recorded under Deviations). cost 0.017 R = top of the design's fee-in-R range 0.012-0.017. m = 1 as the design states. Decision: BLOCK reported, not hidden; the run goes ahead because the operator ordered the wave on 2026-11-14 (no BLOCKED.md for that reason). A FAIL or UNDERPOWERED result reads as UNTESTED at this power, never as proof of no edge.

## Protocol

1. This PRE_REG, `t10_core.py`, `t10_stats.py`, `t10_trades.py`, `test_t10_core.py`, `counts.json` and `mutation_check.txt` are committed before any outcome is computed. Tests are synthetic-bar only and never read the cache.
2. `python t10_trades.py trades` writes the trade list with no pooled statistic; `python t10_stats.py` computes the bars, RESULT.md and results.json. Parameters are never changed after the freeze; a found mechanical bug is logged in RESULT.
3. A later stage independently recomputes 3 dated trades from raw klines and FORMULAS.md, audits look-ahead and fees, and re-derives the verdict from these bars.
4. Weekly bars are not used in this study, so the Sunday-spike resample test is replaced by the ISO entry-week test (Sunday entry belongs to the week of the prior Monday).

## Deviations

1. DEV week-level sd was not computed before the freeze (it needs DEV outcomes, which the counting step may not read): the 1.0 R floor is fed to `prereg_gate.py`.
2. Shared rule "fewer than 30 alive coins excluded": the first date with 30 alive coins is 2020-01-10, so the 2018 bear (named in the spec for DEV bar 3) contributes no trades; the three-period report shows 2018 with n 0. DEV is 2020-2023 including the 2022 bear.
3. Rescue 2 in the spec (SMA100d gating for DISTRIBUTION days) is not implemented: the spec does not define the gating precisely and extra cells are not allowed. Rescue 1 (rally 8%) is a descriptive row.
4. `psutil` is not installed; BelowNormal priority is set through ctypes SetPriorityClass 0x4000 (class printed at run start).
5. The "2025-26" bear period is defined as entries from 2025-10-01 (OURS, stated above); the design gives no dates.
6. Primary metric is R (as the design's bars and fee-in-R), mean net R price-only; a per-trade % is also in the CSV (gross, fee, net columns).
