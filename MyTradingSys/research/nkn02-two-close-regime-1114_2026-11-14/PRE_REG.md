# PRE_REG nkn02-two-close-regime-1114 (committed with the study code, before any trade outcome is computed)

Rule NKN-02 "Two-close regime switch and 200-average hold" (videos a8RP5ftOfGo, lmhqooBqJWU, PLJda-dtBIc, IjU9PpqvrI8) from `research/nk_stocktalk_1113/extract55/NK55_RULES_1114.md`. Operator order 2026-11-14 06:12Z: NK rules are not tested blindly; context is applied (phases / context / crypto context / layers / levels). The design below is the frozen `NKN-02.md` context design (side-session notes, local_62e478d7), copied here; this PRE_REG implements it and changes nothing in it. Labels: SOURCED = video id + time, OURS = our choice with one value and no grid. No OURS parameter is NK's.

## Context
- Regime: BTC cycle state shared by all coins (BEAR = drawdown <= -20% and close < SMA200; BULL = close > W200 and drawdown > -20%; else BASE), read from `F:\MTS\data_cache\mts_brains\phase_daily.csv` column `cycle` at the close of the day BEFORE the first confirming close. Long cell needs cycle not BULL (BEAR or BASE); short cell needs cycle BULL. The -20% and W200 thresholds are the MTS BRAINS spec (OURS).
- Phase: per coin, at that same prior close: UP / DOWN / RANGE = 20-day SMA slope over 5 days plus ADX14 >= 20 with DI direction (else RANGE). Long cell L-TURN needs DOWN or RANGE; short cell S-TURN needs UP or RANGE. PRIMARY cells are regime TURNS (counter-trend entry into the new trend); the draft's continuation reading (2 closes above SMA20 and SMA200 inside an established uptrend) is a control.
- Session: UTC daily bar. Signal at the 00:00 UTC close, entry at the next 00:00 UTC open (OURS). One session only; no NY-close variant.
- Entry: next daily open after the second confirming close (long: 2 closes above SMA20 and SMA50 with the second above SMA200 after a drop under the 200; short: 2 closes under SMA20 with all 10 closes under SMA200), one open trade per coin.

## Hypothesis
Regime flips confirmed by 2 closes (SOURCED) beat 1-close flips as a filter: fewer whipsaws and positive fee-net R. Pre-registered where the edge, if any, sits: AT the SMA200 level (descriptive split only). Crypto transfer of an Indian-equity swing behaviour is unproven; the expected outcome is FAIL or UNDERPOWERED and this design makes that decidable. It does not rescue the rule.

## Frozen design (copied from NKN-02.md)
- Phase tested: ONE primary cell per side = a regime TURN. L-TURN: cycle at the day before the first confirming close not BULL AND coin phase DOWN or RANGE at that prior close. S-TURN: cycle BULL AND coin phase UP or RANGE at that prior close. Long and short are separate rows, never pooled. De-overlap: one open trade per coin. Cluster by day.
- Episode gate (OURS): >= 15 independent turn episodes on DEV (entry days from any coin, entries within 10 days of each other chain into one episode), else the cell is UNDERPOWERED. Episode counts are reported for DEV and VAL.
- Claim test: in L-TURN and S-TURN, is the day-cluster CI low of the 2-close V0 above that of the 1-close V0? Gates apply to the 2-close rows only.
- Context conditions:
  1. S: two consecutive daily closes under SMA20 = bear flip (a8RP5ftOfGo 00:08:50; IjU9PpqvrI8 00:14:58). Short trigger.
  2. S: an SMA200 break counts only if it holds 10-12 days (a8RP5ftOfGo 00:09:40). Use 10, strict reading: ALL 10 closes (t-9..t) under the SMA200 at their own bar. No run at 12.
  3. S: long re-entry after a drop under the 200 needs 2 daily closes above SMA200 and SMA50 (PLJda-dtBIc 00:13:25). Long trigger: close[t-1] and close[t] both above SMA20 and SMA50, and close[t] above SMA200. The SMA20 leg is OURS (mirror of the sourced short trigger). SMA = simple (FzNDQm7wC_s 00:02:39).
  4. O: "after a drop" arming = close under SMA200 on at least 10 of the 30 days ending the day before the first confirming close (day t-2).
  5. O: phase and cycle gates read at the prior close (look-ahead free).
  6. S: stop = two closes back against the position (lmhqooBqJWU 00:07:26): long exits after 2 consecutive daily closes under SMA20, short after 2 closes over SMA20; exit at the next daily open. O: 60-day time stop.
  7. O: R = max(structural, 0.5% of entry price, 0.6 x ATR14 daily). Structural = long: entry minus the lowest low of the 10 daily bars ending at the signal day; short: highest high of those bars minus entry. PRIMARY P&L is the close-based exit path (no intraday stop). A second non-gating column shows P&L with an intraday hard stop at 1R. Per cell, the share of trades where the floor beat the structural distance is reported.
  8. NOT_STATED by NK, not invented: index filter for this rule, time of day, VWAP, gap, volume.
  9. Weekly-close alternative (PLJda-dtBIc 00:14:26): control row only.
- Crypto translation: UTC daily bar, signal at the 00:00 UTC close, entry at the next 00:00 UTC open. NKN-02 has no gap element. Weekly expiry, option chain, Nifty legs: dropped. Funding (8h, `binance_futures/nkp1/<COIN>USDT_funding.csv`): crowding veto as a CONTROL filter only: skip long if the mean funding of the 3 prior completed UTC days (t-2..t) exceeds its trailing 90-day 90th percentile (the 90 daily values before t); short mirror at the 10th percentile (OURS, one value). OI (`<COIN>USDT_oi_daily.csv`): descriptive column only (5-day OI change before entry). BTC filter: control row for alt longs only (BTC close > BTC SMA200 at the signal close). Shorts: no BTC filter. CBP lean and the Bible cycle clock are labels only, not used. Does not translate: NSE 15:30 close, gap, expiry, index/option legs. NK's 10-12 day hold was tuned to a stock tape (weak port).
- Layer agreement (daily bars; reads up to the signal close): V0 rule alone. V1 = V0 + ADX14 >= 20 and DI sign agrees (long +DI > -DI; short -DI > +DI; OURS; `backtest/layers/adx/adx.py adx_di`). V2 = V1 + daily RSI14 Malkan regime (`rsi_core` then `malkan_regime(rsi, 40, 60, 20)`; long needs BULL, short needs BEAR; 40/60 SOURCED (Malkan), 20-bar lookback is the function default, OURS). Dropped: WaveTrend, funding as a layer, order-flow, pitchfork, volume profile.
- Level type: ONE level = daily SMA200 (SOURCED: FzNDQm7wC_s 00:02:39, PLJda-dtBIc 00:13:25). D = |close_signal - SMA200_signal| / ATR14_signal (Wilder). AT-LEVEL: D <= 1.5 (OURS); AWAY: D > 1.5. The split runs on the V0 2-close rows only and is descriptive (control rows). Also reported per cell: median SMA20-SMA200 gap in ATR, and days since the close crossed the SMA200.
- Timeframes: native DAILY is the rule (all primary rows). 15m and 4h are NOT expressible (the rule is defined on daily closes and daily SMA20/SMA200): no cells at those timeframes. 1h: only NK's own separate 1h SMA200 switch (a8RP5ftOfGo 00:13:14) as one control row (long when the 1h close crosses above SMA200(1h), exit at the next 1h open after a 1h close back under; 1440-bar time stop; same R definition on 1h ATR14 and 10 1h bars). Weekly: one control row (PLJda-dtBIc 00:14:26): at each Saturday daily close (= Sunday 00:00 UTC weekly close) with close above daily SMA50 and SMA200 and the previous weekly close not, long at the next open; exit as the daily rule.

## Cell table (28 cells tried, 6 primary)
All daily and 2-close unless stated. PRIMARY = verdict plus the BH family of 6. CONTROL = descriptive, never pooled, not in BH.

| # | Cell | Variant | Level | TF | Side | Trigger | Role |
|---|---|---|---|---|---|---|---|
| 1 | L-TURN | V0 | all | 1d | long | 2-close | PRIMARY |
| 2 | L-TURN | V1 | all | 1d | long | 2-close | PRIMARY |
| 3 | L-TURN | V2 | all | 1d | long | 2-close | PRIMARY |
| 4 | S-TURN | V0 | all | 1d | short | 2-close | PRIMARY |
| 5 | S-TURN | V1 | all | 1d | short | 2-close | PRIMARY |
| 6 | S-TURN | V2 | all | 1d | short | 2-close | PRIMARY |
| 7 | L-TURN | V0 | all | 1d | long | 1-close | CONTROL (key, trap claim) |
| 8 | S-TURN | V0 | all | 1d | short | 1-close | CONTROL (key, trap claim) |
| 9 | continuation UP x BULL (draft original, no drop-arming) | V0 | all | 1d | long | 2-close | CONTROL |
| 10 | continuation DOWN x BEAR (draft original short) | V0 | all | 1d | short | 2-close | CONTROL |
| 11 | L-TURN cell, mismatched direction | V0 | all | 1d | short | 2-close | CONTROL |
| 12 | S-TURN cell, mismatched direction | V0 | all | 1d | long | 2-close | CONTROL |
| 13 | random same-cell placebo (matched cycle + phase) | n/a | all | 1d | long | none | CONTROL |
| 14 | random same-cell placebo | n/a | all | 1d | short | none | CONTROL |
| 15 | MARKDOWN (BRAINS spec), descriptive | V0 | all | 1d | short | 2-close | CONTROL |
| 16 | L-TURN | V0 | AT | 1d | long | 2-close | CONTROL |
| 17 | L-TURN | V0 | AWAY | 1d | long | 2-close | CONTROL |
| 18 | S-TURN | V0 | AT | 1d | short | 2-close | CONTROL |
| 19 | S-TURN | V0 | AWAY | 1d | short | 2-close | CONTROL |
| 20 | L-TURN + funding veto | V0 | all | 1d | long | 2-close | CONTROL |
| 21 | L-TURN + funding veto | V0 | all | 1d | long | 1-close | CONTROL |
| 22 | S-TURN + funding veto | V0 | all | 1d | short | 2-close | CONTROL |
| 23 | S-TURN + funding veto | V0 | all | 1d | short | 1-close | CONTROL |
| 24 | L-TURN alts + BTC>SMA200 | V0 | all | 1d | long | 2-close | CONTROL |
| 25 | unconditioned draft (no phase/cycle) | V0 | all | 1d | long | 2-close | CONTROL |
| 26 | unconditioned draft (no phase/cycle) | V0 | all | 1d | short | 2-close | CONTROL |
| 27 | 1h SMA200 switch | V0 | all | 1h | long | 1h close > SMA200 | CONTROL |
| 28 | weekly-close re-entry (>SMA200 and >SMA50) | V0 | all | 1w | long | 1 weekly close | CONTROL |

**total cells tried: 28 ; primary cells: 6**

## Exact trigger definitions (implementation of the frozen design; the readings below are fixed here, before any outcome)
- A_long[d] = close[d] > SMA20[d] and close[d] > SMA50[d]; B_short[d] = close[d] < SMA20[d].
- "First confirming close" f: the first close of the pair. 2-close long signal day t = f+1: A_long[t] and A_long[t-1] and NOT A_long[t-2] (a fresh flip; the day before f is t-2) and close[t] > SMA200[t] and armed(E = t-2). 2-close short: B[t] and B[t-1] and NOT B[t-2] and all of close[t-9..t] < SMA200 at their bars. Phase and cycle are read at t-2.
- 1-close control: f = t. Long: A_long[t] and NOT A_long[t-1] and close[t] > SMA200[t] and armed(E = t-1); short: B[t] and NOT B[t-1] and the 10-close hold. Phase and cycle read at t-1.
- Draft (cells 9, 10, 25, 26): 2 closes above SMA20 and close above SMA200 (long), 2 closes under SMA20 with the 10-close hold (short); no freshness requirement, no arming. Cell 9 reads cycle BULL and coin UP at t-2; cell 10 reads cycle BEAR and coin DOWN at t-2.
- Cells 11 / 12: the V0 short / long 2-close trigger evaluated in the other turn cell's phase/cycle condition. Cell 15: V0 short trigger with the BTC BRAINS label MARKDOWN at t-2. Cell 24: cell 1 for non-BTC coins with BTC close > SMA200(BTC) at t.
- Exit pair: the two closes against the position must both be at or after the entry bar (an exit signal at day j needs j >= e+1); exit at the open of j+1; 60-day time stop at the open of e+60; a trade unresolved at the end of data exits at the last close and is counted (reported as `unresolved`).
- Entry = open of the day after the signal day. Data: daily bars aggregated from the cached spot 15m of each coin; the final partial day is dropped; a day with exchange-downtime gaps stays as a shorter day.
- Placebo (like-for-like, per primary cell): for each real VAL trade, a random entry day of the SAME coin from the pool of VAL signal days where the cell's phase/cycle condition (read at t-2) holds, same side, same exit logic and fee, no de-overlap in the pool, matched count, 1000 draws, p = (1 + #(placebo mean >= real mean)) / 1001. The pool is the cell's phase/cycle pool, so V0, V1 and V2 of a side share it (the placebo asks whether the trigger and layers beat random entries in the same phase/cycle cell). Cells 13/14 report the placebo mean and the matched count of cells 1/4.

## Universe, splits, fees
- Universe fixed before any run: the 20 cached spot coins BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO (all with history on both sides of 2024-01-01). Fresh 10-coin holdout: NOT run (see Design items not implemented).
- DEV = signal bar open before 2024-01-01 UTC; VALIDATION = on/after. Split by SIGNAL bar, never entry or exit bar.
- Fees: 12 bp taker round trip (primary verdict) = 6 bp of entry notional plus 6 bp of exit notional; 6 bp maker round trip (secondary) = 3 bp each leg on the same trades (a fee sensitivity row, no fill model). Fee in R = (bp/2e4) x (entry + exit) / R_distance. Gross R = side x (exit - entry) / R_distance. Net R = gross - fee. Spot-equivalent, no funding charge. Fills: next-bar open for entries; exits at the next open (close-based rule) or, in the non-gating 1R-stop column, a gap through the stop fills at the bar open, a touch at the stop. There is no target in this rule, so no stop-vs-target same-bar case exists.

## Gates (VALIDATION primary cells; all needed for PASS)
Net R at 12 bp > 0; trade-level bootstrap CI low > 0 (5000 draws, percentile 2.5); day-cluster bootstrap CI low > 0 (5000 draws, cluster = signal day); ex-best-5 mean > 0 (mean R after removing the 5 days with the highest summed R); placebo p < 0.05; Benjamini-Hochberg q <= 0.10 across ALL 6 primary cells with the one-sided day-cluster bootstrap p (mean <= 0); n VAL >= 200 for PASS (common block). n VAL < 100: UNDERPOWERED. 100 <= n < 200: may FAIL, never PASS. DEV episodes < 15: UNDERPOWERED. Rule verdict: PASS if at least one primary cell PASSes; UNDERPOWERED if all 6 are UNDERPOWERED; else FAIL. "Beats placebo" is reported separately from "profitable". For this event-style rule the tradeable version is the only version (no separate event study is gated).
Kill rules: if DEV L-TURN signals total < 60 the cell is reported thin and the trigger is NOT loosened. No parameter, cell or threshold changes after seeing results; a bug fix is a separate commit listed under Deviations.

## Parameters
| Parameter | Value | Label |
|---|---|---|
| SMA lengths 20 / 50 / 200, simple | 20, 50, 200 | SOURCED (a8RP5ftOfGo, PLJda-dtBIc, FzNDQm7wC_s 00:02:39) |
| Two closes for flip and stop | 2 | SOURCED (a8RP5ftOfGo 00:08:50, PLJda-dtBIc 00:13:25, lmhqooBqJWU 00:07:26) |
| SMA200 hold (short) | 10 closes, strict | SOURCED (10-12 days, a8RP5ftOfGo 00:09:40); strict reading and the value 10 are OURS |
| Long trigger SMA20 leg | on | OURS |
| Arming | >= 10 of 30 days under SMA200 ending t-2 | OURS |
| Freshness (day before f not confirming) | on | OURS |
| Cycle thresholds -20% / W200 | MTS BRAINS spec | OURS |
| Coin phase: SMA20 slope lag 5, ADX14 >= 20, DI sign | as stated | OURS (common-block definition; labeller written here, see below) |
| ADX V1 threshold 20 and DI sign | 20 | OURS |
| RSI14 Malkan 40/60, lookback 20 | 40 / 60 / 20 | 40/60 SOURCED (Malkan); 20 OURS (function default) |
| AT-level D <= 1.5 ATR | 1.5 | OURS |
| Time stop | 60 days (1h row: 1440 bars) | OURS |
| R floor | 0.5% of entry, 0.6 x ATR14 | OURS (common block) |
| Structural window | 10 daily bars | OURS |
| Episode gate | 15 episodes, 10-day chaining | OURS |
| Funding veto | 3-day mean vs trailing 90-day p90 / p10 | OURS |
| Entry at next open | | OURS |

## Design items not implemented / readings changed before any run
1. The design says to reuse `nkp1-session-rules-phase-1114/phases.py` for the coin trend phase. That file is the BTC 6-phase BRAINS labeller (MARKDOWN, MARKUP, ...), not the per-coin UP/DOWN/RANGE labeller of the common block. No UP/DOWN/RANGE code exists in the repo, so `trend_phase()` in study.py implements the common-block definition: UP = SMA20 slope over 5 days > 0 and ADX14 >= 20 and +DI > -DI; DOWN mirror; else RANGE (ADX/DI from `adx_di`, causal, completed days only). This is a reading of "20-day MA slope with 5-day lag", fixed here. The BTC cycle state is read from `phase_daily.csv` (as the design says); its label day d holds the state at the close of day d-1, so the state at the close of day t-2 is the row dated t-1.
2. Fresh 10-coin holdout (design open doubt 5): no OHLCV for fresh coins exists in the cache, and the bars were not fetched; verdicts rest on the 20 coins. Said in RESULT.
3. Funding veto cells need a funding file: NEAR, FIL, ALGO have none in the cache (the other 17 do); those three coins are absent from cells 20-23 only. The veto needs a 90-day warm-up, so early DEV is lost there. The design's "drop the veto if the 2-close vs 1-close ordering is unchanged" is applied by reading the cells 20-23 against 1-8 in RESULT, not by code.
4. 15m and 4h rows: not expressible (design). The task asked for rows at those timeframes "wherever the rule can be expressed"; it cannot.
5. The maker 6 bp row is a fee sensitivity on the same trades, with no fill model (the rule exits at opens).
6. The `ex-best-5` removes the 5 best DAYS (cluster consistent), not the 5 best trades.
7. OI 5-day change is descriptive; its coverage starts 2020-09 (BTC); NEAR/FIL/ALGO have none.

## Protocol and tests
`study.py run` computes everything once and refuses to run while PRE_REG.md / study.py / test_study.py are uncommitted. `test_study.py` (synthetic data, no cache access, < 20 s): truncation invariance of indicators, phases, ADX, RSI regime, every cell mask and the placebo pools (fails with a centred SMA), hand-computed fee on both legs, split by signal bar, gap fill, exit and time-stop and unresolved hand cases, trigger hand cases (long, short, freshness, arming, strict hold), de-overlap, a control-phase signal never landing in a primary cell, episodes, BH, ex-best-5, placebo, loader assertions, resampler partial-day handling. Output files are small (< 200 KB, test).

## Weaknesses stated up front
BTC-based cycle: effective n is episodes, not signals (20 correlated coins; day clusters and the episode gate are the honest unit). VAL (2024-26) is bear-heavy, so L-TURN may be thin or one episode. The short cell needs cycle BULL and an alt that has sat under its own SMA200 for 10 days; it may be nearly empty and the trigger is not loosened. V1 is the same indicator family as the phase label (read two bars earlier) and may add little. Prior phase fixes on NK rules all FAILed.
