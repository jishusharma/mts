# PRE_REG: T5 bear-phase 4h bearish-divergence short on FRESH coins, frozen before any outcome (2026-11-14)

Source cell: `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/` (`PRE_REG.md`, `bear4h.py`, `REPORT.md`, on origin/fast-track). Design: `EDGE_WAVE2_DESIGN_1114.md` (notes folder), pick T5. Nothing here is an edge until a fee-net out-of-sample result passes. Frozen BEFORE any signal, trade, return or placebo number is computed; only data availability (file listing) was looked at. The source result on its 22 coins (BEAR DEV +0.107 R n 287, VAL +0.090 n 211, RECENT +0.238 n 127, pooled +0.100 CI [-0.01, 0.21], placebo pct 99.2) is SEEN and is not tuned against: this study changes the coins, not one rule. Every parameter is SOURCED (copied unchanged from the named source file) or OURS (stated).

## Context

Regime: the ex-ante post-peak-bear flag BEAR (daily, read at day D-1, rule table below) is the only regime gate. Shorts are claimed only when BEAR is true. BEAR is a per-coin flag on each coin's own daily bars (not the BTC cycle label).
Phase: the claim flag is the per-coin BEAR flag. Descriptive only: BTC's MTS brain phase from `F:/MTS/data_cache/mts_brains/phase_daily.csv`. Today (2026-11-14, row provisional) BTC is label MARKDOWN, cycle BEAR (2026-11-13 the same; 2026-11-12 was DISTRIBUTION / BASE). Calendar-day shares 2019-2026 in that file: cycle BEAR 39.6%, BASE 32.5%, BULL 27.9%. The brain label is reported as a descriptive cut of trades (BTC label on the signal day), never a gate. Control rows (BEAR false) are split by the per-coin Test 1 phase label (UP, BASE, RANGE, DOWN, POSTPEAK_BEAR), definitions in `buyzone_test1_ladder_2026-11-14/PRE_REG.md`.
Session: not applicable; 4h bars run 24/7 (UTC), no session gate is tested.
Entry: short at the next 4h open after the confirming close of the second swing high (SOURCED, source PRE_REG Entry line).
Regime mix: RESULT.md reports, per split (DEV, VAL, RECENT) and pooled over the fresh coins, the share of coin-days with BEAR true and the share of each Test 1 phase (UP, BASE, RANGE, DOWN, POSTPEAK_BEAR), the BTC brain cycle (BULL / BASE / BEAR) share of the trades' signal days, and the share of claim trades by calendar year. A split whose claim trades are more than 85% from one calendar year is flagged ONE-YEAR and cannot carry a PASS alone. Expected from the source report (22 coins): BEAR about 42% of coin-days in DEV and 47% in VAL; the fresh coins were listed later on average, so their BEAR share may differ.

## Question and design

Does the source cell's sign and size replicate on 45 coins it never saw? The source failed only on CI width in VAL (CI [-0.07, 0.27]) and on VAL placebo percentile 89.3 (pooled 99.2). The lever here is sample size and coin independence. The fresh coins are out of sample BY COIN, not by calendar time (same weeks as the old coins), which is why the time split stays and why the bootstrap clusters on calendar week across all coins.

## Source cell, exact rules (one cell, nothing to tune)

| Item | Rule | Label |
|---|---|---|
| Bars | Binance spot USDT 4h klines, UTC; the last (possibly partial) bar of each series dropped. First 100 4h bars of each coin give no event and no placebo draw | SOURCED (source PRE_REG Data) |
| Swing high | 4h bar i with High[i] > High[i-3..i-1] and High[i] > High[i+1..i+3] (k = 3, strict). Known only at the close of bar i+3 | SOURCED (bear4h.py K = 3, swing_highs) |
| RSI | RSI14 Wilder on 4h closes, per `MyTradingSys/backtest/layers/FORMULAS.md` | SOURCED (source PRE_REG); formula FORMULAS.md |
| Upper band | SMA20(Close) + 2 x population sd20(Close) (ddof 0), closed bars through the second high j | SOURCED (source PRE_REG; bear4h.py bollinger_upper) |
| Bearish divergence | consecutive swing highs p < j with 6 <= j-p <= 60 bars, High[j] > High[p], RSI14[j] < RSI14[p], and High[j] > upper band[j]. "Consecutive" = adjacent in the full swing-high list of the coin, regardless of the other filters. Signal bar c = j+3, one signal per pivot j | SOURCED (source PRE_REG Signal; bear4h.py find_signals) |
| Entry | Open[e], e = c+1 | SOURCED |
| BEAR flag | for 4h entry bar e on UTC day D, daily bar D-1 of the same coin: Close < SMA350(Close) AND NOT base reclaim, base reclaim = (a) Test 1 BASE (not UP, DD >= 0.40 where DD = 1 - Close / max High over the last 365 bars, and min Low[t-59..t] >= min Low[t-179..t-60]) OR (b) Test 1 UP (Close > SMA200 and SMA200[t] > SMA200[t-30]). No flag (treated as false and no event) when SMA350 or the 180-bar low windows are undefined, i.e. fewer than 350 daily bars | SOURCED (source PRE_REG "Phase flag BEAR"; equals bear4h.py daily_flags, label not in "", UP, BASE) |
| Stop0 | High[j] + max(0.6 x ATR14[c], 0.005 x High[j]), ATR14 Wilder on 4h closed bars at c. r = (stop0 - entry)/entry. An event with entry >= stop0 is dropped and counted | SOURCED (source PRE_REG Stop) |
| Exit | first of (a) trailing stop, level at bar t (t > e) = min(stop0, min Low[e..t-1] + 2 x ATR14[t-1]); if High[t] >= level exit at max(Open[t], level); on the entry bar only stop0 is checked (exit at max(Open[e], stop0)); (b) Close[e+41] (42 bars, 7 days), taken only if the stop was not reached in that bar (stop is checked first, so the stop wins any tie). If neither occurs before the data end the event is dropped | SOURCED (source PRE_REG Exit; bear4h.py sim_exit) |
| Lockout | an event is dropped if its entry bar is within 60 bars of the previous KEPT entry bar of the same coin, or on or before that trade's exit bar | SOURCED (source PRE_REG Lockout, 10 days) |
| Return | gross = (entry - exit)/entry (short). R = (gross - fee + funding)/r | SOURCED |
| Seed | 1114 everywhere | SOURCED (design note) |

This study re-implements the cell in its own `t5_*.py` module; it does not import the buyzone module. Behaviour must match the table above; a synthetic test per row (look-ahead by truncation, stop wins ties, fee arithmetic from `fees.py`, planted edge) is committed.

## Data and fresh universe (frozen now)

Price: Binance spot 4h and 1d klines fetched into `F:/MTS/data_cache/binance/wave2-1114/{spot_4h,spot_1d,funding}` (outside the repo, never committed; when this file was written the 4h and 1d folders were still being filled by the shared fetch, so availability is verified at the code stage and reported, not assumed). Funding: Binance futures funding prints from the same cache. DEVIATION from the source, stated: the source used Bybit funding as a proxy; here Binance funding is used, and both rows (with and without funding) are reported and both are required for a PASS.

Candidate list (frozen, 48 tickers as supplied, all `*USDT`): NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN. (The design note said 49; the list actually supplied has 48.)

Fresh universe = candidate list minus NEAR, FIL, ALGO (they are in the source 22) = 45 tickers: MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN. BTC, ETH and the other source coins are excluded (not fresh).

Drop rule (OURS, the only one): a coin is kept iff it has 4h data and at least 350 daily bars; every drop is listed with its reason in RESULT. No coin is dropped or added for performance or after any outcome. A coin whose funding history is shorter than its price history gets funding 0 before its first print on the with-funding row; such trades are counted and listed ("no funding coverage"), none is dropped. A coin with no funding file gets funding 0 throughout and is listed; the no-funding row is unaffected.

Survivorship note: the list was chosen knowing which coins exist or existed with 4h history, so it is survivorship-biased in an unknown direction. Delisted or collapsed coins that the Binance archive still holds (LUNA, FTT, OMG, WAVES and similar) are kept. LUNAUSDT and possibly other symbols were reused or re-denominated by the exchange (LUNA after May 2022); the series is used as published and flagged in RESULT, and the per-coin and top-coin-removal rows show its effect. For a short, collapse tails help the signal; the sign of the net bias is not assumed.

## Splits (OURS, as in the source)

DEV: signal bar close time <= 2023-12-31 23:59 UTC; VAL: signal bar on or after 2024-01-01 00:00 UTC (by signal bar, as the design note states; the source split by entry date, a difference of at most one bar). RECENT: signal bar on or after 2025-07-01, a subset of VAL, descriptive only, never used to pick anything.

## Costs

Fee round trip = 2 x BINANCE_TAKER + SLIPPAGE_RT_S13, both imported from `MyTradingSys/backtest/fees.py` (= 12 bp); never typed as a literal. The 6 bp row is descriptive (half of the main row, computed by arithmetic on the imported constant). Funding: a Binance print is assigned to the 4h bar that contains its timestamp; a short held from entry bar e to exit bar x receives the sum of rates in bars e+1..x (a print at the entry bar is not counted, one in the exit bar is); a positive rate is income to the short. Funding return = that sum, notional approximated as entry notional (OURS, as in the source). R with funding = (gross - fee + funding)/r; without = (gross - fee)/r. Both are reported at every stage.

## Bars to pass and kill criteria (statistics defined exactly)

Unit and primary sample: fresh universe, BEAR true, trades after lockout. Statistic = mean R per trade (pooled over coins). Cluster unit = ISO entry week (ISO year + week of the entry bar's UTC date); all coins in a week form one cluster. Bootstrap: 2000 resamples of clusters with replacement, seed 1114, statistic = mean R of the pooled trades of the resampled clusters, percentile 95% CI; one-sided p = (1 + number of resample means <= 0)/(2000 + 1). Computed separately on the with-funding and without-funding rows.

Placebo draw (OURS, as the source, with the design's 1000 draws): for every real trade in a cell (split), pick a uniformly random eligible 4h bar of the SAME coin, SAME split, with the BEAR flag (read at D-1) true, past the 100-bar warm-up, whose trade closes inside the data; enter short at that bar's open with the real trade's own stop distance r (stop0 = entry x (1 + r)), the same exit rule (2 x ATR trail, max 42 bars, stop wins), the same fee, and on the with-funding row that draw's own funding over its own hold. One draw = one such matched set over all real trades of the cell; its statistic = mean R over the set. 1000 draws, seed 1114, no lockout on draws (stated). Placebo percentile = share of draw means below the real mean (ties counted half); "beats placebo" = real mean above the 97.5th percentile of the draw means. Computed per split (DEV, VAL, DEV+VAL pooled) and per row.

The seven pass bars (design note, made exact; all must hold on BOTH the with-funding and the without-funding 12 bp row, evaluated on the fresh VAL cell unless stated):
1. Power: VAL n >= 30 trades and >= 20 distinct ISO entry weeks, else UNDERPOWERED.
2. VAL mean R > 0 and week-cluster bootstrap CI low > 0.
3. DEV mean R > 0 (sign agreement).
4. Excess over random entries: VAL real mean above the 97.5th percentile of the 1000 placebo draw means.
5. Ex-best-5 entry weeks: remove the 5 ISO entry weeks (VAL) with the largest summed R; the mean R of the remaining VAL trades > 0.
6. Buy-and-hold baseline (short-and-hold of the basket over BEAR days): signal rate = (sum over VAL trades of (gross - fee + funding), funding omitted on the no-funding row) / (sum over VAL trades of days held, held bars x 4/24). Baseline rate = mean over UTC days in VAL of the equal-weight average, across the fresh coins that have BEAR true on that day (flag read at D-1, the same day mapping as entries) and a close on both days, of the daily short return -(Close[d]/Close[d-1] - 1) plus (with-funding row only) that coin's funding prints inside UTC day d; no fee and no rebalance cost (favours the baseline, stated). Pass if signal rate >= baseline rate. The same two numbers are reported for DEV.
7. Top-coin removal: remove the coin with the largest summed VAL R; the VAL mean of the rest > 0, else FRAGILE (reported, blocks PASS).

Holm: the raw one-sided VAL bootstrap p from bar 2 (the larger of the two rows) is reported next to the verdict. The Holm adjustment over the wave family m = 3 (the T4, T5, T6 VAL p-values) is computed by the coordinator when all three are in; a PASS whose Holm-adjusted p > 0.05 is labelled MULTIPLICITY-FLAGGED. Other label: ONE-YEAR (see Context).

Kill (design note; "either row" is the conservative reading because PASS needs both): KILL if the fresh pooled (DEV+VAL) mean R is <= 0 on EITHER row, OR the fresh VAL placebo percentile is < 90 with VAL n >= 200 on EITHER row. Then the +0.10 R was the old-coin sample.

Verdict vocabulary and order (first that applies):
1. UNDERPOWERED: bar 1 fails (stated with n and weeks; not a KILL, not a claim).
2. KILL: as above.
3. PASS: bars 1-7 all hold on both rows (plus FRAGILE / MULTIPLICITY-FLAGGED / ONE-YEAR labels where they apply; FRAGILE blocks PASS). A PASS stops this line; a blind review and a testnet-forward card need the operator's go.
4. REPLICATED-WEAK: not UNDERPOWERED, not KILL, not PASS, fresh pooled mean > 0 and DEV mean > 0 and VAL mean > 0 on both rows (the VAL CI low <= 0, i.e. the CI spans 0 again, or one of bars 4-7 fails). Next step is size (all listed perps), not a new rule.
5. FAIL: anything else, stated with the failing bars.

Descriptive rows (cannot change the verdict): 6 bp rows; RECENT; per coin (n < 30 marked underpowered); the control signal with BEAR false by Test 1 phase (expected no edge); by calendar year; by BTC brain label; old 22 + fresh pooled as an n-weighted row built from the SOURCE summary numbers (DEV n 287 +0.107 / +0.111 without / with funding, VAL n 211 +0.090 / +0.092, pooled n 498 +0.100 / +0.103), clearly labelled "not re-run"; per-trade sd of R; time in market; number dropped for entry >= stop; number without funding coverage.

## Known weaknesses (stated before the run)

- Gross is only about +0.15 R in the source, below the +0.30 R line the postmortem used; the cell can pass only by sample size.
- Same calendar weeks as the old coins: coins fall together in a bear market, so weeks, not trades, are the sample; the week-cluster bootstrap handles that and widens the CI relative to a trade bootstrap.
- Funding source differs from the source study (Binance, not Bybit); the entry-notional approximation and the entry-bar funding convention are inherited.
- The source VAL placebo percentile was 89.3, below the 97.5 bar and below the kill line's 90; a kill on that line is plausible and would be a faithful result.
- Fresh coins skew small-cap, thinner and more volatile, with possible survivorship bias, symbol re-use (LUNA) and delistings; 12 bp may understate small-coin slippage.
- BEAR needs 350 daily bars, so coins listed after about 2021 contribute little to DEV. The 4h series of some coins may start after their daily series.
- Forty-five coins may give few BEAR-flagged signals each; per-coin results are descriptive only.
- All parameters are OURS, inherited from a seen cell; none is the trader's.

## Power gate

Command run in the worktree: `python scripts/dev/prereg_gate.py --n 150 --sd 1.26 --cost 0.045 --m 3 --sd-source "derived from source test3 VAL CI"`. Inputs and where each comes from:
- n 150: expected fresh VAL trades (OURS guess, not measured). The source gave VAL n 211 on 22 coins; the 45 fresh coins are on average listed later and thinner, with lockout and the BEAR gate unchanged, so about 150 is assumed.
- sd 1.26: derived from the source VAL week-block CI [-0.07, 0.27] at n 211: 0.17 / 1.96 x sqrt(211) = 1.26 (it includes clustering inflation, so it is conservative). Source: `buyzone_test3_bear4h_2026-11-14/REPORT.md`, pooled table.
- cost 0.045 R: middle of the design note's 0.03 to 0.06 R fee in R units for stops of 2 to 5%.
- m 3: the wave family T4-T6.

Output pasted:

```
n 150 sd 1.26 m 3 z_holm 2.394 MDE 0.333 R + cost 0.045 = 0.378 vs max plausible gross 0.3; n needed 255
BLOCK: do not freeze (write BLOCKED.md with these numbers)
```

BLOCK stated. The run proceeds because the operator ordered the wave (2026-11-14); no BLOCKED.md is written for that reason. Reading: against the seen effect of about +0.10 R, the Holm-level test needs about 255 trades at this sd and the expected 150 falls short, so a FAIL or REPLICATED-WEAK is to be read as under-powered, never as proof of no edge. The realised n and sd are reported in RESULT. A PASS would still need the blind review.

## Protocol

1. Code (`t5_*.py` modules with the unique prefix) and synthetic-bar tests (`test_t5_*.py`: no data-cache reads, no scheduler imports, seconds to run) are committed first.
2. Step A: the trade-list script writes the trade list (per trade: coin, signal bar, entry bar, exit bar, entry, exit, r, gross, funding, flags) with no pooled statistics.
3. Step B: an independent recompute of 3 dated trades from raw klines and FORMULAS.md, plus an adversarial look-ahead / fee audit, both on the step A list.
4. Step C: only if step B is clean, the statistics script computes bars 1-7, the verdict, the baseline, controls and descriptive rows; RESULT.md (with its own `## Context` and `Regime mix:` lines) and the notes file are written.
5. Mechanical bugs are fixed and logged in RESULT with the number before and after. Rules, thresholds, universe and splits are never changed after step A.

## Ambiguities in the source text and the reading frozen here

- BEAR flag: the source PRE_REG text and `bear4h.py` agree (Close < SMA350 and not UP/BASE; the label hierarchy makes "label not UP and not BASE" the negation of base reclaim). Frozen as the text says; undefined history = false.
- Split key: source used entry date; the design note says signal bar; frozen as signal bar.
- Bootstrap: source used 7-day blocks and 10000 resamples; design says ISO entry week and 2000 resamples; frozen as the design.
- Placebo count: source 2000 draws; design 1000; frozen as the design (a draw = the whole matched set).
- Which funding row carries the verdict: both, as the source and the brief.
- Bars 5, 6 and 7 name no split in the design note; frozen on fresh VAL (the primary cell), with DEV and pooled reported.
