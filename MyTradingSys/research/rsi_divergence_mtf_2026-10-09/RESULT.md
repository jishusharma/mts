# T089 + T091 result: RSI divergence on every timeframe, 2022-01-01 .. 2026-10-07 (2026-10-09)

Verdict: no edge on any timeframe that reached 300 events, for either Malkan's sourced 3-10 bar rule or the
operator's 11-60 bar long-range idea. From 2h up only one cell (2h Malkan bearish, 301) reaches 300 events on one
symbol in 4.75 years; the rest stay "insufficient n" (not "edge", not "no edge").

- 32 cells have >= 300 events (1m-1h except 1h operator bullish at 277, plus 2h Malkan bearish). Gross forward return at 10 bars sits within a few
  hundredths of a percent of plain drift; after one taker round trip (0.10%) 31 of 32 are net negative (t -0.4 to
  -73). On 1m-30m net is negative in every year 2022-2026 except three 2024 operator cells (15m/30m, +0.001% to
  +0.072%).
- Best cell with enough n: 1h operator bearish, 332 events, net +0.038%, t 0.39: noise.
- 6h operator bullish (54 events, net +1.57%, t 2.99) and 2d operator cells look large, but n is 6-54; they are
  leads for a multi-symbol rerun at most, not results.
- Operator column (T091) is no better than Malkan's: Malkan's own words ("diluted") are not contradicted.

Method: `backtest/layers/rsi/run_divergence_mtf.py` (9 tests). RSI 14, close to close, events stamped the bar
after swing B (causal). FORMULAS s7 forward return at 1/5/10/20 bars, net of fees.py taker x2. Verdict at 10
bars needs >= 300 events, net > 0, t >= 2, gross above same-side drift, net > 0 in half the years. 10 bars, t 2
and the 00/12 UTC halves are engineering choices fixed before the run (NO-SOURCE). No stop/target bracket and no
candle confirmation: this measures the raw signal only. B154 regime split not available in code yet.

Files: REPORT.md (all cells + by-year table), summary.json (all horizons, by year, by 12h half).
Data: 2,507,040 1m bars (1741 full days, no gaps), live-tree Dumps/backtest raw_1m_2022 + raw.

## T088 addendum: 4m, 3h, 7h, 7h_epoch (2026-10-09)

Same script, data and rules, `--tfs 4m,3h,7h,7h_epoch` after T088 added them to the registry. Files: REPORT_T088.md,
summary_T088.json.
- 4m: no edge. 14,490 Malkan + 8,815 operator events, gross equals drift, net -0.10% at 10 bars (t -14 to -20),
  negative in every year 2022-2026.
- 3h (168-208 Malkan, 94-106 operator) and 7h (46-113): insufficient n, no verdict.
- 7h operator bullish, 46 events, net +1.09%, t 2.11, positive in all 5 years (8-11 a year): the same shape as the
  6h operator bullish lead. A lead for a multi-symbol rerun only. The epoch-aligned 7h variant gives 41 events,
  net +0.47%, t 0.72, so the lead depends on the 00:00 UTC day-reset anchor (NO-SOURCE, T090 open).
