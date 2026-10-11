# FINDINGS LOG (report -> audit -> fix)

Operator rule 2026-10-09: whenever an observation is off or wrong, write a report, audit it, then fix it.
Every worker appends here when it sees something wrong. One entry per finding. Status moves REPORTED -> AUDITED -> FIXED
(or ESCALATED when the fix is a live-path file, an operator decision, or needs a tuned number first).

Template (copy):
```
## F-BT-NN  <one line>   [SEVERITY]  status: REPORTED | AUDITED | FIXED | ESCALATED | NOT-A-DEFECT
Found by: <session/worker>, <date>. Report: what was seen, with file:line or command and the numbers.
Audit: independent check (script or second read), what it confirmed or refuted, other instances searched for.
Fix: what changed (file, test that failed before the fix) or why not done and who decides.
```
Live-path files (MyTradingSys/execution/, layers/alerts/, anything auto_trader, position_manager, daily_loss_monitor or
live_runner_cli import, the Java producer) are never edited in place: stage `<file>.new` + a fail-first test, status ESCALATED,
supervisor promotes.

## F-BT-01  Stop floor removal left degenerate stops; R:R and the net R:R gate are distorted   [HIGH]  status: AUDITED, ESCALATED (fix needs a tuned number first)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt, 2026-10-09, while answering the AUDIT_CLOSEOUT "19 -> 0 SETUP_FORMING" open item.
Report: `python scripts/dev/diff_tom_rows.py F:/MTS/data/tom_bt F:/MTS/data/tom_bt_2026-10-07` (old run vs current Java) plus a join on t
of the 19 old SETUP_FORMING rows. Stop distance as a share of price, month 2025-07: OLD median 0.245 %, share under 0.10 % = 10 %;
NEW median 0.084 %, share under 0.10 % = 56 %, minimum 0.0000 %. Examples (same instant, same zone): 2025-07-02 short at weekly_vah, stop
107983 -> 107785 (0.234 % -> 0.049 %), gross_rr 3.34 -> 118.86, net_rr 2.51 -> 15.29 (verdict WATCH); 2025-11 short at vwap gross_rr 3.25 -> 50.42;
2024-09 short stop 0.0011 % from price (54114.9 vs 54114.3), gross_rr 0.47. Targets also moved further out (0.64 % -> 1.84 %, 0.62 % -> 4.11 %).
Audit (19 rows, all joined): 7 of 19 old SETUP_FORMING instants have no row at all in the new run (candidate no longer generated);
12 remain with proof 5 -> 1..4 (one proof point lost; PR #12 set book_imbalance to null) and verdict WATCH / WAIT_PROOF / WAIT_RR / WAIT_TRIGGER.
So the live-rule drop 19 -> 0 has three causes: candidates gone (7), proof ceiling lower (12), and R:R no longer comparable because the
stop is at the zone edge plus a few ticks. A stop that tight is hit by one 1m wick; R is tiny so fees cost ~2.76 R per trade (TOM_CORE_BT_RERUN).
The net R:R floor (net_rr_floor.json, 1.25) now passes degenerate setups (net_rr 15..22) and the same Java feeds the live producer.
Fix: not done here. The floor (0.1 %, B116) was NO-SOURCE and its removal was an operator ruling, so the stop must come from the trader's rule
plus a noise buffer, and the buffer needs a number. Plan: backtest D tunes `stop_buffer_atr` (stop = structure level +/- k x ATR(TF)) for Tom
core and every tight-stop layer, label BT-TUNED, report fee_R = round-trip fee / stop distance for every cell. Then a staged
SetupCandidatesBuilder `.new` with a fail-first test (stop distance never below the tuned buffer). Supervisor promotes.

## F-BT-02  turn_of_candle FAILED T055 C3 (closed) yet is 79 % of live testnet trades   [MEDIUM]  status: AUDITED, ESCALATED (operator decision)
Found by: same session. Report: T055_BT_c3.md "NO EDGE (FAIL) ... No alert-only live sampling warranted"; auto_trades.jsonl 2026-09-28..10-08 joined
trade_closed.source to ledger_row.net_pnl_usd: turn_of_candle:1m 262 closed, 29 wins, net -3.02 USD, exits 262/262 time_exit; all layers 333 closed,
time_exit ~97 %, target/stop 6. Only rsi_events:1h reaches targets (3 trades, 3 wins, +9.75 USD).
Audit: ledger numbers recomputed from the file (not from a report). Possible intent: testnet volume generator (side + sampling promoted 7058bc2),
which would make this deliberate, but the 1m ToC stream drowns every other layer's sample (333 trades, 8 sources) and no document records that intent.
Fix: none by this session (live path, operator's call). Backtest C re-tests ToC with real fires and ride exits; if no config shows a net edge the
recommendation to the supervisor is to remove it from the auto_trader layer map or cap its slot share. Needs operator yes/no on "keep as volume generator".

## F-BT-03  PENDING_BACKTEST_AUDIT.md still said NOT DONE   [LOW]  status: FIXED
Report: header "Status: NOT DONE" while BACKTEST_METHOD_2026-09-21.md exists (a draft written from dispatch excerpts, no commands run, 10 open questions).
Audit: file exists, 67 lines, says so itself ("Draft written from dispatch excerpts only; no commands run").
Fix: header rewritten to DELIVERED-AS-DRAFT, SUPERSEDED by research/bigtrade_2026-10-09/PLAN.md. No other content changed.

## F-BT-04  Two suspected data problems checked, both clear   [INFO]  status: NOT-A-DEFECT
- OI change_1h_pct flat 0.0 (B136): last 200 snapshots, 0 flat, latest -0.22 with delta_state rekt_short. Fixed upstream.
- orderflow_live recorder stall (missed-trades ROADMAP step 5): 2026-10-04..10-08 CSVs have 1440 rows per full day, 0 gaps over 1 minute, 10-08 live to 19:33Z.
Do not re-audit unless a new gap appears.

## F-BT-05  308 zero-volume flat 1m bars in the kline archive (8 dates)   [LOW]  status: AUDITED
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker A (bigmoves), 2026-10-09. Report: loading Dumps/backtest/raw_1m_2022/klines with
bt_data.load_klines and counting v == 0: 308 bars, all with O=H=L=C, on 2022-05-01 (29), 2022-05-28 (35), 2023-09-12 (19), 2023-11-10 (99),
2024-10-28 (89), 2025-01-14 (2), 2025-01-29 (17), 2025-08-29 (18). None in Dumps/backtest/raw (2025-09..2026-10-07).
Audit: all 308 are flat (not just zero volume); the same 308 are in F:/MTS/data/tom_raw/klines. A scan of 2,507,040 merged bars found 0 OHLC
inconsistencies (high < max(o,c,l), low > min(o,c,h), price <= 0) and 0 missing minutes. These are exchange-maintenance fills at the prior close.
Fix: none needed in the data. The ground-truth build keeps them (removing them would create time gaps) and counts TF bars made only of such
minutes (see BIGMOVES_REPORT.md). Any layer that treats a zero-range bar as a signal must be checked for it.

## F-BT-06  Duplicate kline files; tom_raw does not extend coverage   [INFO]  status: NOT-A-DEFECT
Found by: same worker, same day. Report: Dumps/backtest/raw/klines holds daily files BTCUSDT-1m-2025-09-01..07.csv AND the monthly
BTCUSDT-1m-2025-09.csv (10,080 overlapping rows). F:/MTS/data/tom_raw/klines (89 files) was checked for extra coverage.
Audit: overlap rows compared field by field: 10,080 overlapping, 0 differing, so bt_data.load_klines "keep first" is safe. tom_raw has 2,491,200
bars 2022-01-01..2026-09-26, every one present in the main set with identical o/h/l/c/v (0 missing, 0 conflicting): it is a subset and adds nothing.
Merged coverage = 2022-01-01 00:00Z .. 2026-10-07 23:59Z, 2,507,040 bars (= 1,741 days x 1440), no gaps.
Fix: none.

## F-BT-07  ATR definition differs between the big-trade PLAN (Wilder) and MTS core (plain SMA)   [LOW]  status: AUDITED
Found by: same worker, same day. Report: PLAN.md section 3 says ATR(14) Wilder; FORMULAS.md section 12 records an operator decision (2026-09-28)
that MTS core ATR (SetupCandidatesBuilder.averageTrueRange) is a plain SMA of TR and must not be turned into Wilder. Fire files whose
stop_dist_atr was produced by core code would then be in SMA-ATR units while legs and forward labels from bigmoves.py are in Wilder units.
Audit: SMA(14)/Wilder(14) ATR ratio measured on all closed bars 2022-01..2026-10 (bigmoves_stats.json): 4h p5/p50/p95 = 0.768/0.989/1.188, 1h 0.751/0.984/1.212,
15m 0.783/0.972/1.216, 5m 0.810/0.975/1.198. Medians are close, but a single bar differs by up to about +-20 %, so stop_dist_atr in SMA units is not Wilder units.
bigmoves.py stores both (labels_*.csv atr_wilder, atr_sma). Other instances: B1 fire files carry their own `atr` and `stop_dist_atr` columns without an atr_kind column.
Fix: not a defect in the data; a unit rule. Status AUDITED. Rule used by capture.py: fee_R is computed from stop_dist_atr x ATR of the SAME kind as the file states in the `atr_kind` column
(default wilder); a fire file without that column is assumed Wilder and the report says so.

## F-BT-08  No big-move ground truth for 1m, so turn_of_candle (79 % of live trades) cannot be scored   [MEDIUM]  status: REPORTED
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker A, 2026-10-09. Report: CAPTURE_MATRIX run on F:/MTS/data/bigtrade/fires: the two groups
layer:turn_of_candle:turn_of_candle:1m (long 83,927 and short 83,180 fire rows) are listed under "no ground truth" because legs_1m / labels_1m were not built
(PLAN and the worker brief list 5m/15m/1h/4h). All other 18 fire files were scored.
Audit: capture.py skips a group only when its tf has no legs_<tf>.csv + labels_<tf>.csv; bigmoves.py accepts tf "1m" (TF_MS has it), so the gap is a build
decision, not a code limit. Estimated cost: about 10 minutes and a ~250 MB labels file.
Fix: pending a supervisor yes: `python -B -m MyTradingSys.backtest.bigtrade.bigmoves --tfs 1m`, then rerun capture.py. Needed for F-BT-02 (ToC side study).

## F-BT-09  Java volume profile (buildVp) does not conserve volume: POC/VAH/VAL biased to fast-move bars, 300-690 points off the trade-level POC   [HIGH]  status: AUDITED, ESCALATED (Java producer = live path)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: the operator's POC rays (24-row fixed-range profile, screenshots C04-C07) disagree with the snapshot: 10-05 14:53 chart ~86,27x vs daily_vp.poc 85,519.2; 10-06 chart ~85.57K vs prior_day.poc 86,269.35 (trade-level 85,580, +689); 10-07 21:13 chart ~83.33K vs daily_vp.poc 83,702.35 (trade-level 83,400, +302); 10-04 chart ~85,246 vs prior_day.poc 86,574.75 (+575 vs trade-level 86,000). Cause, src/main/java/datafeed/MarketDataSnapshot.java buildVp (lines ~548-560): each 1m bar spreads its volume over n=max(1,(high-low)/bin) points with weight 1-|p-tp|/halfRange and the weights are not normalised, so a bar adds ~vol*n/2: the profile weight sum is 6.69x / 8.43x / 6.33x / 11.07x the real volume on 10-04..10-07, wide-range (fast) minutes weigh up to ~30x a quiet one, and a single-bin bar with tp above mid-range gets weight 0 (1.2 % of 10-06 volume dropped).
Audit: MyTradingSys/backtest/bigtrade/obs_vp_check.py re-implements buildVp and reproduces all four Java POCs exactly (86574.75, 85510.32, 86269.35, 83702.35; 10-07 VAH/VAL 84062.77/83081.63 also exact). With per-bar weights normalised the POC becomes 85,162.9 / 85,510.3 / 85,538.3 / 83,407.0 against the trade-level $10 POC from orderflow_live fp 86,000 / 85,500 / 85,580 / 83,400: error Java +575 / +10 / +689 / +302, normalised -837 / +10 / -42 / +7 (10-04 profile is bimodal 85.25K / 86.0K). The same function feeds weekly, prior-week, 4h, post-funding and prior-day profiles, so every POC/VAH/VAL/HVN/LVN zone Tom reads is affected. Latent: a bar with high==low gives 0/0 = NaN weight; none in 2026 klines (scan 2026-01..10-07), F-BT-05 covers the archive.
Fix: not done, live path. Spec for the supervisor: in buildVp divide each bar's weights by their sum (put the whole volume on the tp bin when the sum is 0); acceptance test over the 2026-10-06 and 2026-10-07 1m files: POC within 50 of 85,580 and 83,400. Tom backtests that used VP zones need a re-run after the change.

## F-BT-10  Snapshot open_interest.* is hourly-stepped; invisible to the 1m/5m OI flush the operator describes   [MEDIUM]  status: AUDITED, ESCALATED (design, Java producer)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: open_interest comes from openInterestHist period 1h (MarketDataSnapshot.oiFromHistory, last two hourly points) and changes once an hour: 2026-10-07 has 25 distinct change_1h_pct values in 1,373 snapshots, median 59.995 min between updates, max 61.0. Example: 01:02-02:02 frozen at -0.05 flat/neutral across the 01:50-02:05 crash (85,276 -> 83,500, delta -5.0K). delta_state combines the frozen OI direction with the moving trailing 1h flow (nd1h). The 1m OI recorder (oi_1m.csv) is not read by the snapshot.
Audit: transitions counted over all 1,373 snapshots of the UTC day; BinanceClient.openInterestHist(symbol,"1h",2) and classifyOiDeltaState read; no layer reads oi_live.
Fix: none by this session. Backtests must use oi_live/oi_5m_30d.csv or Dumps metrics, not snapshot OI. Producer change (read the 5m series) needs a fail-first test and the supervisor.

## F-BT-11  OI recorder holes: 46 h of the last 4 days have no OI (all of 2026-10-06)   [MEDIUM]  status: AUDITED, ESCALATED (data operation)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: MyTradingSys/runtime/oi_live/oi_1m.csv gaps 2026-10-05 15:44 -> 10-07 07:42 (39.97 h), 10-07 19:21 -> 19:25, 10-07 23:27 -> 10-08 05:45 (6.3 h); oi_5m_30d.csv gaps 10-05 15:40 -> 10-07 07:30 and 10-07 23:25 -> 10-08 05:35. 2026-10-06 and 10-07 00:00-07:30 (incl. the 01:50-02:05 crash) have no OI; Dumps/backtest/raw/metrics stops at 2026-09-26.
Audit: gap scan over ts_ms in both files; oi_recorder.py read (appends only while the task runs; --backfill is a separate manual flag, 30-day window).
Fix: not done (live data dir, scheduled task owner). oi_recorder.py --backfill (public GET) would refill 10-06/10-07 until about 2026-11-04; after that data.binance.vision metrics. Write the refill to a new file, not into oi_live.

## F-BT-12  vwap.price is anchored at 00:00Z while session.vwap_anchor_utc says 13:30Z; chart VWAP depends on bars loaded   [MEDIUM]  status: AUDITED, ESCALATED (field naming, Java producer)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: snapshot vwap.price equals the 00:00Z-anchored VWAP (10-07 21:13 83,722.76 vs recomputed 83,722.61 from 1m hlc3 x volume; 10-05 14:53 86,074.51 vs 86,073.86) but session.vwap_anchor_utc in the same snapshot is 13:30Z; the 13:30Z VWAP is 83,205.68 on 10-07 (-517) and 85,968.28 on 10-05. buildVwap(dailyBars) vs buildSession(nyOpen) in MarketDataSnapshot. session_anchor_options_note.md describes the NY anchor as the session one, so a reader taking vwap.price as NY-anchored is off by hundreds of points. Chart side: CoinGlass VWAP is a session VWAP truncated to the loaded history (3m chart 83,461.8 = anchored 06:06Z, error 0.08, vs true 83,722.6; 4h chart 83,782.9 = 4h-bar hlc3 basis).
Audit: three anchors recomputed on two days; grep for consumers of vwap_anchor_utc: docs only.
Fix: none in code. Recommend emitting both vwap_00z and a DST-aware vwap_ny (G6) and renaming; FEAT-08 in SCREENSHOT_OBSERVATIONS.md.

## F-BT-13  Liquidity sweep flag latches on a prior-day H/L breach from the US open and never clears; local pivots invisible   [LOW]  status: AUDITED, ESCALATED (known G12/T063, numbers added)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: session.sweep_flag / liquidity_sweep_direction turn True at 13:31 and stay True to the end of the UTC day whenever price is already beyond the prior-day extreme at the US open: 10-07 True/below from 13:31 (prior-day low 85,072.7 was first broken at 01:54, 11.6 h earlier, no reclaim test); 10-04 True/above from 13:31; 10-08 True/below from 13:33; 10-03, 10-05, 10-06 never. The 10-07 13:45 sweep-and-reclaim of the 13:40 low and the 10-05 14:08 poke above the 08Z high are invisible.
Audit: six days of snapshots sampled every 3rd (transition table); buildSession lines ~786-806 read (lastSweepBelow set by any bar since 13:30 with low below priorDayLow).
Fix: none; FEAT-02 in SCREENSHOT_OBSERVATIONS.md is a causal event definition the backtest can use.

## F-BT-14  NakedPocTracker has no writer: naked POC list frozen at 2026-08-28 but still fed to setup zones   [MEDIUM]  status: AUDITED, ESCALATED (Java, live path)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: runtime_data/naked_pocs/BTCUSDT_naked_pocs.json last written 2026-08-28 11:12 (last entry 2026-08-28; unvisited 63,155.87, 77,145.49, 76,248.29, 81,294.72). recordTodayPoc and checkRevisit have no callers in src/ (grep); only getNakedPocsNode is read, in SetupCandidatesBuilder lines 333-346, which adds the entries as tfRank-11 zones. Live setups carry six-week-old naked POCs and none for 08-29..10-08, while the operator's 4h/30m charts draw each day's POC ray.
Audit: grep -rn over src, file mtimes and content.
Fix: none (live path). FEAT-07 recomputes per-day POC and first revisit from orderflow_live fp; note the Java daily POC itself is affected by the volume-profile finding.

## F-BT-15  First snapshot after 00:00Z carries a cvd.value that matches neither day   [LOW]  status: AUDITED, ESCALATED (cosmetic, Java producer)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: 10-03 00:00:xx cvd.value -407.8 (previous-day final +2,030.0, true first-bar delta +5.2); 10-05 +751.6 (final +2,276.5, delta -42.1); 10-07 -501.7 (final -2,622.6, delta -7.2). The next snapshot (00:01) equals orderflow_live cvd_day exactly. Days without a snapshot in the first two minutes (09-30, 10-01, 10-02, 10-04, 10-06, 10-08) cannot be tested.
Audit: snapshot cvd.value compared with cvd_day of the previous minute at about 30 sample points on 10-05 and 10-07: all equal to within 0.004 except the 00:00:xx snapshot.
Fix: none; harmless unless a layer reads cvd at 00:00:xx.

## F-BT-16  Time-base traps: snapshot file date is IST, footprint pages are IST, snapshots cover only two thirds of the period   [LOW]  status: AUDITED, documented (NOT-A-DEFECT for the naming)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: (a) the date in BTCUSDT_<date>_<ms>.json is the UTC+5:30 date: 2026-10-07 files span 10-06 18:30Z -> 10-07 18:29Z; (b) CoinGlass footprint pages (legend.coinglass.com) draw IST (clock 'UTC+5.5') while the TradingView pages are UTC; (c) snapshot coverage since 09-28: 9,152 files and 10 gaps over 10 min totalling 88.7 h (09-29 22:29 -> 09-30 17:43 19.2 h; 09-30 19:50 -> 10-01 14:32 18.7 h; 10-01 19:44 -> 10-02 13:01 17.3 h; 10-03 21:19 -> 10-04 09:09 11.8 h; 10-05 17:32 -> 10-06 05:11 11.7 h; 10-07 23:28 -> 10-08 08:22 8.9 h; four under 25 min), about a third of the period. F-BT-04 cleared only the order-flow recorder.
Audit: epoch ms from file names; footprint bar deltas match orderflow_live only with the -5:30 shift (33 of 33 closed 15m bars).
Fix: none to names; rule for workers: join on epoch ms, never on the date string, and treat snapshot-based samples as gap-aware.

## F-BT-17  orderflow_live 1m rows differ slightly from Binance 1m klines (boundary trades)   [INFO]  status: NOT-A-DEFECT
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker C (screenshot observations), 2026-10-09. Report: 2026-10-07 has 64 of 1,440 rows with OHLC differences (open off by 0.1-0.8; 10-04/05/06: 17/59/33), volume differs in 83 rows (max 5.54 BTC, median 0.06), buy_vol in 48.
Audit: day cumulative delta identical (-6,229.599 in both, 1e-11), so trades move between adjacent minutes at the boundary only; CoinGlass footprint deltas agree with orderflow_live within 0.07 BTC per 15m bar and 1.64 BTC per hour.
Fix: none needed. Do not re-audit.

## F-BT-18  Live layers run on SPOT klines; every history and backtest is USD-M PERP, so fires are not reproducible   [HIGH]  status: FIXED for backtests 2026-10-09 (spot 1m history downloaded, fires re-run, parity gate passes); live path unchanged (it was already spot)
Found by: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt worker B1, 2026-10-09, parity gate (FIRES_B1_REPORT.md). Report: live_runner_cli.py:84 default_fetch_klines GETs https://api.binance.com/api/v3/klines (spot); fetch_binance_archive.py BASE = data.binance.vision/data/futures/um (perp), as are orderflow_live, OI, funding and every Dumps/backtest kline. Live alert prices carry 2 decimals (84813.22, spot tick 0.01), the perp archive 1 (84582.7). Replay of the 99-bar live window on perp bars vs MyTradingSys/runtime/alerts, last 5 days 2026-10-03..10-07 with runner-dark time removed: turn_of_candle time 383 of 384 (99.7 %) but SIDE agrees on only 271 of 383 (70.8 %; |imbalance| 0.0-0.1: 53 %, 0.3-0.5: 81 %, >=0.5: 82 %; spot-vs-perp imbalance corr 0.55 on 400 fires); rsi_events 5m 65.3 %, 15m 77.8 % (all 50 unmatched events lie within the measured spot-vs-perp RSI noise of a band edge: median 0.32 / 0.15 RSI points, max 2.15 / 0.95); cryptocred and fabio escalation / cvd_absorption / volume_fvg 0-4 % (example 10-03 06:30: spot shows a record up-delta bar and three long breakouts, perp shows the record down-delta bar at 06:45 and four short ones). Held up but n too small to certify: rsi 1h 1/1, malkan_bull 2/2, session_momentum 3/3.
Audit: replay_key equals live_runner_core.run_registry fed one 99-bar window per bar on synthetic data for all 19 kline keys (test_all_kline_keys_match_run_registry; 8 mutations of the replay code all fail the tests), so the residual is data, not logic. Not provable for the flow / structure layers without spot history on disk (searched Dumps, F:/MTS/data, runtime_data: none).
Fix: not done. (a) Approve a download of Binance SPOT BTCUSDT 1m monthly klines, data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-YYYY-MM.zip + .CHECKSUM, 2022-01..2026-09 (57 files, order of 100 MB; spot files use microsecond stamps from 2025, the loader converts them), then BIGTRADE_VENUE=spot BIGTRADE_KLINE_DIRS=<dir> python -m MyTradingSys.backtest.bigtrade.fires_kline run, then parity (about 10 and 1 minutes); or (b) operator decision to point the live runner at fapi (live-path change, staged .new). Until then TOC side, rsi 5m / 15m event timing and all cryptocred / fabio fires are NOT trusted.

## F-BT-19  Live system was dark for 23 of the 120 hours of the parity window; alerts and auto_trader both silent   [MEDIUM]  status: AUDITED (operator knowledge needed)
Found by: B1, 2026-10-09. Report: turn_of_candle fires every 15 min; replay vs MyTradingSys/runtime/alerts shows runs of missing slots 2026-10-03 21:29..10-04 08:59 (47 slots), 10-05 17:44..10-06 04:59 (46), 10-07 23:29..23:59 (3), and the log has no alerts at all 09-30 04:00..10-02 21:44.
Audit: MyTradingSys/execution/auto_trades.jsonl has 0 events inside each of the three windows (normally 7..30 per hour), so the whole stack was stopped, not one layer. One more lost slot (10-06 15:29) is a single lost poll. Impact: live ledger statistics are conditioned on uptime; the parity gate excludes only-replay fires inside these windows (column dark).
Fix: none by B1 (machine sleep or shutdown overnight is an operator call).

## F-BT-20  Swing detector rejects ties: cryptocred / fabio fires depend on open == previous close micro-structure   [MEDIUM]  status: AUDITED
Found by: B1, 2026-10-09. Report: cc_structure.find_swings (use_body=True, strict <=). On a gap-free series (open = previous close) it finds ZERO swings (hand-checked on synthetic bars). On perp history 51 % of bars open exactly at the previous close (5m 51.5 %, 15m 51.3 %, 1h 50.6 %) and the strict detector keeps 32 % of the swings a tie-tolerant one finds (15m: 10,049 + 10,049 vs 31,511 + 31,342). Every fire of sr_flip / fib_pullback / failed_msb / escalation / cvd_absorption / volume_fvg inherits this, and tick-level opens differ between spot and perp, a likely cause of the 0-4 % parity in F-BT-18.
Audit: counted on the cached 5m / 15m / 1h arrays with numpy (strict vs >=); same ratio 0.32 in all three timeframes.
Fix: none (layer semantics, live path). Backtest D should register a tie-tolerant swing variant as a trial; no promotion without the usual gates.

## F-BT-21  Live alert log holds duplicate rows (41 extra rows, 14 keys; one TOC alert written 18 times)   [MEDIUM]  status: REPORTED
Found by: B1, 2026-10-09. Report: MyTradingSys/runtime/alerts/*.jsonl, duplicates on (layer, sub, tf, t_close, event): turn_of_candle 2026-10-06 10:14Z written 8 times and 10:29Z 18 times (rows 348-373 of 1m.jsonl, identical t_confirm), plus rsi_events 15m / 1h and sr_flip 1h. run_registry de-duplicates on its emitted list inside one process, so the copies point at several runner processes sharing one state file, or a state save that failed and was retried.
Audit: counted by script; cause not determined (no per-process log for that hour). The parity gate de-duplicates.
Fix: none by B1. Supervisor: check whether auto_trader de-duplicates alerts (one trade per t_close) and whether two live_runner_cli processes ever ran together (loop-supervisor match pattern).

## F-BT-22  cryptocred sr_flip stop is exactly the round-trip fee: fee_R = 1.00 on all 7,600 fires   [MEDIUM]  status: AUDITED, ESCALATED (same fix path as F-BT-01)
Found by: B1, 2026-10-09. Report: cc_setups setup1_sr_flip / setup3 stop = level -/+ stop_buffer_pct 0.001, the live adapter passes stop into the alert, fee_rt in trade_costs is 0.0010. Fire CSVs: sr_flip 15m n=6,071 and 1h n=1,529, median fee_R 1.00 (every fire), median stop distance 0.33 / 0.16 ATR of the TF; fib_pullback median fee_R 0.62 (15m) / 0.46 (1h); failed_msb 0.14 / 0.07. The live adapter emits no target.
Audit: arithmetic in test_cc_rows_carry_stop_and_fee_R (fee_R = 1.0 by construction). B1 also fixed a float bug in its own new code: a stop exactly at the fee was flagged fee_dominated on 74 % of sr_flip rows (|entry-stop|/entry = 0.00099999..); relative tolerance 1e-9 plus test_stop_exactly_at_the_fee_is_not_under_it, which failed before the fix.
Fix: via backtest D stop_buffer_atr (F-BT-01 plan); live files untouched.

## F-BT-23  tf_resample.resample drops taker-buy volume (and is slow per bar)   [LOW]  status: AUDITED, FIXED in new code
Found by: B1, 2026-10-09. Report: layers/timeframe/tf_resample.py returns o,h,l,c,v only; escalation, cvd_absorption and the turn_of_candle side need tbv and raise KeyError on its output; 2.5M bars through bucket_start with a registry lookup per bar is slow.
Audit: test_resample_equals_tf_resample_and_keeps_tbv asserts tbv is absent from tf_resample and that the new aggregator sums it.
Fix: fires_kline.resample_arrays (numpy, closed buckets only, tbv summed), tested equal to tf_resample on o/h/l/c/v; tf_resample untouched.

## F-BT-24  Docs vs code: live_runner_cli says two layers; malkan_mtf is not live; rsi events repaint by one bar   [LOW]  status: REPORTED
Found by: B1, 2026-10-09. Report: live_runner_cli.py header and build_default_registry docstring say "two registered layers (RSI and FABIO CVD)"; the registry holds 21 keys (19 replayed from klines, 2 handed to B2). malkan_mtf has no adapter in live_layers and needs weekly + monthly RSI regimes that a 99-bar window cannot hold, so it has no fires (the brief said "if live"). On the 99-bar window RSI warm-up changes as the window slides: 0.5 % of rsi_events (204 of 41,538 on 5m) are first reported one bar after their own bar time.
Audit: counted from the fire CSVs. Fix: none needed; t_fire_ms always uses the bar on which the event was first reported.

### F-BT-18 resolution (2026-10-09)
Spot BTCUSDT 1m archive (data.binance.vision, 2022-01..2026-10-07, 64 files, 122 MB) in F:/MTS/data/bigtrade/spot_raw; replay with BIGTRADE_VENUE=spot -> F:/MTS/data/bigtrade/fires_spot/. Parity last 5 d (dark time removed): every kline key 92.3-100 % (turn_of_candle 99.7 %, side differs 0 of 383; rsi 5m 100 % n=100, 15m 100 % n=32; sr_flip 15m 92.3 %; cvd/escalation/volume_fvg/fib 100 %). Use fires_spot/ for all analysis; fires/ (perp) is superseded. Cause confirmed as venue, not logic.
