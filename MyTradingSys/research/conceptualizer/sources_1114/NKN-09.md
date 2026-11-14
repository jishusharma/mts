# NKN-09 context design (frozen before results)

Rule: long-leg doji at RSI 30/70 (i2bGV_Wo5Yw). Frozen 2026-11-14 from five angle designs. No backtest, no outcome data read. Prior is LOW: edge-rsi-extreme-confirm (0/384), rsi_confirm_layers (0/56) and NK4 (0/12) failed; this adds a body filter and context only. The common block of NK55_RULES_1114.md Part 2 applies (DEV <= 2023-12-31, VAL >= 2024-01-01 split by SIGNAL bar, 12 bp taker, 6 bp maker non-gating, R floor, BH q <= 0.10, placebo, day-cluster CI, ex-best-5, code committed WITH the PRE_REG).

## Phase tested
**Primary cells (M = 5, one value per parameter, no grid). All use the base signal below, V0 unless stated:**

| ID | TF | Side | Coin-day trend phase | BTC cycle state | Variant |
|---|---|---|---|---|---|
| P1 | 4h | long | DOWN | CAPITULATION | V0 |
| P2 | 1d | long | DOWN | CAPITULATION | V0 |
| P3 | 4h | long | RANGE | ACCUM-RANGE (BTC close in lower half of its 40-day range, spec row 4) | V0 |
| P4 | 4h | long | DOWN | CAPITULATION | V1 (1D WaveTrend agrees) |
| P5 | 4h | short | UP | DISTRIBUTION (spec row 6, short) | V0 |

- Cycle label = MTS_BRAINS_SPEC_1114 six-row table, read from `<local-path>` (column `label`; label day d = state at close of d-1, BTC only, causal; builder `research/nkp1-session-rules-phase-1114_2026-11-14/phases.py`). Rows with an empty label are skipped.
- Coin-day trend phase = common block (20-day MA slope with 5-day lag plus ADX14 >= 20 with DI direction, else RANGE), from the prior daily close; ADX code `research/combo-edge-miner-1114_2026-11-14/miner.py::adx_di`. A coin-day label function written to the common-block text must be added and unit-tested; no ready import exists.
- The cell is the intersection of coin-day phase and BTC cycle state, both fixed at the prior daily close (an intraday doji on day D uses the D-1 labels).
- 4h is the primary intraday TF. 1h is a control (fees about 0.21-0.24 R per trade). 1d gets one declared row (P2).
- Known weakness, stated up front. Label day counts from phase_daily.csv (DEV / VAL): CAPITULATION 85 / 6; ACCUM-RANGE 725 / 156; DISTRIBUTION 543 / 333; MARKDOWN 759 / 199; MARKUP 1119 / 321; RELIEF 253 / 34. P1, P2 and P4 are expected to be UNDERPOWERED on VAL (6 BTC days). They stay primary because the order asks for the cycle-bottom reading. They are reported UNDERPOWERED, never FAIL, never pooled. Report a DEV episode count (a label run per coin, separated by >= 10 days) beside n.
- Disagreement resolved: PHASES wanted CAPITULATION only. CONTEXT, LEVELS and LAYERS used the common-block phase-matched direction. Both kept: P1/P2/P4 are the PHASES cell; P3 and P5 add the two cycle states that have real VAL days.

**Controls (reported separately, never pooled; descriptive, not in the BH family):**

| ID | TF | Description |
|---|---|---|
| C01 | 4h | long DOWN x MARKDOWN V0 (continuation trap) |
| C02 | 4h | short UP x MARKUP V0 (sign symmetry; spec calls MARKUP long-only) |
| C03 | 4h | P1 with the doji filter removed (RSI<30 and close above prior bar high) |
| C04 | 4h | short DOWN x CAPITULATION V0 (opposite of P1) |
| C05 | 4h | mid-trend doji, RSI 40-60, phase-matched direction, any cycle (SOURCED negative, 00:13:04: must not beat P1/P3/P5) |
| C06, C07 | 1h, 15m | P1 |
| C08, C09 | 1h, 15m | P3 |
| C10, C11 | 1h, 15m | P5 |
| C12 | 1d | P3 |
| C13 | 1d | P5 |
| C14 | 4h | P1 with V2 |
| C15, C16 | 4h | P3 with V1, with V2 |
| C17, C18 | 4h | P5 with V1, with V2 |
| C19 | 4h | P1 recovery row: RSI14 crosses back above 30 by the trigger bar (4-OtV5JVM4g 00:06:52 idea) |
| C20 | 4h | P3 with the index: BTC daily close above SMA20 and SMA50 (t1b_1h2QMXw 00:18:13 idea; OURS proxy) |
| C21 | 4h | P1 with funding filter (see Crypto translation) |
| C22 | 1d | P2 with OI flush filter |
| C23 | 4h | short RANGE x ACCUM-RANGE V0 (opposite of P3) |
| C24 | 4h | long UP x DISTRIBUTION V0 (opposite of P5) |

## Context conditions (base signal; bar t is the doji; closed bars only)
1. Doji: |close-open| <= 0.05 x (high-low), high > low. SOURCED (i2bGV_Wo5Yw 00:08:17, "poori body ka 5% se zyada nahi hoga").
2. Range filter: high-low >= 0.5 x ATR14 on the same TF. OURS (one value; removes zero-range bars). The "long-leg" wick test (both wicks >= 30%) is dropped: it adds an OURS parameter and would exclude dragonflies and gravestones.
3. RSI zone: Wilder RSI14 at bar t close < 30 (long) or > 70 (short). Zone SOURCED, but its link to the doji is in an UNQUOTED span (adjacent fragment i2bGV_Wo5Yw 00:09:30). The verdict must say "RSI link not verified". Period 14 is OURS. Code: `MyTradingSys/backtest/layers/rsi/rsi_core.py` (rsi_core, period 14).
4. Prior move: close[t-1] versus close[t-6] is down >= 1.5 x ATR14 (long) or up >= 1.5 x ATR14 (short). OURS (one value); reading of "after a prior up or down move" (00:09:30 fragment, idea only). It gives "ignore a mid-trend doji" (00:13:04, SOURCED) a number; C05 checks it.
5. Trigger: a bar closes beyond the doji high (long) or low (short), within 3 bars of the doji, else the setup expires. SOURCED idea (doji = "waiting", i2bGV_Wo5Yw 00:11:24; confirmation, cX2GZ7B5Gc8 00:10:48); the 3 is OURS.
6. Entry: open of the bar after the trigger close. OURS.
7. R = max(distance to doji extreme, 0.5% of price, 0.6 x ATR14 of the TF); stop = R. OURS (common block).
8. Exit: 2R target or a 10-bar time stop; one fixed row, no variants. OURS.
9. One open position per coin; no new signal while one is open. OURS.
10. Time of day: NK gives none, so no session filter. Session is a descriptive tag only (S rows).
11. Dropped: the "or a level" alternative as a gate (tested only as a split), the CBP lean and the Bible clock as selectors (Context only; they may tag the regime-mix block).

## Crypto translation
- Session open: the 13:30 UTC NY open is a TAG, not a filter, reported as descriptive splits S01-S09 on 4h. Partition by doji bar close time (UTC): NY = closes 16:00 and 20:00; London = closes 08:00 and 12:00; Asia = closes 00:00 and 04:00. No session is chosen. Not applied on 1d.
- Gap: no crypto equivalent; dropped, not ported. NK's "wait" meaning is carried by the confirm-close trigger.
- Funding (C21): last 8h funding print at or before the doji close, from `<local-path>` (cols ts,rate; BTC from 2020-01-01), <= its own trailing-90-day 20th percentile for longs (shorts paying), >= the 80th percentile for shorts. 90 days and 20/80 are OURS. Weak port of "expiry crowding".
- OI (C22, 1d only): OI on the doji day fell versus the prior day (`<SYM>_oi_daily.csv`, cols ts,oi, one value per UTC day stamped 23:59:59.999; BTC from 2020-09-02). OURS and the weakest element. No intraday use (no intraday OI history). Both files verified present for 23 symbols in the nkp1 folder; verify the 20-coin universe at build. Funding/OI cells shrink DEV to 2020 onward.
- BTC market filter: NOT a gate on the primaries (the BTC cycle label already is BTC state, and "BTC not in DOWN" contradicts a counter-trend long). The with-the-index version is C20 only. The Nifty-filter quote is NOT FOUND, so it is OURS.
- Does NOT translate: weekly-expiry pinning and max-pain, stock/sector/breadth rules, the overnight gap, session on 1d.
- Data: OHLCV from the 15m npz files in `<local-path>` (array `a`: t,o,h,l,c,v), resampled to 1h/4h/1d as in `research/nkp1-session-rules-phase-1114_2026-11-14/ctx.py::resample`. `binance_spot_htf` holds only 5 coins and is not used.

## Layer agreement
- **V0:** the base signal alone (conditions 1-9).
- **V1: 1D WaveTrend agrees.** Long: daily WT1 at the last closed UTC day before the doji bar's open <= -53; short >= +53. LazyBear EMA10/EMA21 on hlc3, 200-bar warm-up. Code: `MyTradingSys/backtest/layers/wavetrend/wavetrend.py` (compute, htf_index; OB2 = 53 verified at line 17, SOURCED to the indicator default, not to NK) or the identical availability-stamped layer C2 in `research/nkp1-session-rules-phase-1114_2026-11-14/ctx.py` (has the STUDY_BUG look-ahead switch). For the 1d row, "prior day" is the day before the signal bar.
- **V2: Bollinger %B at the extreme.** %B < 0.10 (long) / > 0.90 (short), SMA20, 2 population sd (cutoffs OURS, brains spec C3). For 15m/1h/4h rows use the 4h %B at the last closed 4h bar at the doji bar close (ctx.py layer C3, availability-stamped). Not run on 1d (no daily %B code). No dedicated BB module exists under backtest/layers; ctx.py C3 is the code path.
- V1 is used in P4 (primary) and C15, C17; V2 only in controls C14, C16, C18. Rejected: rsi_divergence, CVD divergence, candle_patterns (failed earlier). Funding/OI are crypto rows (C21, C22), not layers.
- Each layer gets a future-bar poke test (STUDY_BUG style) in the tests committed with the PRE_REG.

## Level type
- **One primary level: HTF swing S/R from daily bars.** Support S = lowest low of the prior 20 CLOSED daily bars (signal day excluded; for 15m/1h/4h, the last fully closed daily bar as of the doji bar's open). Resistance R = highest high of the same 20. The 20 is OURS.
- **At-level test:** long: doji low <= S x (1 + 0.5 x ATR14/close); short: doji high >= R x (1 - 0.5 x ATR14/close). ATR14 on the signal TF at the doji close. The 0.5 is OURS. A breach of S or R counts as at-level.
- **Away-from-level:** the complement inside the same cell. Level is NOT a filter on the primaries (NK says RSI 30/70 OR a level; the "or" is unverified). It is a descriptive split (L01-L06), not gated.
- Placebo for at-level rows: random same-phase, same-cycle entries that are also at-level (at-level is near-tautological in a falling market).
- Dropped: pivots and prior-day value area (need intraday, fragment the cell), 200-week SMA (single-regime, too few events).

## Timeframes
- 15m and 1h: controls only (C06-C11), covering the "required where expressible" rule. Labels are daily, so intraday rows carry a TF mismatch, reported.
- 4h: primary (P1, P3, P4, P5).
- 1d: native daily row P2 (primary); C12, C13, C22 controls. Weekly: no rows (dojis too rare).

## Cells
Level and session splits are partitions of the primary cells (descriptive, not gated). Controls are not in the BH family.

| Group | IDs | Count | Marked |
|---|---|---|---|
| Primary | P1-P5 | 5 | PRIMARY |
| Controls | C01-C24 | 24 | CONTROL |
| Level splits | L01-L06 = {P1, P3, P5} x {at-level, away} | 6 | CONTROL (descriptive) |
| Session splits | S01-S09 = {P1, P3, P5} x {NY, London, Asia} | 9 | CONTROL (descriptive) |

**Total cells tried: 44. Primary cells: 5.** BH family = the 5 primaries. Every cell reports DEV and VAL n, gross and net R at 12 bp, 6 bp maker, day-cluster CI, ex-best-5, placebo, regime-mix block and the cycle-state tag. A primary PASS needs on VAL: mean net R > 0, trade and day-cluster CI low > 0, ex-best-5 > 0, placebo beaten (placebo alone is not a pass), BH q <= 0.10, n >= 100. Descriptive comparisons: P1 vs C03 (does the doji add anything), P1/P3/P5 vs C05 (mid-trend control).

## Underpowered rule
A cell with n VAL < 100 is UNDERPOWERED, not FAIL, and cannot PASS (this replaces the common block's 200 for this rule, per the order). Episode count (>= 40 independent episodes) is reported beside n for P1, P2, P4. UNDERPOWERED cells are never pooled with neighbours. P1, P2, P4 (6 BTC VAL days) and the 1d rows are expected to land here; that is a finding, not a rule failure.

## Open doubts
- The RSI-to-doji link is in an UNQUOTED span, so the RSI condition is "not verified". The "or a level" reading is only a descriptive split.
- CAPITULATION has 6 VAL days, so the primary cycle-bottom cells are probably untestable on VAL. Only fresh coins (10 unused), longer history, or days since 2026-11-13 run forward give power. DEV was already used by earlier RSI studies, so it is not clean either.
- A 5% body is rare on 1d/4h crypto; n may be small even in ACCUM-RANGE and DISTRIBUTION.
- OURS values, each fixed once and never tuned: range >= 0.5 ATR, prior move 1.5 ATR over 5 bars, trigger within 3 bars, 2R / 10-bar exit, 20-day level with 0.5 ATR band, %B 0.10/0.90, funding 90d 20/80, NY/London/Asia partition.
- No module exists for the coin-day trend phase, daily %B or the doji/trigger logic. They must be built and committed WITH the PRE_REG, with expected numbers computed independently from FORMULAS.md. `MTS_BRAINS_SPEC_1114.md` lives only in side-session notes, not in the repo; the six-row cycle definition was cross-read from the nkp1 PRE_REG line 7 and phases.py.
- The "with the index" tension (NK trades with the index; this rule is counter-trend) is tested only as C20.
- Whether the 1.5 ATR prior move is redundant in DOWN (nearly always true) is untested; it matters mostly in RANGE.
