# T088-T091 All-timeframe capture, wired for testing (operator 2026-10-09 14:32 UTC)

Operator words: "Make sure we have a timeframe module that makes sure we have what we need! 1m, 2m, 3m, 4m, 5m, 10m, 15m, 30m, 1h, 2h, 3h,4h,6h,7h(dark horse - research this time frame on youtube and internet), 8h, 12h, 1d, 2d, 3d, 5d, 1w. Prepare relevant tasks to capture these on all time frames - wired for testing."
Trigger: 30m BTCUSDT screenshot 6188a576411b (screenshots/2026-10-09_BTCUSDT_6188a576411b.md).

## What exists (checked 2026-10-09)
`backtest/layers/timeframe/registry.json` + `tf_resample.py` (FORMULAS 8, tests in test_tf_resample.py, real-data gate tf_realdata_gate.py) already hold 18 of the 21 asked frames: 1m 2m 3m 5m 10m 15m 30m 1h 2h 4h 6h 8h 12h 1d 2d 3d 5d 1w (+1M).
Missing: 4m, 3h, 7h. 4m and 3h divide 24 h, so epoch alignment = daily-aligned. 7h (25,200 s) does not divide 24 h: epoch-aligned 7h buckets drift against the UTC day; TradingView-style charts reset intraday bars at the session/day start (00:00, 07:00, 14:00, 21:00, then a 3h stub). Which anchor is right is open (T090).
Live: the live runner polls 1m / 5m / 15m / 1h layers only (live_runner.log families); no live multi-TF capture.

## Tasks
- T088 (MED) Add 4m, 3h, 7h to registry.json with tests that fail first (bucket starts, partial-bucket rule, gap count); 7h anchoring as decided in T090, until then both variants (epoch, day-reset) behind an explicit registry key, NO-SOURCE flagged. Grep every TF map (alert_rate_check, account routing, audits) per CLAUDE.md.
- T089 (HIGH) Multi-TF RSI divergence capture for testing: run rsi_divergence.py (Malkan 3-10 bars, sourced) on every registry frame from the 2022-01..2026-10 1m klines via tf_resample; event table per TF with forward outcome (FORMULAS 7) and fees; >= 300 events per TF before any verdict; split by year and by B154 session/regime when available. Backtest only, no live gate.
- T090 (MED) 7h research under playbook PART I (T1-T3 / REJECT, verified citations): who uses 7h, on what anchor, any tested evidence. Seed (unverified, standard web search 2026-10-09): TradingView scripts "MCS HTF Po3" (7H candles printed from 18:00, ICT power-of-three framing) and "7 hours a day" (range between 20:00 and 03:00). Neither is a test result.
- T091 (LOW, operator idea, NO-SOURCE) Long-range divergence: the operator's 30m pairs (10-07 14:30 -> 10-08 17:00, 53 bars; 1m 13:36 -> 14:01, 26 bars) are outside Malkan's window, and Malkan rejects them in his own words: "If you have 30 times divergence, 50 times divergence, that is diluted." (extract_Wvq1TZh8aF0.md:13) and "The divergence gets diluted completely and it has not worked." (extract_cQ-y1oULkBw.md:15). Measure it in the T089 table as a separate operator-idea column (11-60 bars, non-adjacent swings); never wired live without a source.

## Result T089 + T091 (2026-10-09)
DONE. No edge on any timeframe with >= 300 events (32 cells, 1m-1h + 2h Malkan bearish), Malkan or operator column; the rest of 2h and up stay insufficient n. research/rsi_divergence_mtf_2026-10-09/RESULT.md.

## Result T088 (2026-10-09)
DONE. registry.json now holds 4m, 3h, 7h (unit day_reset_seconds: 00/07/14/21 UTC then a 3h stub, the default) and
7h_epoch (epoch-aligned, drifts 3h a day); both 7h keys carry a NO-SOURCE flag until T090 picks the anchor.
tf_resample.py handles the new unit; 9 new tests in test_tf_resample.py failed on the old code. TF maps: observation/capture.py
TF_MINUTES gained 4m/3h/7h; alert_rate_check and market_guide map live alert families only, none on these frames, unchanged.
T089 rerun on the four frames: 4m no edge; 3h/7h insufficient n; 7h operator bullish lead (46, t 2.11) disappears on 7h_epoch.
research/rsi_divergence_mtf_2026-10-09/RESULT.md (T088 addendum).
