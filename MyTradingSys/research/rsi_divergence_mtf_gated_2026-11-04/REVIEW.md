# Blind read: malkan_div_trade_charts.py vs study.py (2026-11-06)

Read from source only (malkan_div_trade_charts.py, study.py, plus rsi_divergence.py for the event fields). Existing RESULT/BLOCKED files not read. Research docs only.

## Verdict on the question
Chart marks = study trades: the chart calls the same find_events / gate_events / trades_for with the same lo/hi window, then re-keys each trade to its event by bar open time (L38, L45). Event bar i = swing B + 1 (rsi_divergence.py L104), one event per B, so the key is unique. Entry = close of bar i (study.py L102-103), exit = close of bar i+H (L111), both drawn that way (L51-52). No lookahead in the signal: the pivot is confirmed by bar i's own close. Bars drawn after i (to i+H+AFTER, L46) are post-entry by design for showing the exit; they never feed the signal. RSI series for the chart is rsi_core on the full close list; pure causal recursion, so values at bars <= i do not depend on later bars (assumes rsi_core is causal; not re-read).

## Defects (display only, none changes the traded numbers)
1. malkan_div_trade_charts.py:46 `a = max(0, e["a_i"]-4, e["b_i"]-BEFORE)`: max, not min. With B-A <= 17, b_i-30 < a_i-4 always, so BEFORE=30 (L16, "candles shown before swing B") is dead; chart always starts 4 bars before swing A (13-21 bars before B, not 30).
2. malkan_div_trade_charts.py:62-63 compares a simple mean of rounded (3 dp) nets to dev_cells net with tolerance 1e-2 (percent). Loose: a 0.01 pct-point drift passes. cluster_mean_se returns the plain mean (research_kit.py L43) so the comparison is the right quantity, only the tolerance is weak.
3. L70-73 hard-codes "10 candles", "3-18" and tf_min 240 instead of S.H / S.ARMS / S.TF_MS; L72 `ref["net"][:6]` string-slices a number (a long negative or sci-notation value truncates oddly).
4. Goal asked for 12/18/>18-bar marks: the chart covers only the W18 arm (3-18 bars); W12 and a >18 split are not drawn, and e["bars"] (the A-to-B span) is not exported, so a 12 vs 13-18 bar divergence cannot be told apart on the chart.
5. Not verified: partial last 4h bar at the DEV end. load_1m cuts 1m data at DEV_END 2024-07-01 (midnight, a 4h boundary), so no partial bar expected; the j+h >= len guard (study.py L109) drops events lacking an exit bar.

FOUND: 5 items (0 affecting trades/marks/lookahead; 2 display-logic: #1, #4; 3 hygiene: #2, #3, #5 unverified). DIFF vs study entries: 0.
