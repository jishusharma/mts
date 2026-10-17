# CONTEXT FIRST: the market around the operator's 2026-10-16 reads (card confluence-read-encode, 2026-10-17)

Descriptive only. No returns, no event counts as evidence, no backtest run, no pre-registered bar touched, no VALIDATION or HOLDOUT bar read.
Every field names its file or says NOT_IN_DATA. Numbers come from `context_sheet.py` (output in `context_sheet_output.md`).
Files: `OF` = runtime_data/_mirror/MyTradingSys/runtime/orderflow_live/2026-10-16.csv (1m, 1,440 bars); `OI1` = .../runtime/oi_live/oi_1m.csv (1/min REST poll, 1,324 of 1,440 on 10-16); `OI5` = .../runtime/oi_live/oi_5m_30d.csv (5m, 2026-09-13..10-17; the second column is notional, so price proxy px = notional / OI); `CMS` = .../runtime/current_market_state.md (snapshot 2026-10-17 09:55Z); `HTF` = MyTradingSys/research/htf_context/2026-10-16.jsonl. All are the JIS-NB mirror (manifest v20261017T095600Z).

## 0. What was NOT done, and why (defaults taken, logged)
- Step 1 (operator trade log): the coordinator gave no path (the card note was redacted after review finding 1). Default: skipped, nothing read, nothing committed. "Trade days" are taken as 2026-10-16 (the chart in extract c5e7b5c17d90) plus the 2 days before, 10-14 and 10-15. When the path arrives, step 1 needs aggregate counts only (which checklist items were visible at entries and exits), per REVIEW.md 1 and 13.
- The 1m price tape exists only for 10-16 and 10-17 (OF). For 10-14 and 10-15 the only price series is the OI5 implied price (a proxy on 5m samples; its 10-16 high is 82,785 against the true 1m high 82,900.5). The Binance archives on disk end 2026-09-26 (data/tom_raw/klines, data/binance_tf/um). Daily-structure fields for 10-14 and 10-15 are therefore proxy or NOT_IN_DATA.
- OI5 has one data defect: rows with zero notional (dropped by the script, count printed in the output). Any price built from that column must drop them.

## 1. Context sheet

| Field | 10-14 (OI5 proxy) | 10-15 (OI5 proxy) | 10-16 (OF tape) | Source |
|---|---|---|---|---|
| Open / high / low / close | 83,706 / 84,057 / 81,449 / 81,555 | 81,642 / 82,544 / 80,200 / 82,217 | 82,195.3 / 82,900.5 (11:28Z) / 80,780.0 (17:26Z) / 81,578.3 | OI5, OI5, OF |
| Day range | 2,607 | 2,345 | 2,120.5 | OI5, OI5, OF |
| Prior-day high / low / close as the day opened | 10-13 proxy: 84,130 / 82,980 / 83,330 | 10-14 proxy: 84,057 / 81,449 / 81,555 | 10-15 proxy: 82,544 / 80,200 / 82,217 | OI5 |
| Prior-day value area (VAH / VAL / POC) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA for 10-15. CMS PRIOR_DAY, taken on 10-17, is 10-16's own profile: VAH 82,415.39, VAL 81,390.14, POC 82,297.86 | CMS |
| 5-day window ending 10-16 | - | - | high 84,292, low 80,200, range 4,092, drift first row to last row -2,193, OI +0.90% | OI5 |
| 10-day window | - | - | range 4,092, drift -2,619, OI -1.72% | OI5 |
| 14-day (bi-weekly) window | - | - | high 87,060, low 80,200, range 6,860, drift -3,252, OI -2.71% | OI5 |
| Weekly structure | NOT_IN_DATA per day | NOT_IN_DATA per day | CMS WEEKLY (snapshot 10-17): POC 83,422.12, VAH 83,879.91, VAL 81,603.48, shape TWOPEAK; prior-week POC 83,007.82; two-weeks-ago POC 84,784.76. The 10-16 close 81,578 sits below the weekly VAL | CMS |
| Macro phase | decline from the 09-21/22 high (OI5 proxy 87,255) to the 10-15 low 80,200; closes 10-13..10-16: 83,330 / 81,555 / 82,217 / 81,578 | same | CMS STATE classification trend_healthy on 10-17 (a live label, not a phase study) | OI5, CMS |
| Speed: range per hour | proxy day range / 24 = 109 | 98 | 1m tape: median hour 401.4, max hour 1,312.1 (17:00Z, the spike hour) | OI5 (5m samples under-state range, not comparable to OF), OF |
| Speed vs the recent norm | day range 2,607 | 2,345 | 2,120.5 (OF) / 1,980 (OI5 proxy): smaller than 10-14 and 10-15 on the same proxy; 09-21 and 09-18 were 6,344 and 4,997 | OI5 |
| OI trend on the day | +1.23% (91,994 -> 93,122) | +1.37% (93,117 -> 94,396) | -0.10% (94,395 -> 94,305); OI1 first 94,162, max 95,793, min 93,658 | OI5, OI1 |
| Sentiment: funding | NOT_IN_DATA (no history) | NOT_IN_DATA (no history) | NOT_IN_DATA (no history); CMS FUNDING on 10-17 09:55Z: rate 2.739e-05, extreme False | CMS |
| Sentiment: long/short ratio, liquidations | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA (no heatmap or liquidation file; heatmap_field_map.md is a field map only) | - |
| Sentiment: spot-perp basis | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA for the day; CMS SPOT_PERP on 10-17: basis -0.04%, discount | CMS |
| Absorption / distribution: CVD vs price | NOT_IN_DATA (no delta) | NOT_IN_DATA (no delta) | Day: price -617 (82,195 -> 81,578) while cvd_day ended +3,463; 11 of 24 hours have price change and delta of opposite sign (table in the output). Hours 17-19Z: delta +2,938 / +176 / +1,681 with hourly price change -220 / -68 / +440 | OF |
| OI vs price | OI5 only (see above) | OI5 only | Price down on the day with OI flat (-0.10%); OI fell about 0.7% across the 17:34Z bar (OI1: 95,256 at 17:33:57, 94,567 at 17:34:55) | OI5, OI1 |
| Session frame | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA (OF is 00:00-23:59Z; no session-frame file for the day) | - |

## 2. The operator's claims against the tape (checkable from OF and OI1; no outcome measured)
| Claim (extract c5e7b5c17d90) | What the files say | Source |
|---|---|---|
| Top 82,896-82,900 | 1m high 82,900.5 at 11:28Z. Ray 3 (82,900.5) equals the day high to the tick | OF |
| Low near 80,700-80,800 before the spike | 1m low 80,780.0 at 17:26Z, 8 minutes before the spike bar | OF |
| Spike bar near 17:30-17:35, volume spike, CVD step, OI fall, wick up to about 82,100 | Largest-volume 1m bar of the day is 17:34Z: 6,264 BTC, delta +3,105.2, high 82,092.1, low 81,040.9. OI fell 95,256 -> 94,567 -> 94,457 around it (OI1 polls, not candles) | OF, OI1 |
| Ray 1 (81,800) swept by the spike | The 82,092.1 wick is above ray 1 and below ray 2 (82,459.8), so ray 2 was not reached by the spike. Ray 1 sits inside the day's range (price opened at 82,195, so the first 1m high above it is 00:00Z) | OF |
| Ray 2 (82,459.8) retest "repeats the story" | First 1m high at or above 82,459.8 is 01:16Z; the retest time is not given | OF |
| Rejection near 12:34Z | The 12:34Z bar is 82,348.5 / 82,390.1 / 82,343.8 / 82,390.1 on 96.9 BTC: a small bar. Hour 12 fell 590 with delta -933 | OF |
| Big green candle near 14:47Z | 14:47Z bar: O 82,278.1 C 82,368.8, 235.1 BTC, delta +80.7, body +90.7. The largest green 1m body in hour 14 is 14:11Z (+129.4) | OF |
| RSI divergence, Bollinger dance, RSI 40/60, StochRSI | NOT_IN_DATA: no 1m band or RSI series is stored for the day. They can be built from OF closes; that computes the signal itself, so it is deferred | - |

Observation for the operator (not a finding): ray 3 equals the day high exactly. A ray drawn after the day shows a level the day already respected; one drawn at 17:00Z would have been unknown at the time. Whether the rays were drawn live or after is a question below.

## 3. Context machinery that exists, and what it says for these days
| Machinery | What it covers | For 10-14..10-16 |
|---|---|---|
| `research/context_factors_pit_2026-10-16/context_asof.py` (87 point-in-time fields: side-aware levels, daily ladder, weekly phase, ATR, pivots, profile) | DEV only: bars 2022-01-01..2024-06-30; the loader refuses later bars (`test_loader_refuses_validation_bars`) | Says nothing: 2026-10 is outside DEV and beyond the archive on this host. It cannot run on these days without opening data past DEV |
| `pit_levels` (VERDICTS row pit_levels_2026-10-16) | prior-day value-area failed auction | BLOCKED by the power gate, n=0; no output for these days |
| `htf_context` jsonl (HTF) | 4-hourly: bal_1d, bal_4h, failed_breakout, oi_delta_1h_pct | 10-16 has 6 rows; bal_1d, bal_4h and failed_breakout are null in all 6; oi_delta_1h_pct runs -0.54..+0.64 |
| `runtime/alerts/*.jsonl` (1m, 5m, 15m, 1h) | RSI event alerts (cross, rejection at 40/60) per timeframe | Present in the mirror but the rows read carry null rsi and rsi_ma; not mapped to 10-16 here |
| CMS (live state card) | weekly, daily, prior-day profile, VWAP, funding, CVD, basis | One snapshot at 10-17 09:55Z. No history, so it cannot give the state at an operator entry |

Gaps as feature hypotheses (all OURS, none tested):
1. Weekly and bi-weekly profile as of the decision bar (point-in-time), not the latest snapshot.
2. Speed = range per hour divided by the trailing 5-day median range per hour, on closed bars.
3. Rolling price-vs-CVD opposition as an absorption proxy; the same for price vs OI.
4. Funding and basis history (not stored: needs a recorder, a build card).
5. Multi-timeframe band-dance state (checklist item 10) built from the 1m close series.
6. Distance to the nearest level defined only from levels known before the bar (prior-day, weekly, naked POCs in runtime_data/_mirror/runtime_data/naked_pocs).

## 4. Diagnosis of the backtest apparatus (no new numbers; existing files only)
The ten cards `dsa-audit-01..10` are all STATE ready (not run), so none has produced a finding yet. What already explains "nothing works", from reports that exist:

| Cause | Evidence on disk | Fits "everywhere on the chart, nothing in the test" |
|---|---|---|
| Frame mismatch: tests use fixed horizons (h=60/120) and one filter; the operator reads a sequence over several timeframes and exits by discretion | REVIEW.md 14(i),(iii); VERDICTS rows mal_bb_mid_engulf (5m, h=60), opr_bb_mtf_center (1h, h=120) | Strongest: a rule that encodes the sequence is a different object |
| Cost against small gross | VERDICTS cost_pct 0.14 on the screens; AUDIT_MAJOR_GAPS_2026-10-09 B146 (tiny stops dominated by fees) | Yes for any 1m idea at 20-50x (REVIEW.md 13) |
| Power: small n or an MDE above any plausible effect | VERDICTS wlow_bounce n=8; pit_levels BLOCKED n=0; backtest_gap_review_2026-10-13 G1 | Yes for rare sequences |
| Hindsight selection: setups seen after the fact, thresholds fitted to a known day | REVIEW.md 12 | Applies to any encoding of the 10-16 sequence |
| No planted-edge canary for the simulators | dsa_backtest_audit AUDIT_BRIEF section 2 (mts_flow_audit 6a: none was ever filed); card dsa-audit-03 not run | Unknown: until a known edge is recovered, a FAIL cannot be trusted |
| Known open apparatus defects | AUDIT_BRIEF section 2: through_ticks not passed (tom_bt.py:228); orderflow_views books gaps through the stop at the stop price (N2); chart_lab minute-open labels (N3); screen.py:259-267 overwrites DATA_MANIFEST; eight split schemes with no shared module | Partly: they bias results, mostly not toward zero |
| Context absent from the tests | checklist items 13-14; the one context test is VERDICTS row context_factors_2026-10-16 (composite C, verdict row only, not used as evidence here) | This card's subject |
| Data seams | OI history is a snapshot poll with gaps (1,324 of 1,440 on 10-16) plus the zero-notional defect in OI5; CoinGlass OI and CVD candles are not stored | Blocks any OI/CVD test at the operator's resolution |

Canary status: look-ahead canaries PASS (7 planted leaks all caught, context_factors_pit_2026-10-16/test_context_asof.py, per CONTEXT_FACTORS_SPEC.md). Planted-edge canary for the event-study simulators: NOT PRESENT. Clean-room twin: NOT RUN (dsa-audit-04 ready). I ran none of them here.

Before any later test (card step 6): rules written blind to 10-16 prices; 10-16 used only as a unit test that a counter fires; count families (band, RSI, flow, levels), not items; list prior VERDICTS rows (above); cost at 20-50x; every variant in the trial ledger; state events per month and MDE first.

## 5. Questions for the operator (default in brackets if no answer comes)
1. Were the three rays drawn live (before 17:34Z) or after the day? [after; use only levels known at the bar]
2. Which of your trades on 10-14, 10-15, 10-16 count as "taken on this setup"? Aggregate counts only (checklist items visible at entry and exit), no times, prices or PnL. [step 1 stays skipped]
3. Does "yesterday" mean the UTC day or a session day (Asia, EU, US)? [UTC day, as CMS PRIOR_DAY]
4. For "speed": range per hour above the recent norm, or the speed of the last leg into the level? [range per hour vs the trailing 5-day median]
5. Is sentiment funding, long/short ratio, liquidations, or your own read of the tape? None of the first three is stored as history. [build a recorder only if you rank it above the rest]
6. Absorption and distribution: price flat while CVD rises, price rising while CVD falls; over the last 5 bars or the last hour? [rolling 60 one-minute bars, OURS]
7. Which horizon decides a trade for you first: weekly or bi-weekly structure, or the day's profile? [weekly, then prior day, then 5-day]
8. Do you accept an "events per month and MDE" statement before any test, and that a pattern with too few events is reported as untestable rather than as a fail? [yes]
9. Order of work after this reading: (a) record funding, long/short, liquidations; (b) build point-in-time context fields for 2025-2026 bars (needs your OK to open data past DEV); (c) run the dsa-audit canaries first? [c, then a]

Stop here. A pre-registered test comes only after the operator has read this.
