# NKN-04 context design (frozen before results)
Frozen 2026-11-14. No backtest, no outcome data read. Every OURS parameter has one value, no grid. The common block of NK55_RULES_1114.md Part 2 applies unless a line below says DEVIATION.

## Resolutions of the angle disagreements (read first)
| Issue | Angles said | Frozen |
|---|---|---|
| Direction vs phase | Draft: "long in DOWN at support, short in UP at resistance". The geometry contradicts it: in a DOWN phase price sits below a falling SMA20 and meets it from below (resistance), so the fade is a SHORT. | Direction = approach side (from below = short, from above = long). Primary cells are the weak rally in a downtrend (short) and the dip to support in an uptrend (long). The draft's literal counter-phase mapping becomes CONTROLS. DEVIATION from the draft. |
| Phase / cycle definition | PHASES invented a MARKDOWN formula. | Use what exists: coin-day phase UP/DOWN/RANGE from the common block, and the BTC cycle label from `F:\MTS\data_cache\mts_brains\phase_daily.csv` (`label` column: MARKUP, MARKDOWN, ACCUM-RANGE, DISTRIBUTION, RELIEF, CAPITULATION; lag 1, per `research/nkp2-levels-phase-1114_2026-11-14/mts_phase.py`). No invented formula. Alts use BTC's label. |
| Touch band | Draft 0.3% fixed vs LEVELS 0.5 x ATRd | ATR band (coin-invariant). The 0.3% is dropped. |
| Failed 1h pattern (C5) | CONTEXT: mandatory. Draft and LAYERS: optional. | NK gives no definition of the pattern, so a mandatory gate would be invented. Kept as a CONTROL split with one definition (below). Open doubt. |
| Confirmation | CONTEXT: options half not portable | HM red-line gate on 15m only (role SOURCED, formula OURS), flagged. |
| Stop floor | Draft 0.5% / 0.6 ATR vs CRYPTO postmortem 1.2% / 1.0 ATR | DEVIATION: R = max(structural, 1.2%, 1.0 x ATR14 of 15m). Reason: fee/R at 12 bp is 0.24 with a 0.5% floor. I could not read the postmortem, so this rests on the CRYPTO designer's citation. Open doubt. |
| 5m row | Draft had it | Dropped (stops cannot beat fees at that scale). 10m (NK's named TF) is not in the data: omitted, stated. |
| V2 layer | LAYERS: daily WT1 >= +53 | Dropped: a rally in a DOWN phase rarely reaches WT1 +53, so the cell would be empty by construction. V2 uses 4h RSI instead. |
| Session filter 07-21 UTC, funding gate, OI 3% gate | CRYPTO optional | Dropped as cells (cell count). Funding and OI are logged columns only, never gates. |

## Phase tested
**Primary cell A (SHORT):** coin-day phase = DOWN AND BTC cycle label = MARKDOWN, price approaching the daily SMA20 from below.
**Primary cell B (LONG):** coin-day phase = UP AND BTC cycle label = MARKUP, price approaching the daily SMA20 from above.
Phase per coin-day is known at the prior daily close (common block: 20-day MA slope with 5-day lag plus ADX14 >= 20 with DI direction, else RANGE). The AND with the cycle label is deliberate: the 11-14 studies showed phase alone does not carry a rule.
**Control cells (reported separately, never pooled):**
- C1 short, DOWN phase, BTC label not MARKDOWN. C2 long, UP phase, BTC label not MARKUP (does the cycle matter?).
- C3 short, UP phase x MARKUP (the draft's literal counter-phase). C4 long, DOWN phase x MARKDOWN.
- C5 short in RANGE (approach from below), C6 long in RANGE (approach from above), any label. Descriptive.
- Away-level complement of each primary (below).
- Placebo for each primary: random entries, same phase x label, matched hour-of-day mix (gate component, not a cell).

## Context conditions (evaluated in this order, all on closed bars)
1. HTF level = daily SMA20 (SOURCED: cX2GZ7B5Gc8 00:02:40). Weekly SMA20 only as a confluence flag (idea SOURCED: cX2GZ7B5Gc8 00:06:43).
2. Level value L = mean of the last 20 CLOSED UTC daily bars (through the prior day). Constant all day. Weekly: last completed week only. (OURS construction, no look-ahead.)
3. Phase cell and BTC label as above; labels for day d use data through d-1 (OURS definitions, one value).
4. Approach side: the 15m close 8 bars (2h) before the trigger bar is below L (short) or above L (long). 2h = OURS. The idea is SOURCED (price rising into the SMA20), with no verbatim quote.
5. At-level: within the 8 bars up to and including the trigger bar, short: bar high >= L - 0.5 x ATRd and trigger close < L + 0.25 x ATRd; long is the mirror. ATRd = ATR14 on closed daily bars. 0.5 and 0.25 = OURS.
6. Trigger: the 15m close crosses below (short) or above (long) its own 15m SMA20, prior bar on the other side, against the prior 2h move (sign of close[t-1] minus close[t-9] opposite to the trade). SOURCED idea (cX2GZ7B5Gc8 00:13:21; he names 5/10/15 min); 2h OURS.
7. Confirmation gate: HM(9,3,21) on 15m at the trigger bar. Short needs HM not bullish, long needs HM not bearish. Role SOURCED (cX2GZ7B5Gc8 00:10:48, 00:16:00: a close alone is not enough); formula OURS = RSI9 with EMA3 vs WMA21, unverified against his chart. Gate only, never a trigger.
8. Entry at the next 15m bar open. Stop and exit: R = max(structural beyond the 8-bar extreme, 1.2%, 1.0 x ATR14 15m); half at 2R; runner trailed under each candle low (OURS, UNQUOTED); also two 15m closes through L exit (OURS). Gap-through fills at the bar open, not at the level. Fee 12 bp round trip charged on entry plus exit notional; 6 bp maker as a non-gating row. Regime labels per coin-day, not per 1h bar.
9. Failed-pattern split (FP, control only): in the last 8 bars a 1h close was beyond L (through the level) and the trigger close is back on the approach side. One definition, OURS.
10. Weekly confluence flag (control split): weekly SMA20 within 0.5 x ATRd of the daily SMA20.
11. Omitted by design: gap, time-of-day, index filter (NK's belong to NKN-03 and NK-R04). Listed as a known weakness.

## Crypto translation
- Session open: none used. Day boundary = 00:00 UTC for the daily bar, 7-day weekly bar matching the phase table.
- Gap replacement: none (dropped, nothing replaces it).
- Funding: `<local-path>` exists (8h). Logged column only. The BTC file tail row (rate 0.0001 at about 2026-10-31) looks like a placeholder, so no funding gate.
- OI: `<SYM>_oi_daily.csv`, one value per UTC day from 2020-09-02, not intraday. Logged column only (prior-day change), never a gate.
- BTC market filter: expressed through the BTC cycle label (phase_daily.csv) in the cell definition. Not a separate filter.
- Does NOT translate: options-chart confirmation, Nifty trend gate as a gate, weekly expiry, gap, 5m and 10m triggers.

## Layer agreement (max 3 variants, all closed-bar, applied to the same trigger)
Verified to exist: `research/nkp2-levels-phase-1114_2026-11-14/ctxlib.py` has `resample`, `wilder_rsi`, `bollinger_pb`, `wavetrend1`, `_htf_index`; `F:\MTS\data_cache\mts_brains\phase_daily.csv`.
- **V0 rule alone** (conditions 1-8).
- **V1 = V0 + 4h Bollinger %B** (`ctxlib.bollinger_pb`, n=20) at the last CLOSED 4h bar before the trigger bar. Short needs %B >= 0.90, long needs %B <= 0.10 (OURS cutoffs; period SOURCED to SPEC C3). The 4h index for a 15m trigger = the bar whose end is <= the trigger-bar open. This indexing is NEW code (`_htf_index` is 1h-based) and needs a future-bar-poke test. The `STUDY_BUG` env var must be unset (BUG=2 is a deliberate look-ahead switch).
- **V2 = V1 + 4h RSI(14)** (`ctxlib.wilder_rsi`) at the same bar. Short needs >= 55, long needs <= 45 (OURS). The Malkan 40/60 constants are private to `backtest/layers/rsi/malkan_40_60.py` per rule D2, so they are not imported.
- Dropped: daily WaveTrend (exists, golden test at `backtest/layers/wavetrend/test_wavetrend.py`, but its +/-53 level conflicts with the DOWN-phase geometry), funding/OI layers, taker delta.

## Level type
Primary: the daily SMA20 (the only level NK names for this rule). At-level test = condition 5. Away-from-level complement: same trigger, HM gate, phase cell, but the nearest approach over the 8 bars stayed more than 0.5 x ATRd from L. The question it answers: does at-level beat away-level in the same cell? Descriptive only: "far" (> 1.5 x ATRd). The weekly SMA20 is a flag only.

## Timeframes
- 15m: trigger, HM, entry (all verdict cells).
- 1h: failed-pattern split (FP) only.
- 4h: %B and RSI for V1/V2.
- Native daily: level, ATRd, phase. Native weekly: confluence flag only.
- 5m dropped, 10m not available. Data: `<local-path>` (26 coins, key `a`, columns t,o,h,l,c,v; BTC 2019-01 to 2026-11). Daily, weekly, 4h and 1h are built by resampling the 15m file to UTC bars.

## Cells
Every cell: 15m trigger, HM gate on. "at" = at-level, "away" = away-level.
| # | Phase x BTC label | Side | Variant | Level | Role |
|---|---|---|---|---|---|
| 1 | DOWN x MARKDOWN | short | V0 | at | PRIMARY |
| 2 | DOWN x MARKDOWN | short | V1 | at | PRIMARY |
| 3 | DOWN x MARKDOWN | short | V2 | at | PRIMARY |
| 4 | UP x MARKUP | long | V0 | at | PRIMARY |
| 5 | UP x MARKUP | long | V1 | at | PRIMARY |
| 6 | UP x MARKUP | long | V2 | at | PRIMARY |
| 7-12 | same as 1-6 | | V0, V1, V2 | away | CONTROL |
| 13 | DOWN x not-MARKDOWN | short | V0 | at | CONTROL C1 |
| 14 | UP x not-MARKUP | long | V0 | at | CONTROL C2 |
| 15 | UP x MARKUP | short | V0 | at | CONTROL C3 |
| 16 | DOWN x MARKDOWN | long | V0 | at | CONTROL C4 |
| 17 | RANGE x any | short | V0 | at | CONTROL C5 |
| 18 | RANGE x any | long | V0 | at | CONTROL C6 |
| 19 | cell 1 with FP split | short | V0 | at | CONTROL |
| 20 | cell 4 with FP split | long | V0 | at | CONTROL |
| 21 | cell 1 with weekly-confluence flag | short | V0 | at | CONTROL |
| 22 | cell 4 with weekly-confluence flag | long | V0 | at | CONTROL |

**Total cells tried: 22. Primary cells: 6.** Benjamini-Hochberg runs over the 6 primaries (family m = 6). The 16 controls are reported separately, never pooled, and never used to rescue a primary. Placebo rows (6, one per primary) are gate components, not cells.
Splits: DEV <= 2023-12-31, VAL >= 2024-01-01. Cells are frozen and committed with the code and PRE_REG before VAL is read. The confirmation set (10 fresh coins plus days since 2026-11-13) runs once. Gates per the common block: mean net R > 0, trade-level and day-cluster CI low > 0, ex-best-5 > 0, placebo beaten, BH q <= 0.10, plus a planted-edge unit test and a future-bar-poke test on every level and layer. Run `scripts/dev/prereg_gate.py` first (exists); BLOCK = do not run. Report episodes (coin-days with a trigger) next to trades and de-overlap trades.

## Underpowered rule
A cell with n VAL < 100 trades is UNDERPOWERED, not FAIL, and cannot PASS. n VAL 100-199 is reported with its CI and labelled THIN (cannot PASS, per the common block's 200 requirement). Compute event counts on DEV signal dates only, before any outcome is read; if a primary is UNDERPOWERED up front, say so before the run. Expect V2 and the confluence/FP controls to be UNDERPOWERED.

## Open doubts
1. The FP definition is mine; NK defines no "pattern". Mandatory vs control is unsettled.
2. HM implementation: not in this worktree (the nkp3 code lives in a sibling tree; no HM def found here). It must be imported from there or re-written, and stays flagged OURS/unverified.
3. The `nkp4` shared simulator (`simulate` + `stats.py`) named by CRYPTO does not exist in this tree or in `mts_brains/nkp4` (empty dir; the only `stats.py` found is the unrelated `options/backtest/stats.py`). The study must ship its own simulator with the planted-edge test.
4. The 1.2% stop floor rests on a postmortem I could not read.
5. Fresh coins: `<local-path>` holds only 8 coins outside the 26 (AAVE, ENJ, GRT, HBAR, MANA, SAND, THETA, XTZ). 10 are required, so 2 more must be fetched or the set stated as 8.
6. The 2h window, ATR 0.5/0.25, %B 0.9/0.1, RSI 55/45 and the 8-bar lookback are all OURS and untuned. Cell A may be thin (DOWN x MARKDOWN is a minority of days; VAL DOWN share 35%).
7. phase_daily.csv has 1400 blank labels (early history); those days are excluded, not defaulted.
8. Prior failures (0 of about 100 rows) make FAIL the honest prior. The value of this design is whether context separates at-level from away-level.
