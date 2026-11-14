# NKN-03 context design (frozen before results)

Rule: full NK intraday sequence (3KnEiKNh1pc). No backtest or outcome data was used. Splits: DEV before 2024-01-01, VAL 2024-01-01 to 2026-11-13 (as in earlier NK studies). Fee 12 bp taker, plus funding on holds that cross a funding stamp.

## Phase tested
- **PRIMARY phase:** BTC day label MARKUP (`<local-path>`, column `label`, same label for every coin, built from closes through d-1; rows with `provisional=True` are excluded). Side: LONG only. MARKUP is the cycle-state half (c > SMA50, S50 >= +1%, c > SMA200 or BULL) and already implies an up trend phase, so no second coin-level phase gate is stacked. The coin's own 11-14 trend phase (MA20 slope + ADX14 >= 20) is a report column only. (The PHASES angle wanted trend-phase x cycle in one cell; stacking on a conjunction rule only thins n. Resolved: MARKUP alone.)
- Counts on disk (label counts, 2024-01-01 to 2026-11-13): MARKUP 321 of 1048 days (31%), DISTRIBUTION 333, MARKDOWN 198, ACCUM-RANGE 156, RELIEF 34, CAPITULATION 6. (The PHASES angle guessed under 25%; the file says 31%.)
- **CONTROL phases (reported separately, never pooled):** ACCUM-RANGE longs; DISTRIBUTION longs (up-trend but not MARKUP); MARKDOWN mirror shorts (the mirror is OURS, NK gave only longs in this video). RELIEF (34 days) and CAPITULATION (6) are descriptive only, not run.

## Context conditions (closed bars only; "window" = the NY session row unless stated)
1. **Cycle label MARKUP** for the day. OURS (label thresholds OURS). One value.
2. **Index filter:** BTC daily close d-1 > SMA20 and > SMA50 (SOURCED 3KnEiKNh1pc 00:15:29; BTC as Nifty proxy OURS). Implied by MARKUP; reported as a redundancy check, not an extra gate. NK says "otherwise cut size"; our hard skip is OURS. BTC uses its own close.
3. **Session open = 13:30 UTC (NY).** OURS. NK's "first 10 minutes" needs an open and crypto has none; NK5's only positive row was NY. The UTC day (00:00 open) is a control only.
4. **Prior reference:** the prior window runs 13:30 of d-1 to 13:29 of d. Prior close = close of the 13:29 minute; prior high = high of that window. OURS (no gap exists; SOURCED idea 00:07:24).
5. **Scanner:** first-hour return (close of the 14:29 minute vs open of 13:30) >= +2% (SOURCED 00:09:15). A second primary row at >= +1% (SOURCED alternate). No rank row, no alt-specific threshold.
6. **Trap:** within minutes 0-9 after 13:30 the 1m low is below the prior close (SOURCED 00:07:24; 10 min SOURCED, 1m bars OURS), then a 1m CLOSE above the prior close before 14:30 (SOURCED idea; close-not-wick OURS).
7. **Confirmation:** the first session-anchored 1h candle (13:30-14:29, built from 1m, anchor OURS) closes above the prior window high (SOURCED 00:08:07, 00:08:58). 60 min primary; the 90 min variant is dropped.
8. **Skip:** first 1h range (high-low)/open > 4% (OURS; NK said only "big", 00:12:01). Fixed once; skip count and share reported.
9. **HM filter:** HM(9,3,21) on the last closed epoch-aligned 1h bar must favour a long (SOURCED agree 00:18:24). Fixed reading, formula and line colour OURS and unverified: EMA3 of RSI9 above WMA21 of RSI9 AND RSI9 > 50. Use the HM helper in `research/nkp1-session-rules-phase-1114_2026-11-14/study.py` (WMA present there).
10. **Entry:** first 1m bar from 14:30 on with low <= session VWAP (VWAP from 13:30, typical price x volume, 1m; SOURCED place 00:10:08, definition OURS); fill at VWAP, or at the open if it opens below. A touch must come before 20:00 UTC or no trade. No entry before 14:30 (SOURCED patience 00:15:10).
11. **Stop:** session low since 13:30 (SOURCED "day low" 00:10:48), widened to the common floor R = max(structural, 0.5%, 0.6 x ATR14 daily through d-1) (floor OURS). Also a VWAP stop: a close of an epoch-aligned 1h bar below VWAP exits at that close (SOURCED 00:25:50). Both are part of the one rule version, not separate rows.
12. **Exit (one only):** 20:00 UTC (NY cash close, session end), OURS. The 2R target, the 8 h hold and the 24 h hold are not run.
13. **Funding/OI:** descriptive columns only: prior-day funding sum vs its own 90-day percentile, 5-day OI change. Never a gate (earlier OI-class studies did not separate).
14. **Tags only, never gates:** coin 11-14 trend phase, cycle clock / BIBLE reading, CBP lean.

## Crypto translation
- **Session open:** NY 13:30 UTC primary; UTC day 00:00 control. London and Asia dropped.
- **Gap replacement:** dip below the prior-window close, then a 1m close back above it. This is a plain level sweep, a WEAK port (earlier sweep-reclaim studies had gross about 0).
- **Funding/OI:** conditioning columns only (item 13). Files `<local-path>` (8h) and `<COIN>_oi_daily.csv` exist (23 coins); no hourly OI, no liquidations.
- **BTC market filter:** item 2.
- **Does NOT translate:** overnight gap psychology; weekly expiry and option-chart confirmation; options strike/delta; a stock-style mover scanner on a small universe.
- **Dropped as not computable here:** volume-profile/order-flow layers (need aggTrades), taker-delta divergence (already negative), BUY_ZONE_MAP (hand-built BTC snapshot, would look ahead), value area/POC, hourly OI, liquidations, the funding 80th-percentile gate.

## Layer agreement
All reads use bars closed before the entry bar. Verified present in the worktree: `backtest/layers/rsi/rsi_core.py` (`rsi_core(closes, period)`), `backtest/layers/adx/adx.py` (`adx_di(high, low, close, n=14)`), `backtest/layers/timeframe/tf_resample.py` (`resample(bars_1m, tf, registry)`; registry has 1h, 4h, 1d). A look-ahead test (alter bars after the read time; the read must not change) is required before the run.

| Variant | Definition | Labels |
|---|---|---|
| V0 | Rule alone (items 1-12, which already carry the BTC index filter and the 1h HM) | reference |
| V1 | V0 AND 4h Wilder RSI14 >= 50 on the last closed epoch-aligned 4h bar (`rsi_core`, period 14, tf_resample 4h) | RSI14 SOURCED (FORMULAS s1); the 50 cut OURS |
| V2 | V1 AND daily ADX14 >= 20 AND +DI > -DI on the last closed daily bar (`adx_di`) | ADX SOURCED (FORMULAS s30); 20 SOURCED in the NK55 common block |

- Shorts mirror (RSI <= 50, -DI > +DI) in the MARKDOWN control only (C4 uses V0 only).
- Disagree controls: V0 AND NOT V1, and V0 AND V1 AND NOT V2. Report gross R lift of V1 over V0 and V2 over V1, not net R alone.
- Expected overlap: 4h RSI is correlated with the HM and with MARKUP; a small marginal lift is not a flaw.

## Level type
- **Primary level: classic daily pivot ladder, P = (H+L+C)/3, S1 = 2P - H, R1 = 2P - L**, from the prior closed window (13:30 d-1 to 13:29 d for the NY row; prior UTC day for the C5 control). Pivot family SOURCED (NK2; the Part 1 pivot table supplies the quote); window basis OURS. Same family exists in `research/nkp2-levels-phase-1114_2026-11-14/nkcore.py`.
- **At-level (one test):** entry price E; a long is at-level if min(|E-P|, |E-S1|) <= 0.25 x ATR14(daily, through d-1). The band is OURS, one value. Set {P, S1} for longs, {P, R1} for shorts (OURS).
- **Away-from-level:** the complement.
- The level is a TAG on the V0 entry, not a new trigger. The ladder is frozen at window start; test that altering day d's bars does not change d's ladder.
- **Circularity guard:** P contains the prior close and the trap is a dip/reclaim of that close, so at-level may be nearly always true. Report the at-level share. Above 90%, P5 is declared REDUNDANT (same sample as P1) and C1 is UNDERPOWERED.
- Placebo for at-level (C10): random same-phase days, same entry clock, same at-level split.

## Timeframes
- 1m: trap, VWAP, entry, stop, exit (the only way to express the 10-minute trap).
- 1h: session-anchored from 1m for scanner/confirm/skip; epoch-aligned for HM and the VWAP stop. Required by the source.
- 15m: one CONTROL (C6) on the 20-coin spot universe (`<local-path>`): trap read on the first 15m bar (low below prior close, close above it), confirm within 60 min. Coarser and weaker, OURS.
- 4h: L-RSI read for V1/V2.
- Native daily: MARKUP label, BTC SMA20/50, ATR14, ADX, pivots. Weekly: not expressible for an intraday rule; weekly context enters only through the cycle label. No weekly rows.

## Data coverage (checked on disk)
- 1m, `<local-path>`: BTC, ETH, BNB, XRP from 2019-01-01; ALGO from 2026-09-01 only; ADA and DOGE part files exist but stop before the end of VAL (read from listings, not probed). The VAL 1m universe is 4 coins (BTC, ETH, BNB, XRP). A coin enters a split only with >= 95% minute coverage there (probe is part of the run). Fetching more public 1m is a separate step, not assumed.
- 15m spot (20 coins), funding (23 coins), `binance_spot_htf` (5 coins 1d/4h/1w), `phase_daily.csv`, `btc_cycle_features_1114.csv`: present.

## Cells
Every cell: NY row unless stated, entry/stop/exit as items 10-12, 12 bp, no grid, no tuning on DEV. VAL gives the verdict.

| # | Phase cell | Variant | Scanner | Level | TF | Side | Role |
|---|---|---|---|---|---|---|---|
| P1 | MARKUP | V0 | +2% | all | 1m/1h | long | PRIMARY |
| P2 | MARKUP | V0 | +1% | all | 1m/1h | long | PRIMARY |
| P3 | MARKUP | V1 | +2% | all | 1m/1h/4h | long | PRIMARY |
| P4 | MARKUP | V2 | +2% | all | 1m/1h/4h/1d | long | PRIMARY |
| P5 | MARKUP | V0 | +2% | at-level | 1m/1h | long | PRIMARY |
| C1 | MARKUP | V0 | +2% | away | 1m/1h | long | CONTROL |
| C2 | ACCUM-RANGE | V0 | +2% | all | 1m/1h | long | CONTROL |
| C3 | DISTRIBUTION | V0 | +2% | all | 1m/1h | long | CONTROL |
| C4 | MARKDOWN | V0 mirror | -2% | all | 1m/1h | short | CONTROL |
| C5 | MARKUP | V0, UTC-day row (00:00 open, exit 08:00 UTC, descriptive) | +2% | all | 1m/1h | long | CONTROL |
| C6 | MARKUP | V0, 15m trap, 20 coins | +2% | all | 15m/1h | long | CONTROL |
| C7 | MARKUP | V0 AND NOT V1 | +2% | all | 1m/1h/4h | long | CONTROL |
| C8 | MARKUP | V0 AND V1 AND NOT V2 | +2% | all | 1m/1h/4h/1d | long | CONTROL |
| C9 | MARKUP | random same-phase placebo for P1 | n/a | all | 1m | long | CONTROL |
| C10 | MARKUP | random placebo for P5, same at-level split | n/a | at-level | 1m | long | CONTROL |

**Total cells tried: 15. Primary cells: 5.** BH over the 5 primary rows only. A primary passes only if: day-cluster CI low > 0 on VAL, ex-best-5 > 0, holds at 12 bp, beats the placebo, and DEV gross R >= 2x fee R (checked before VAL is opened; failing it drops the rule). One run, no re-runs with changed values. Code frozen in the same commit as PRE_REG.

## Underpowered rule
A cell with n VAL < 100 is UNDERPOWERED, not FAIL. Report n DEV, n VAL and a funnel (scanner, trap, confirm, skip, HM, VWAP touch counts) plus MARKUP's share of DEV days; under 5% of DEV days forces UNDERPOWERED. An UNDERPOWERED cell is never pooled with another to reach n and no condition is loosened afterwards.

## Open doubts
1. Power is the main risk: +2% mover AND trap AND confirm AND HM on 4 coins in MARKUP may give only tens of events, so most primary cells may be UNDERPOWERED. P2 (+1%) exists for that reason, pre-registered, not chosen afterwards.
2. NY 13:30 as primary session is OURS, not NK's.
3. HM formula and which line is "red" are unverified (OURS); the fixed reading may be the wrong way round.
4. The 4% skip cap overlaps the +2% scanner (a mover candle can also be "big"); NK gave no number.
5. Session-anchored 1h candles (13:30) are not in `registry.json` (epoch-aligned); the study builds them from 1m and needs its own test.
6. The pivot level is probably circular with the trap; NK2's best pivot row was -0.009 R.
7. VAL is one bull-then-bear cycle; a pass is a regime result, not a cycle law.
8. ADA/DOGE 1m coverage was not probed at minute level.
9. All earlier NK studies had gross R near 0; the DEV gross-vs-2x-fee check may end this rule before VAL.
