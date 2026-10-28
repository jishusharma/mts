# HANDOFF W2a - levels confluence (wave 2, created files only)
1. Module `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py`; adapter `levels_confluence_layer(bars)` (1m bars, live_layers shape).
2. Needs >= 14 UTC days of 1m history in the bar window (prior week, 10-day naked POC / fractals); adapter reports the last 2 UTC days.
3. Registry: ONE key `layer:levels:confluence:1m` (events carry `family`; split per family later only if routing needs it). Grandfather, no PASS verdict.
4. Event: `lc_<family>_<round(level)>`, side long = price was above the level on the previous bar's close (Q79), `sampling: true`.
5. Proposed size (OURS): 20 USD / 2 (per layer unit, calibration data source, not an edge claim).
6. W3: grep every TF/family map (alert_rate_check, account routing, audits) for the new 1m layer key.
7. Counts: 1278 first-touch events on the DEV seed span = research event_table.csv exactly (per day and family); touch bars identical.
8. research event_table.csv sides predate Q79 (they equal the touch-bar close side); only counts are comparable. Do not read its outcomes.
9. Caveat: Java level builder matches these Python zones only 54.9% (ledger 59b85fd2); Python research is the reference here.
10. Tests: `test_live_levels_confluence.py` (11, auto-gated under backtest/, B150); 2 mutants (touch-bar side, same-day levels) fail them.
