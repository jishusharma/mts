# EDGE WAVE 3 DESIGN (SWING, T7-T12), 2026-11-14

Judge's note: three designers (sourced, power, skeptic) were merged per idea. Winner per idea and grafts are in the summary table. Nothing here was run, fetched or edited. Counts quoted are the power designer's gate-day counts (no outcomes read); the PRE_REG counting step replaces them with measured numbers before any outcome is read.

## Summary table

| Id | Idea | Winner base | Grafts | Bars / stop / fee in R | Primary cell | Expected VAL independent units | Power outlook |
|---|---|---|---|---|---|---|---|
| T7 | Cycle-bottom long | power (coin-level deep DD + weekly reclaim) | skeptic: BTC-state strata, episode row, same-window placebo; sourced: BTC reclaim event as descriptive row | 1d + weekly; 12-15%; 0.008-0.010 | 1 | 28-32 weeks (4-8 episodes) | borderline, episodes UNDERPOWERED |
| T8 | Bollinger range-to-range | skeptic (coin range gate, mirror control) | sourced: width filter + frozen target; power: 1d primary, 4h secondary | 1d; 4-9%; 0.014-0.03 | 1 (+ 4h row) | 45-90 weeks | best powered |
| T9 | Weekly-trend pullback long | skeptic gates + sourced MA pair | power: independence cap, basket baseline; sourced: T6 exclusion | weekly; 10-18%; 0.007-0.012 | 1 | 25-35 waves, 50-60 weeks | borderline |
| T10 | Bear relief-rally short | power gate (BTC < SMA200d) | skeptic: episode unit, 3-bear-period report, carry split; sourced: frozen target | 1d; 6-10%; 0.012-0.02 | 1 | 20-27 weeks | borderline, likely UNDERPOWERED |
| T11 | Breadth washout long | power trigger (measured episode counts) | skeptic: dose-response, leave-one-event-out; sourced: cycle control row | 1d; 10-14%; 0.009-0.012 | 1 (+ BTC>SMA200d row) | 13-19 episodes | UNDERPOWERED by design, descriptive |
| T12 | Funding extreme reversal | power gate + skeptic carry split | sourced: phase gates per side, OI descriptive only | 1d; 6-12%; 0.010-0.02 | 2 (long, short) | 25-50 weeks per cell | A testable, B borderline |

---

# SHARED RULES (T7-T12)

## Data
- Root `<local-path>`. 1d and 4h spot: `binance/wave2-1114/spot_1d`, `spot_4h` (50 coins) and `binance/combo-edge-miner-1114/spot_1d`, `spot_4h` (20 coins). Funding: `wave2-1114/funding`, `combo-edge-miner-1114/funding`. OI (20 coins only, T12 descriptive): `combo-edge-miner-1114/oi`. Phase: `mts_brains/phase_daily.csv` (label for day d uses closes through d-1; BTC only).
- Universe: 68 distinct coins (50 wave2 + 20 miner; BTC and ETH once). Named list is the union of the two folders' file lists, read at run time and written to the PRE_REG. Delisted coins are kept; a trade open at a coin's last bar closes there and is flagged ENDED. No trade may span the LUNA (2022-05-13..05-31) or FTT (2022-11-15..2023-09-22) holes. Every RESULT carries an ex-ENDED and ex-LUNA/FTT row and states the survivorship direction (longs biased up, shorts biased down).
- A coin is alive on day d with >= 260 daily bars of history (T7: >= 365). Signal dates with fewer than 30 alive coins are excluded from verdicts and counted separately (about 16 coins in 2018, 44 by end 2019).
- Weekly bars: resample 1d to ISO weeks (Monday 00:00 to Sunday 23:59 UTC). A weekly value is usable only from the following Monday bar. Required unit test: a planted Sunday-only spike changes the signal on Monday and never on Sunday.
- No fetch is needed for the primary cells. Optional later fetch card (not blocking): 50 more liquid coins plus OI for all, using `wave2-1114/_fetch/w2fetch.py` as template into a new cache folder; it would help T7, T9, T10, T12 OI row.

## Execution and cost
- Signal on completed bar t, entry at the t+1 open, all flags use data through t. Stop wins ties. Fee 12 bp round trip = `2*BINANCE_TAKER + SLIPPAGE_RT_S13` imported from `MyTradingSys/backtest/fees.py`; no private cost constants. Real signed funding charged per 8h print where a perp is implied (all shorts; longs too), on spot prices as proxy (basis flagged). No funding imputed: no trade where funding is missing in the hold window (T12) or funding reported as NOT_IN_DATA row (others).
- Stop distance >= 1.5% of entry on every idea (fee <= 0.08 R). Fee in R = 0.12% / stop%.
- BTC smoothed cycle state (OURS): the cycle column state counts only after 10 consecutive days; until then the prior state holds. Coin-level flags are built from the coin's own closes through the signal bar.

## Splits and statistics
- DEV = signal bar <= 2023-12-31; VALIDATION = signal bar >= 2024-01-01 (T12 VAL ends 2026-10-31, funding end).
- Primary unit: ISO entry week over all coins (coins move together), moving-block bootstrap with the block stated per idea, 2000 resamples, seed 1114. Episode or event unit where stated is reported as the second unit. Never the trade.
- `scripts/dev/prereg_gate.py` must be fed `--n` = distinct independent units (weeks or episodes), never trades, with `--sd` from the DEV week-level sd of the counting step (floor 1.0 R), `--m` as stated per idea. State the n used. A BLOCK is reported, not hidden, and the run is still ordered.
- Family: 9 cells total (T7 1, T8 2 incl. 4h row, T9 1, T10 1, T11 2, T12 2). Holm over the family is reported next to each verdict in addition to the per-study Holm.

## Pass bars (wave-2 bars 1-7 as base; wave-2 wording wins on any discrepancy)
1. VAL fresh: n >= 30 trades and >= 20 entry weeks (idea-specific unit minimum where stated), else UNDERPOWERED (never FAIL, never KILL).
2. VAL mean net > 0 and cluster-bootstrap 95% CI low > 0.
3. DEV mean net > 0 (sign agreement).
4. Excess over like-for-like placebo: 1000 draws, same coin, same regime flag, same split, same stop distance in %, same exit rule, same side; real mean above the 97.5th percentile. Placebo entries are drawn inside +/-8 ISO weeks of the real trade (same-window) and also reported as a global variant (any flagged day of the coin and split). Per-idea override of the window is stated.
5. Ex-best-5 entry weeks mean > 0 (ex-best-2 units when units < 30; RIDE-style or tail-shaped exits also report a 3R-capped row).
6. Baseline: mean net daily return in position >= the stated equal-weight baseline basket over the same eligible days (side matched).
7. Top-3-coin removal keeps the mean > 0, else FRAGILE (reported, blocks PASS).
Added for wave 3 (apply to all): 8. Leave-one-year-out stays > 0 (reported; failure = FRAGILE). 9. Row by BTC cycle state (BEAR/BASE/BULL) and by year always printed; a result positive only in the phase opposite to its gate is labelled SIGN-FLIP, not PASS. Verdict vocabulary: PASS, FAIL, UNDERPOWERED, FRAGILE, SIDE-SPLIT, CARRY-ONLY, NOT-A-PASS (descriptive).

## PRE_REG lint and process
- File `MyTradingSys/research/t<n>_<slug>_2026-11-14/PRE_REG.md`, section order as T6: Context, Rules, Data, Splits, Pass bars, Kill criteria, Verdict vocabulary, Seen results, Known weaknesses, Power gate (paste `prereg_gate.py` output), Protocol.
- `## Context` must contain four non-empty lines starting `Regime:`, `Phase:`, `Session:`, `Entry:` (`none, because ...` allowed). Any RESULT*.md or DEV_CHECK*.md needs a line starting `Regime mix:` (bull/bear/range shares or NOT_IN_DATA). Template `MyTradingSys/backtest/PRE_REG_TEMPLATE.md`; lint `scripts/dev/prereg_context_lint.py`.
- Every parameter is labelled SOURCED (with source) or OURS. Never call OURS the trader's. BIBLE.md has no line on Bollinger, funding, breadth, weekly pullbacks; those are OURS.
- Step 1 counting step first: signal counts and unit counts only, no outcomes, pasted into PRE_REG. Step 2 trades list with no pooled statistics. Independent recompute of 3 dated trades from raw klines and FORMULAS.md plus an adversarial look-ahead and fee audit before statistics. Then stats and RESULT, checker re-derives verdict from the PRE_REG bars. Seen results: only the inventory counts above.
- Tests: synthetic-bar only (look-ahead, stop-wins-ties, fee arithmetic from fees.py, Sunday-spike test, planted edge, mutation check; new tests must fail on pre-change code). Reuse patterns (not imports) from T6 (`t6_core.py`, `t6_stats.py`) and T3.
- Module prefix rule: every module is prefixed by its study id: `t7_core.py`, `t7_stats.py`, `test_t7_core.py` ... `t12_*.py`. No bare `lib.py`, `core.py` or `stats.py`; no cross-study imports. Shared constants come from `fees.py`, `research_kit.py`, `splits.py`.
- Run order: T8, T9, T12, T10, T7, T11 (T11 first to drop if budget is short).

---

# T7 CYCLE-BOTTOM LONG (coin drawdown + weekly reclaim)

- **Hypothesis:** a liquid coin at least 55% below its 2-year closing high that makes a fresh weekly close back above its own 10-week average has put in a local cycle bottom, and the next 4 weeks pay net of fees. (Operator claim: deep drawdown from cycle high plus weekly reclaim.)
- **Regime:** coin state DD: last completed weekly close <= 0.45 x max daily close of the prior 730 days (window = available history, >= 365 bars). BTC smoothed cycle state is a stratum only (BEAR/BASE/BULL rows), not a gate, because the BTC-only bottom count is too small to power.
- **Entry:** completed weekly bar w: weekly close > SMA10 of weekly closes, previous weekly close <= previous SMA10, and coin in DD state at w. Enter Monday 1d open. Cooldown 28 days per coin (one trade per coin per 4 weeks).
- **Stop:** entry x (1 - max(3 x ATR14 1d (Wilder) / entry, 10%)). Typical 12-15%, fee 0.008-0.010 R. Floor 10% far above the 1.5% minimum.
- **Exit:** first of stop, or close of day 28 (time exit). (Hold set by the independence cap: non-overlapping 4-week blocks.)
- **Universe:** the 68-coin union, alive rule >= 365 bars.
- **Split:** DEV <= 2023-12-31, VAL >= 2024-01-01. Fee 12 bp, signed funding.
- **Statistics unit:** ISO entry week, moving-block bootstrap block 4 weeks. Second unit: episode (entries whose entry dates chain with gaps < 28 days form one episode; trades averaged within an episode). `prereg_gate --n` = VAL distinct entry weeks (blocks of 4 weeks capped at 37), `--m 1`.
- **Placebo:** same coin, same DD state at a completed weekly bar (flag only, no cross requirement), random Monday entry inside +/-8 ISO weeks of the real trade, same stop % and 28d exit. Tests "reclaim timing" against "being deeply oversold".
- **Baseline:** equal-weight basket of all coins in DD state entered on the same Mondays, held 28 days.
- **Descriptive rows (not pass cells):** (a) BTC-only sourced event row: first weekly close above the 200-day SMA after >= 8 weekly closes below it, with BTC smoothed state BEAR on >= 20 of last 52 weeks and 52-week min drawdown from cycle high <= -45% (expected 3 DEV events, 1 VAL event, 2026-07), basket of DD coins from that Monday, exit on BTC weekly close below reclaim-week low or 26 weeks; BTC alone from `btc_cycle_features_1114.csv` as sign check (about 6-7 bottoms). (b) BEAR-only and BASE-only rows (a weekly SMA10 cross inside a bear is a bear-rally trap; if BEAR is negative, "BASE only" is reported as the claim).
- **Pass bars:** wave-2 1-7 with bar 1 = VAL >= 30 trades and >= 20 entry weeks; episode row requires >= 8 VAL episodes else the episode reading is UNDERPOWERED with no kill. Bar 5 ex-best-5 weeks and ex-best-2 episodes.
- **Kill criterion:** VAL mean net <= 0 with >= 20 weeks, or placebo excess <= 97.5th percentile with n >= 100 trades (then the reclaim adds nothing over being oversold). Fewer units gives UNDERPOWERED, not KILL.
- **Parameters:**

| Parameter | Value | Label |
|---|---|---|
| DD depth/window | <= 0.45 x 730d max close | OURS (operator "cycle high" idea; BIBLE s1 drops -54 to -85%) |
| Reclaim | weekly close crosses above SMA10w | OURS |
| BTC reclaim row | first weekly close above SMA200d after 8 weeks below | SOURCED idea (BIBLE s5 "price holds the 200-day"), count 8 OURS |
| ATR | Wilder 14 | SOURCED (Wilder 1978) |
| Stop | max(3 ATR14, 10%) | OURS |
| Hold / cooldown | 28 d / 28 d | OURS |
| BTC smoothing | 10 consecutive days | OURS |
| Fee, funding | 12 bp, signed | SOURCED (fees.py, cached funding) |

- **Expected independent VAL units:** about 519 coin-signals in 74 distinct weeks (power count at 0.45); about 300 trades after cooldown; 28-32 effective 4-week blocks; 4-8 episodes. Borderline, short of 45; gate expected BLOCK.
- **Difference from failed studies:** cycle-conditioned-buy-odds was BTC only (about 4 bottoms, skill 0.00) with no trigger; T6 buys any 20% dip off an 8-week high with no depth or reclaim; edge9 weekly streak has no depth or reclaim; washouts were intraday.
- **Honest weak point:** every bottom is the same 4-6 market dates (2020-03, 2022-06/11, 2024-08, 2025-04), so weeks are not independent beyond blocks and the result is mostly beta rebound plus survivorship; a PASS here is reported as strong evidence only if placebo and basket both clear.

---

# T8 BOLLINGER RANGE-TO-RANGE (1d primary, 4h secondary row)

- **Hypothesis:** inside a ranging coin, a close outside the Bollinger band that closes back inside travels to the opposite band within 20 days, and the move is large against a stop of >= 1.5%. (Operator's own claim; no source quote.)
- **Regime:** coin-level, known at the signal bar close: ADX14 (1d, Wilder) < 20 AND (max high - min low over last 30 daily bars) / mean close <= 0.30. BTC label in {ACCUM-RANGE, DISTRIBUTION} is a reported stratum, and the ACCUM-RANGE-only subset is a second stratum; neither is a gate (the label gate alone leaves only about 22 VAL weeks).
- **Entry (long):** on bar t, close back above the lower band BB(20, 2) after any close below the lower band within bars t-3..t-1 (first re-entry only); band width (upper - lower)/middle at signal >= 10%. Enter t+1 open. **Short:** mirror at the upper band. Cooldown 10 days per coin and side. Bands use closes through the bar tested.
- **Stop:** beyond the lowest low (long) or highest high (short) of bars from the outside close through t, -/+ 0.5 x ATR14, floor 1.5% of entry. Typical 1d 4-9%; fee 0.014-0.03 R.
- **Exit:** target = opposite band value at the signal bar, frozen at entry; or 20 daily bars; or stop (stop wins ties).
- **Universe:** 68-coin union; shorts perp-implied with real funding.
- **Split / fee:** DEV <= 2023-12-31, VAL >= 2024-01-01, 12 bp + funding.
- **Statistics unit:** ISO entry week over all coins, block 2 weeks. Second unit: BTC range episode (consecutive ACCUM-RANGE/DISTRIBUTION blocks).
- **Cells:** primary = 1d, both sides pooled (long and short also reported per side). Secondary row = 4h bars with the same rules (bands on 4h, 1d coin gate at the last completed 1d bar, floor 2.5%, 42 bars time exit, cooldown 2 days); fee 0.03-0.05 R. Holm m = 2.
- **Placebo:** same coin, same side, same coin range gate, random day inside +/-8 weeks and inside the gate, same stop %, same target % (same R:R), same time cap, no band-reclaim trigger. Tests band location against any random range day.
- **Negative control (primary number):** mirror trade: long at the upper-band re-entry, short at the lower-band re-entry, same stop and target rules mirrored. Real minus mirror must be > 0.
- **Baseline:** random-day trade, same side, symmetric 1:1 bracket, same gate; plus the hold-the-range test (same coin held 20 days in the same direction).
- **Pass bars:** wave-2 1-7 with bar 1 = VAL >= 200 trades and >= 40 entry weeks; bar 4 excess CI low > 0; plus: real minus mirror > 0; both sides' means > 0 else verdict SIDE-SPLIT; worst week > -4 R (loss-tail guard); bar 6 against the random-day bracket and the 20-day hold.
- **Kill criterion:** primary VAL net <= 0, or real-minus-mirror <= 0, or placebo excess <= 97.5th percentile with >= 200 trades. Then 1d range-to-range is dead (4h is untested-then-dead only if its row also fails).
- **Parameters:**

| Parameter | Value | Label |
|---|---|---|
| Bollinger | 20, 2 | SOURCED (Bollinger standard; operator claim, "never spoken" as numbers) |
| ADX gate | 14, < 20 | SOURCED (Wilder 1978) |
| 30d range/close | <= 0.30 | OURS |
| BTC label strata | ACCUM-RANGE, DISTRIBUTION | SOURCED (MTS_BRAINS_SPEC lines 27, 29), use as stratum OURS |
| Re-entry window | 3 bars | OURS |
| Band width filter | >= 10% | OURS |
| Stop | extreme -/+ 0.5 ATR14, floor 1.5% | OURS |
| Target | opposite band frozen at signal | OURS (operator's claim) |
| Time cap / cooldown | 20 d / 10 d | OURS |

- **Expected independent VAL units:** 45-90 entry weeks (power: 90 weeks and 2117 raw coin-signals under a proxy flag; about 45 effective 2-week blocks after ADX and cooldown); 400-700 trades. Clears bar 1. Gate expected BLOCK to borderline at sd 1 R.
- **Difference from failed studies:** bb_range_to_range and bb_long_window are BTC 15m/spot, fee 0.2 R, 0 of 6 cells positive; bb_range_retest* were BTC and ETH, BLOCKED not failed. New: 68 coins, 1d (and 4h), fee 0.014-0.05 R, coin range flag from past bars only, frozen target, mirror control.
- **Honest weak point:** short-volatility payoff (many small wins, rare breakout losses) and shared regimes: in a bull VAL, range-flagged alts break up so longs may win and shorts lose; the verdict may be SIDE-SPLIT, and the 15m fee-dominated failures say nothing about 1d either way.

---

# T9 WEEKLY-TREND PULLBACK LONG

- **Hypothesis:** in a coin with an intact weekly uptrend, a week that tags the weekly 21 EMA and closes back above it continues the trend over the next weeks.
- **Regime:** BTC smoothed cycle is BULL or BASE (MARKUP, 321 VAL days, reported as a stratum). Coin weekly flag at the completed week: EMA21w > EMA55w, EMA55w above its value 4 weeks earlier, weekly close > EMA55w.
- **Entry:** completed week w with low <= EMA21w and close >= EMA21w. Enter next Monday 1d open. Cooldown 56 days per coin. Skip the trade if the T6 DD20 rule (close >= 20% below max close of prior 8 weeks, as in the T6 PRE_REG) is true at signal, so T6 and T9 cannot double count.
- **Stop:** signal week low - 0.5 x ATR14 (1d), floor 1.5%. Typical 10-18%, fee 0.007-0.012 R.
- **Exit:** first of stop, first completed weekly close below EMA55w (exit next open), or 84 days (12 weeks cap, keeps independence). Report a 3R-capped row because the exit is trend-shaped.
- **Universe:** 68-coin union; coin enters only after 55 weekly bars.
- **Split / fee:** DEV <= 2023-12-31, VAL >= 2024-01-01, 12 bp + signed funding.
- **Statistics unit:** ISO entry week, moving-block bootstrap block 4 weeks. `prereg_gate --n` = effective 4-week blocks, `--m 1`.
- **Placebo:** same coin, random Monday inside +/-8 weeks with the same weekly flag true and BTC state same, same stop %, same exit rule. Only the touch-and-reclaim trigger is removed.
- **Baseline:** equal-weight basket of flagged coin-weeks held in the same weeks; compare mean net daily return in position. A trigger that only reproduces the trend flag fails bar 6.
- **Pass bars:** wave-2 1-7 with bar 1 = VAL >= 30 trades and >= 20 entry weeks; bar 5 on the 3R-capped row; bar 8 leave-one-year-out; DEV-only (2020-21) positives are flagged FRAGILE.
- **Kill criterion:** VAL mean net <= 0, or placebo excess <= 97.5th percentile with >= 60 trades, or mean in position below the basket on both DEV and VAL.
- **Parameters:**

| Parameter | Value | Label |
|---|---|---|
| EMA pair 21 / 55 | weekly closes | SOURCED pair (BIBLE line 50 Krown 21/55/200 moving averages), weekly timeframe and EMA type OURS |
| EMA55 slope | > 0 over 4 weeks | OURS |
| Touch rule | low <= EMA21w, close >= EMA21w | OURS |
| BTC gate | smoothed BULL/BASE | SOURCED idea (BIBLE s5), thresholds OURS |
| Stop | week low - 0.5 ATR14, floor 1.5% | OURS |
| Exit | weekly close < EMA55w, cap 84 d | OURS |
| Cooldown | 56 d | OURS |
| T6 exclusion | DD20 rule per T6 PRE_REG | OURS |

- **Expected independent VAL units:** coin-weeks in the weekly flag are about 25% of VAL coin-weeks; weeks with >= 5 flagged coins about 86 of 150; trigger not yet counted; estimate 50-60 entry weeks, 25-35 independent waves, about 150 trades. Borderline; gate expected BLOCK on VAL alone, borderline pooled (descriptive).
- **Difference from failed studies:** edge7/edge8 were daily breakout trend-following below buy-and-hold; edge9 weekly streak buys red weeks with no trend gate; T3 is early-uptrend onset; T6 is a 20% dip. T9 is a shallow tag inside an established weekly trend, and the placebo asks whether the pullback adds anything to the trend itself.
- **Honest weak point:** drift and beta. DEV (2020-21) is a 10x alt bull while VAL is an alt-weak bull, so DEV dominates; any long in a flagged trend wins in a bull and only the placebo and the basket row separate trigger from drift.

---

# T10 BEAR-PHASE RELIEF-RALLY SHORT (1d)

- **Hypothesis:** in a bear regime, a coin in a downtrend that rallies at least 12% off its 10-day low into its 20-day average and then prints a red rejection bar falls back to the start of the rally within 10 days.
- **Regime:** BTC prior close < SMA200d (VAL 402 days, about 57 weeks; BIBLE s5 "daily loss of the 200-day"). The narrower BTC labels MARKDOWN or RELIEF (232 VAL days) and the smoothed BEAR cycle state are strata, not gates. Coin flag: close < SMA50 and SMA50 < SMA50 ten days earlier.
- **Entry (short):** rally: signal-bar close >= 1.12 x the lowest close of the prior 10 days. Rejection bar (signal bar): high >= SMA20, close < open, close < prior day's low. Enter t+1 open, short. Cooldown 10 days per coin.
- **Stop:** highest high of the last 5 bars + 0.5 x ATR14, floor 5%. Typical 7-10%, fee 0.012-0.017 R.
- **Exit:** first of stop, target (the lowest close of the prior 10 days measured at signal, frozen at entry; the "falls back to the rally start" claim), or 10 daily bars. Stop wins ties.
- **Funding:** real signed funding on the short (a short pays when funding is negative, common in bears). Report price-only net and total net separately; a result that is positive only with funding is labelled CARRY-ONLY.
- **Universe:** 68-coin union, perp-implied, delisted kept (delisting collapses favour shorts: report ex-ENDED row).
- **Split / fee:** DEV <= 2023-12-31 (2018 and 2022 bears, MARKDOWN 553 DEV days), VAL >= 2024-01-01, 12 bp.
- **Statistics unit:** ISO entry week, block 2 weeks. Second unit: rally episode (entries within 14 days of each other chain). `prereg_gate --n` = VAL distinct entry weeks, `--m 1`.
- **Placebo:** same coin, short side, random day inside +/-8 weeks with the same BTC gate and coin downtrend flag true, same stop %, same target %, same 10-day cap. Not conditioned on a rally. Global variant also reported.
- **Baseline:** short-and-hold of the equal-weight basket of downtrending coins over the same gated days (T5 style).
- **Pass bars:** wave-2 1-7 with bar 1 = VAL >= 30 trades and >= 20 entry weeks; bar 3 DEV net > 0 pooled over 2018 and 2022; bar 4 against placebo; plus sign in at least 2 of 3 bear periods (2018, 2022, 2025-26) reported as a 3-point report, not a test.
- **Kill criterion:** VAL price-plus-funding net <= 0 with >= 40 trades, or placebo excess <= 97.5th percentile with >= 60 trades, or DEV sign negative. Fewer than 20 weeks gives UNDERPOWERED (DEV is then the main read), not KILL.
- **Parameters:**

| Parameter | Value | Label |
|---|---|---|
| BTC gate | prior close < SMA200d | SOURCED idea (BIBLE s5), use OURS |
| Coin downtrend | close < SMA50, SMA50 falling over 10 d | OURS |
| Rally | >= 12% above 10-day low close | OURS (BTC RELIEF +12% is SOURCED, MTS_BRAINS_SPEC line 26; alts more volatile) |
| Rejection | high >= SMA20, red, close < prior low | OURS |
| Stop | 5-bar high + 0.5 ATR14, floor 5% | OURS |
| Target | pre-rally 10-day low close, frozen | OURS (idea: next level, NK "next pivot") |
| Time cap / cooldown | 10 d / 10 d | OURS |

- **Expected independent VAL units:** power count at 8%: 240 raw signals in 33 distinct weeks; at 12%: 119 signals in 27 weeks; after cooldown 20-27 effective weeks, about 60-120 trades. Borderline, likely UNDERPOWERED against 20; stated rescue in order: rally threshold 8%, then adding SMA100d gating for DISTRIBUTION days (rescues are separate rows, never the verdict).
- **Difference from failed studies:** T1 is a 1h pivot rejection, T5 a 4h divergence, edge9 seller-layers intraday (fee 0.4 R), top-87k BTC only n 11, btc-bear-phase-reactions descriptive. This is a daily rally failure with 7-10% stops, 68 coins.
- **Honest weak point:** VAL holds one bear, so VAL is effectively one episode cluster and a DEV-bear or VAL sign flip is likely; delisted-coin collapses flatter shorts while survivor lists penalise them.

---

# T11 BREADTH WASHOUT LONG (market-wide, 1d)

- **Hypothesis:** when many coins are oversold at once and the selling is exhausted, buying the oversold coins pays over the next 10 days.
- **Regime:** primary cell ungated, with a pre-registered prediction: mean > 0 when BTC prior close > SMA200d and mean <= 0 when BTC prior close < SMA200d. Secondary row: BTC prior close > SMA200d only (the control for the DEV sign flip: DEV holds 2022 where washouts kept falling). BTC smoothed BEAR/BASE/BULL rows always printed; a BEAR-state result is "not tradable if negative".
- **Entry:** breadth B(d) = share of alive coins with RSI14 (1d, Wilder) <= 30 at close d. Event day: first day with B >= 15% after >= 7 days with B < 15%. On the event day, every alive coin with RSI14 <= 35 gets a long at the next 1d open. One event is one unit; each coin is one leg.
- **Stop:** entry - max(2.5 x ATR14, 8%) per leg. Typical 10-14%, fee 0.009-0.012 R.
- **Exit:** first of stop or close of day 10. (Wave-3 hold set to 10 d, close to T6's 14 d.)
- **Universe:** 68-coin union, alive rule >= 200 bars and >= 30 alive coins (earlier events counted separately, excluded from verdicts).
- **Split / fee:** DEV <= 2023-12-31, VAL >= 2024-01-01, 12 bp + signed funding.
- **Statistics unit:** the episode: events within 14 days of each other merge into one episode; trades are averaged within an episode first. Event-level and week-cluster CIs are reported as extra rows. `prereg_gate --n` = VAL episodes, `--m 2`.
- **Placebo (primary, like-for-like):** same coin, random day with the coin's own RSI14 <= 35 and breadth < 10%, same BTC state, same split, same stop %, same 10-day exit, same number of coins per draw. Isolates breadth from a single oversold coin. Secondary placebo: random days on the same coin in the same BTC state (no RSI condition).
- **Dose-response control:** events binned by breadth: B >= 50%, 30-50%, 15-30%; the effect should rise with breadth (monotone) or breadth adds nothing.
- **Baseline:** equal-weight basket of all alive coins over the same 10 days.
- **Pass bars:** wave-2 1-7 adapted: bar 1 = >= 8 VAL episodes (pooled DEV+VAL reported as a power row only, never the verdict), else UNDERPOWERED; bar 2 episode-cluster CI low > 0; bar 3 DEV mean > 0; bar 4 vs primary placebo; bar 5 ex-best-2 episodes > 0 and leave-one-event-out stays > 0; bar 6 vs basket; bar 7 ex-LUNA/FTT and top-3-coin removal > 0; dose-response monotone; pre-registered strata prediction holds.
- **Kill criterion:** VAL episode mean <= 0 with >= 8 episodes, or leave-one-event-out flips the sign with fewer than 12 episodes, or placebo excess <= 97.5th percentile. Under 8 episodes: UNDERPOWERED, descriptive only.
- **Parameters:**

| Parameter | Value | Label |
|---|---|---|
| RSI | 14, breadth level <= 30 | SOURCED (Wilder; NK RSI 70/30 per postmortem table, NK note not opened) |
| Entry RSI | <= 35 | OURS |
| Breadth trigger | >= 15% | OURS (power-measured count: 19 VAL, 35 DEV events at 7-day gap) |
| Event gap / merge | 7 d separation, 14 d merge | OURS |
| Stop | max(2.5 ATR14, 8%) | OURS |
| Hold | 10 d | OURS |
| Strata prediction | BTC vs SMA200d | SOURCED idea (BIBLE s1/s5), threshold use OURS |

- **Expected independent VAL units:** 19 events at 7-day gap, 13-15 episodes after 14-day merge, about 14 with the BTC > SMA200d row; effective independence 15-18 at best. Cannot reach 20; UNDERPOWERED by design. Run as a descriptive power row; verdict UNDERPOWERED unless 8 episodes and every bar pass.
- **Difference from failed studies:** edge6_capitulation_breadth had 28 events on 1h with DEV -1.7%; seven washout studies were single-coin or intraday with 15-19 independent days; T2 is 1h Supertrap by cycle state. New: daily breadth across 30+ coins, a breadth-matched placebo, dose-response, strata prediction.
- **Honest weak point:** crash-date concentration (2020-03-12, 2022-05 LUNA, 2022-11 FTX, 2024-08-05, 2025-04-07, 2025-10-10): these dates carry the winners in every washout study, so this is a longer sample of the same event, not a fix.

---

# T12 FUNDING EXTREME REVERSAL (1d, two cells; OI descriptive)

- **Hypothesis:** an extreme funding print means one side is crowded; when price then prints a reversal bar in a phase where the crowd is wrong, the crowd unwinds over about 10 days (price effect, not carry).
- **Regime (phase-specific, BTC label from the phase table):** Cell A (long): MARKDOWN, CAPITULATION, RELIEF or ACCUM-RANGE (MTS_BRAINS_SPEC lines 24-27: "LONG only (reclaim/fade)" for CAPITULATION). Cell B (short): MARKUP or DISTRIBUTION (lines 28-29: "SHORT (failed break, resistance rejection)" for DISTRIBUTION). Cycle state rows always printed.
- **Entry:** funding feature F3(d) = mean of the 8h prints over the last 3 days through d. Cell A: F3 <= the coin's trailing 5th percentile of F3 over 180 days ending d-1 AND F3 <= -0.01% per 8h; reversal bar: close > open and close > prior day's high. Cell B: F3 >= trailing 95th percentile AND F3 >= +0.01% per 8h; reversal bar: close < open and close < prior day's low. Entry at t+1 open. Cooldown 10 days per coin.
- **Stop:** entry -/+ max(2.5 x ATR14, 6%). Typical 6-12%, fee 0.010-0.020 R.
- **Exit:** first of stop or close of day 10. Real signed funding added to P&L.
- **OI (descriptive only, no verdict):** on the 20 coins with OI (from 2020-09, ADA from 2021-12) report the 7-day OI change tercile against the other terciles for each cell (positive OI build for shorts, OI drop for longs as the mechanism reading). No pass bar. A 20-coin OI-gated cell (+20% 7d OI for shorts) is not run.
- **Universe:** coins with funding cached (about 68). Funding starts 2020-01 to 2021-03 and the 180-day window needs history, so first signals are 2020-2021 and DEV is about 2020-2023. VAL ends 2026-10-31.
- **Split / fee:** DEV <= 2023-12-31, VAL >= 2024-01-01, 12 bp. No funding imputed; no trade without funding for the hold window.
- **Statistics unit:** ISO entry week over all coins, block 2 weeks. `prereg_gate --n` = VAL distinct entry weeks per cell, `--m 2`.
- **Placebo:** same coin, same side, same BTC label stratum, random day inside +/-8 weeks carrying the same extreme-funding flag but no reversal bar, same stop %, same 10-day exit. Because the flag is shared, carry cancels and the placebo isolates the price turn. Global variant also reported.
- **Baseline:** equal-weight basket, side-matched, over flagged-state days (price plus carry), and mean funding carry in bp per trade next to it.
- **Pass reporting split:** price-only net (fees, no funding) and total net (price plus carry) both shown. A cell that wins only on carry is labelled CARRY-ONLY and is not a pass.
- **Pass bars (each cell):** wave-2 1-7 with bar 1 = VAL >= 30 trades and >= 20 entry weeks; bars 2, 3, 5 on price-only net (a pass needs price-only excess > 0); bar 4 vs funding-flag placebo; bar 7 top-3 coin removal; Holm over the two cells and over the family reported. A pass on one cell with the other failing is reported as partial.
- **Kill criterion:** both cells VAL price-only net <= 0, or both placebo excesses <= 97.5th percentile with >= 100 trades. Then funding-extreme reversal is dead at the daily level (OI conclusion stays open: only 20 coins).
- **Parameters:**

| Parameter | Value | Label |
|---|---|---|
| Funding formula, 0.01% per 8h baseline | Binance interest-rate component | SOURCED (Binance funding docs) |
| Extreme percentile and window | P5 / P95 of trailing 180 d, ending d-1 | OURS |
| Floor | -/+0.01% per 8h | SOURCED baseline, use OURS |
| Smoothing | 3-day mean | OURS |
| Phase gates | A: MARKDOWN/CAPITULATION/RELIEF/ACCUM-RANGE; B: MARKUP/DISTRIBUTION | SOURCED labels (MTS_BRAINS_SPEC lines 24-29), mapping to funding OURS |
| Reversal bar | colour + prior-bar high/low break | OURS |
| Stop | max(2.5 ATR14, 6%) | OURS |
| Hold / cooldown | 10 d / 10 d | OURS |
| OI change | 7 d terciles, descriptive | OURS |

- **Expected independent VAL units:** power count before reversal bar and phase gate: short floor 0.01%: 566 signals in 66 weeks, long: 946 signals in 138 weeks; expecting about 40% to pass the reversal bar and about half the phase gate: Cell A 25-50 weeks, Cell B 25-40 weeks. Cell A testable, Cell B borderline; gate expected BLOCK at sd 1 R.
- **Difference from failed studies:** edge-crowding-reversal had 57 trades, no reversal-bar trigger, no phase, 21 of 24 cells negative; edge2-ratio-fade-wide used account ratios; edge-oi-flush one 4h episode; T4 is a 4h funding-low breakout with RIDE exit. New: 68 coins, rolling per-coin percentile, reversal-bar trigger, per-side phase gate, 10-day hold, carry/price split.
- **Honest weak point:** extreme funding persists in a bull, so shorts can keep losing, and a long at negative funding collects carry, so the total can beat zero with no price edge; VAL is one bull then one bear, so a sign flip is likely and OI is limited to 20 coins.
