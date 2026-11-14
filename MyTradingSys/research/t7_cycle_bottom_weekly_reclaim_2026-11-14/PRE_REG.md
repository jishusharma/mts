# PRE_REG: T7 cycle-bottom long (coin deep drawdown + weekly SMA10 reclaim), 2026-11-14, frozen before any outcome

Design: `EDGE_WAVE3_DESIGN_1114.md` (side-session notes), section "T7 CYCLE-BOTTOM LONG" and SHARED RULES, frozen spec implemented as written. Frozen BEFORE any trade return, R, placebo or statistic is computed; only signal and unit counts (no outcomes) were produced, see Power gate. Research, not advice; nothing is an edge until a fee-net out-of-sample result passes. SOURCED = named file or paper; OURS = our choice.

## Context

Question: does a liquid coin at least 55% below its 2-year closing high that makes a fresh weekly close back above its own 10-week average (a reclaim) pay net of fees over the next 4 weeks? (Operator claim: deep drawdown from the cycle high plus a weekly reclaim.)
Regime: coin-level DD state (OURS gate): last completed weekly close <= 0.45 x the highest daily close of the prior 730 days (window = available history, at least 365 bars). The BTC smoothed cycle state (BULL/BASE/BEAR from `phase_daily.csv`, switching only after 10 consecutive days, OURS) is a stratum only, never a gate, because the BTC-only bottom count is too small to power.
Phase: no phase gate. Rows by BTC cycle state of the entry day (BEAR/BASE/BULL) and by year are always printed; BEAR-only and BASE-only are descriptive rows ("a weekly SMA10 cross inside a bear is a bear-rally trap"). A result positive only in BULL is labelled SIGN-FLIP.
Session: none. Weekly bars (Monday 00:00 to Sunday 23:59 UTC) and daily entries; 24/7 market, no session gate.
Entry: the Monday 1d open right after a completed week whose close is above its SMA10 of weekly closes, while the previous week's close was at or below the previous SMA10, and the coin is in DD state at that week.
Regime mix: filled in RESULT from the data (shares of DEV and VAL trades by BTC smoothed cycle state). Expected by construction: mostly BEAR and BASE entries; VAL (2024+) includes the 2024 bull, 2025 and the 2026 slide.

## Rules (one frozen cell, no grid, no second pass)

| Item | Rule | Label |
|---|---|---|
| Daily bars | Binance spot `<COIN>USDT` 1d UTC, root `F:/MTS/data_cache/binance`, folders `wave2-1114/spot_1d` (50) and `combo-edge-miner-1114/spot_1d` (20); union read at run time = 68 coins (BTC, ETH once): see Data | SOURCED (shared rules) |
| Segments | per coin, split at any missing day; history resets at a gap, so no trade and no indicator spans the LUNA (2022-05-13..31) or FTT (2022-11-15..2023-09-22) holes. A segment is ENDED when a gap follows it or its last bar is more than 30 days before the data pull (2026-11-14) | OURS |
| Alive | at least 365 daily bars of history inside the segment through the signal Sunday | SOURCED (design T7 override of 260) |
| Weekly bar | full ISO week Monday..Sunday; close = Sunday close; usable only from the following Monday | SOURCED (shared rules) |
| DD state | weekly close of week w <= 0.45 x max daily close over the 730 days ending on the Sunday of w (window = available history) | OURS (operator cycle-high idea; BIBLE s1) |
| Reclaim | weekly close(w) > SMA10 of weekly closes ending at w, and weekly close(w-1) <= SMA10 ending at w-1 | OURS |
| Signal / entry | at completed week w; entry = open of the next Monday daily bar; all flags use data through the Sunday | SOURCED (shared rules) |
| Cooldown | per coin one entry per 28 days (the clock moves only when an entry fires) | OURS |
| Stop | entry x (1 - max(3 x ATR14 / entry, 10%)), ATR14 Wilder (FORMULAS.md: TR0 uses its own close as previous close, seed = mean of first 14 TR) at the prior daily close, i.e. the Sunday; floor 10% far above the 1.5% minimum | ATR SOURCED (Wilder 1978); 3x and floor OURS |
| Stop fill | daily low <= stop checked from the entry day on; stop wins ties with the close; a bar that opens at or below the stop fills at its open | OURS |
| Exit | first of stop, or the close of day entry+27 (28 daily bars in market, time exit). Reading frozen: "close of day 28" = the 28th bar | OURS |
| Data end | window beyond the segment end: skipped if the segment has not ENDED, else exit at the last close, flagged ENDED | OURS |
| Fee | 12 bp round trip = 2 x BINANCE_TAKER + SLIPPAGE_RT_S13, imported from `MyTradingSys/backtest/fees.py` (no private cost constant) | SOURCED |
| Funding | real signed funding prints of the coin's cached funding file, window entry < print <= end of exit day, charged to the long (positive = pays), on entry notional; spot stands in for a perp (basis flagged). If the cache does not cover the whole window the trade carries funding 0 and rule NOT_IN_DATA (no imputation); the count is reported | SOURCED (cached funding); NOT_IN_DATA handling OURS |
| R | net return (gross - fee - funding) / stop distance fraction; gross R and fee R (0.0012 / stop) reported | OURS |
| Split | DEV = signal bar (Sunday) <= 2023-12-31, VAL = signal bar >= 2024-01-01 | SOURCED (shared rules) |
| Thin dates | signal Sundays with fewer than 30 alive coins are excluded from verdicts and counted separately | SOURCED (shared rules) |
| BTC cycle state | `cycle` column of `mts_brains/phase_daily.csv` at the entry day (row of day d is built from closes through d-1); smoothed: a new state counts only after 10 consecutive days | OURS (10 days) |
| Seed | 1114 | OURS |

Parameter labels (design table): DD depth/window 0.45 x 730d OURS; reclaim SMA10w OURS; BTC reclaim row first weekly close above SMA200d after 8 weeks below SOURCED idea (BIBLE s5), count 8 OURS; ATR Wilder 14 SOURCED; stop max(3 ATR14, 10%) OURS; hold and cooldown 28 d OURS; BTC smoothing 10 days OURS; fee 12 bp and signed funding SOURCED.

## Data

Cache `F:/MTS/data_cache/binance`. Universe = union of the file lists of `wave2-1114/spot_1d` and `combo-edge-miner-1114/spot_1d`, read at run time: 68 coins. Wave2 (50): 1INCH AAVE ALGO ANKR AXS BAND BAT BTC CELR CHZ COMP CRV DASH EGLD ENJ EOS ETH FIL FTM FTT GRT HBAR ICX IOST IOTA KAVA KNC LUNA MANA MATIC MKR NEAR OCEAN OMG ONE ONT QTUM RUNE RVN SAND SNX STORJ SUSHI THETA WAVES XMR XTZ YFI ZIL ZRX. Miner-only (18 more besides BTC, ETH): ADA ATOM AVAX BCH BNB DOGE DOT ETC LINK LTC NEO SOL TRX UNI VET XLM XRP ZEC. Funding from the same folder as the coin's spot file (`funding/<COIN>USDT.csv`, from 2020-01, so earlier trades are NOT_IN_DATA). Phase: `mts_brains/phase_daily.csv`. Delisted coins are kept. Every RESULT carries an ex-ENDED and an ex-LUNA/FTT row and states the survivorship direction: longs are biased UP (hindsight coin list; collapsed coins exit at a last close that may not have been tradable). Only LUNA and FTT have gaps in their files (an availability fact: day gaps between consecutive bars; no price outcome opened).

## Splits

DEV = signal bar <= 2023-12-31; VAL = signal bar >= 2024-01-01 (by signal bar, not entry bar; the entry of the last DEV week is 2024-01-01).

## Pass bars (wave-2 wording wins on discrepancy; metric = mean net R per trade after 12 bp + real funding)

Unit: ISO entry week over all coins, moving-block bootstrap with block 4 consecutive calendar weeks (weeks without a trade stay in the series), 2000 resamples, seed 1114; resampled mean = sum of R in the drawn weeks / number of trades in them. Second unit: episode (entries sorted by date, an entry chains to the current episode when its gap to the previous entry is < 28 days; trades averaged within the episode).
1. VAL: n >= 30 trades and >= 20 distinct entry weeks, else UNDERPOWERED (never FAIL, never KILL).
2. VAL mean net R > 0 and block-bootstrap 95% CI low > 0.
3. DEV mean net R > 0 (sign agreement).
4. Placebo (same-window): for every real VAL trade, candidates = Monday entries of the same coin segment and same split at completed weekly bars in DD state (flag only, no cross), not thin, entry week within +/- 8 ISO weeks of the real trade (the real week itself excluded, OURS), with the real trade's stop % and the same stop/28d exit; one draw = mean over matched trades; 1000 draws seed 1114; real mean must be above the 97.5th percentile and excess (real minus draw mean) > 0. Trades without candidates are skipped and counted. A global variant (any DD-flagged Monday of the coin and split) is reported, not a bar.
5. Ex-best-5 entry weeks mean > 0 (ex-best-2 when VAL entry weeks < 30). If VAL episodes >= 8, ex-best-2 episodes mean must also be > 0.
6. Baseline: mean net return per day in position of the real VAL trades >= that of an equal-weight basket of all coins in DD state entered on the same Mondays, held 28 days, no stop, same fee and funding (pooled per Monday, then averaged over Mondays).
7. Top-coin removal: dropping the coin with the largest summed VAL net R keeps the mean > 0, else FRAGILE; top-3 sequential removal is reported and a non-positive result there also gives FRAGILE (blocks PASS). (The shared text says top-3, the wave-2 text single coin; the stricter union is frozen.)
8. Leave-one-year-out (VAL years) stays > 0, else FRAGILE.
9. Rows by BTC cycle state and by year always printed; pooled VAL > 0 only in BULL (not in BEAR or BASE) is labelled SIGN-FLIP, not PASS.
Family: 9 cells (T7 is 1). Holm: per-study (one cell, equals the bootstrap one-sided p = (resampled means <= 0, plus 1) / 2001) and family p = min(1, 9 x p) both reported next to the verdict.

## Kill criteria

KILL if (a) VAL mean net R <= 0 with >= 20 entry weeks, or (b) the same-window placebo real mean is not above the 97.5th percentile with VAL n >= 100 trades (then the reclaim adds nothing over being oversold). Fewer units gives UNDERPOWERED, not KILL. The episode row requires >= 8 VAL episodes, else that reading is UNDERPOWERED with no kill.

## Verdict vocabulary

PASS = bars 1-8 hold, no FRAGILE, no SIGN-FLIP, no kill. FAIL = bar 1 holds and a bar among 2-6 or a kill fires (first failing bar named, KILL added). FRAGILE = only bar 7 or 8 (or top-3) fails. UNDERPOWERED = bar 1 fails (reads UNTESTED, never FAIL). Descriptive rows never give a verdict. A PASS is strong evidence only if placebo and basket both clear; any PASS stops the line pending the operator's go.
Descriptive rows (not pass cells): (a) BTC event row: first weekly close above SMA200d after >= 8 consecutive weekly closes below it, BTC smoothed state BEAR in >= 20 of the last 52 weeks, and the minimum over the last 52 weeks of weekly close / (max close of the prior 730 days) - 1 <= -0.45 ("cycle high" read as the 730-day closing high, OURS); basket of coins in DD state at that weekly bar, entered the next Monday open, exit at the open after the first BTC weekly close below the reclaim-week low, or after 26 weeks; no stop, 12 bp + funding; BTC alone from its own daily closes as sign check; (b) BEAR-only and BASE-only rows.

## Seen results

None. Only inventory counts (signal counts, entry weeks, episodes, alive counts, stop-distance quantiles) were looked at, see Power gate. The design note's expected counts (about 300 VAL trades, 74 weeks, 4-8 episodes) were replaced by the measured ones below.

## Known weaknesses (before the run)

- Every bottom is the same 4-6 market dates (2020-03, 2022-06/11, 2024-08, 2025-04), so weeks are not independent beyond blocks; the result is mostly beta rebound plus survivorship. Effective units are blocks and episodes, not trades.
- Survivorship: hindsight list, collapsed coins exit at a last close that may not be tradable (longs biased up).
- Spot stands in for a perp; funding is real only from 2020-01 and NOT_IN_DATA before it (the cost is understated there, no imputation); no fill model, no liquidity limit.
- Stop at 10% floor or 3 ATR is wide: R is small in % terms; fee is under 0.01 R.
- The 28-day exit reading ("close of day 28" = 28th bar), the placebo real-week exclusion, the strict bar 7 union and the episode chaining across coins are our readings.

## Deviations

Frozen before outcomes, forced by the counting step:
1. The design asks for `--sd` from the DEV week-level sd of the counting step (floor 1.0 R). The counting step computes no outcomes, so no sd exists; the floor 1.0 R is used. The measured DEV week-level sd is reported in RESULT afterwards, not used for any decision.
2. `--n` = number of non-overlapping 4-week blocks of the VAL calendar (from 2024-01-01) holding at least one non-thin entry, capped at 37 (reading of "VAL distinct entry weeks, blocks of 4 weeks capped at 37").
3. `--cost` = median fee in R from the stop-distance quantiles (0.0012 / median stop 17.8% = 0.0068 R), a price-structure quantity, not an outcome.
4. The BTC-alone sign check uses BTC daily closes from the wave2 spot_1d file and the smoothed `cycle` column of `phase_daily.csv`; `btc_cycle_features_1114.csv` is not used (the SMA200d is recomputed from the closes).
5. Nothing else deviates from the frozen spec.

## Power gate

Counting step (`t7_count.py`, no outcomes; `counts.json`): 68 coins, 70 segments (LUNA and FTT split at their holes), 1035 signals in total, 0 skipped for an incomplete window, 88 thin Sundays (< 30 alive coins). DEV (signal <= 2023-12-31): 554 trades non-thin (+45 thin excluded), 85 entry weeks. VAL: 436 trades, 67 entry weeks, 63 coins, 29 four-week blocks (n for the gate), 11 episodes. Median stop distance 17.8% (p10 12.8%, p90 25.9%), median fee 0.0068 R.

Command and output (run in the worktree, exit code 1):

    python scripts/dev/prereg_gate.py --n 29 --sd 1.0 --cost 0.0068 --m 1 --sd-source "design floor 1.0 R (DEV week sd not measured: needs outcomes)"
    n 29 sd 1 m 1 z_holm 1.960 MDE 0.520 R + cost 0.0068 = 0.527 vs max plausible gross 0.3; n needed 91
    BLOCK: do not freeze (write BLOCKED.md with these numbers)

With the family size m 9 the same inputs give MDE 0.671 R, n needed 152, BLOCK. Decision (OURS): BLOCK stated; the run goes ahead because the wave is ordered (the design expected BLOCK and said the run is still ordered). A FAIL or UNDERPOWERED reading is UNTESTED at this power, not proof of no edge.

## Protocol

1. This PRE_REG, the code (`t7_core.py`, `t7_stats.py`, `t7_trades.py`, `t7_count.py`) and the synthetic-bar tests (`test_t7_core.py`: look-ahead, entry at next open, stop wins ties, stop gap, fee arithmetic from fees.py, funding window, Sunday-spike weekly resample, cooldown, gap split, planted edge, no-edge about zero, mutation check in `mutation_check.txt`) are committed before any outcome is computed.
2. `t7_trades.py` writes the trade list; `t7_stats.py` computes bars, RESULT.md and results.json. No parameter is changed after seeing outcomes; no extra cells. A found mechanical bug is fixed and logged in RESULT, never a rule.
