# GPT independent audit: Bollinger range-to-range session study

**Verdict: PASS** — the audited implementation matches PRE_REG.md for entry/exit indexing, fee-net arithmetic, and range/session assignment. No return data was run or inspected in this audit.

## Scope and evidence

Read `MyTradingSys/research/bb_range_to_range_2026-11-04/PRE_REG.md` (parameter and context rules, especially lines 15–31 and 61–63), `study.py` (lines 45–76, 79–138, 141–152, 183–234), and delegated helpers in `MyTradingSys/backtest/research_kit.py` (lines 21, 37–69, 240–259, 270–289), sibling context wrapper `MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py` (lines 64–74, 147–169), `MyTradingSys/backtest/layers/timeframe/tf_resample.py` (lines 90–153), and `MyTradingSys/backtest/splits.py` (lines 1–25).

No study pass was run. This is a static code/math audit; no DEV outcome bars or later bars were read.

## Findings

| Severity | Location | Result | Evidence and assessment | Proposed fix |
|---|---|---|---|---|
| — | `study.py:45–76`; `PRE_REG.md:13–16` | MATCH | `bb_bands` uses the inclusive trailing window `i-19..i`, population `std`, and K=2. `find_events` tags a long on first close crossing to `close <= lower`, short mirrored at upper, and stores the signal-bar opposite band as a static target. The first candidate index is 20 so both current and prior band values are valid. | None. |
| — | `study.py:79–100, 113–138`; `research_kit.py:275–289`; `PRE_REG.md:17–20` | MATCH | Signal entry uses the signal close (`j=i`, `px=close[i]`). Retest searches only bars `i+1..i+10`; long/short fills use the level unless the open gapped through it. `bracket_trade` excludes entry bar `j`, checks `j+1..j+24` inclusive, prioritizes stop if both levels touch, uses open on stop gaps, and times out at bar `j+24` close. | None. |
| — | `study.py:141–152`; `research_kit.py:21,37–48`; `PRE_REG.md:25–26` | MATCH | Each trade’s net return is gross percentage return minus the constant `TAKER_RT_PCT = 0.14`; both are in percentage points of entry price. Clustered mean/SE and 95% interval are then computed on net returns using entry-day labels. This matches the preregistered arithmetic. | None. |
| — | `study.py:103–110, 123–127, 178–192`; `research_kit.py:240–259,270–272`; sibling `study.py:64–74`; `PRE_REG.md:8,14,21,61` | MATCH | Event time is `bar open + timeframe` (the signal close). That close timestamp is passed to `session_tag` in UTC seconds and to `regime_at`; the wrapper evaluates the prior fully closed daily/weekly/monthly context at the UTC day boundary, so no unfinished higher-timeframe candle is used. Gate `all` retains untagged events, while range/bull/bear require the matching as-of regime. Signals are filtered by the half-open signal-close window `[lo_ms, hi_ms)`. Session is assigned once from the signal close and retained for either entry arm, as preregistered. | None. |
| — | `study.py:165–181`; sibling `study.py:147–169`; `tf_resample.py:90–153`; `PRE_REG.md:31` | MATCH | The study selects DEV end from `splits`, calls `load_1m(hi_ms)`, asserts the last loaded open is before the boundary, and the loader passes that end bound through to `load_klines`. Resampling returns closed bars only. The validation branch similarly uses its exclusive end and has a one-read output guard. The audited path does not load holdout data. | None. |
| LOW | `study.py:208–213`; `PRE_REG.md:27` | MATCH | `cluster_diff` is applied to gross returns rather than net. Since the same fixed 0.14 percentage-point cost is deducted per trade in both arms, subtracting it from each arm would cancel from the range-minus-ungated mean difference; using gross therefore yields the same difference and SE. | None. |

## Conclusion

No lookahead or mismatch was found in the requested entry/exit indexing, fee-net math, or range/session boundary logic. This PASS is limited to implementation fidelity; it is not a finding that the encoded setup has a profitable edge.

Follow-up cards created: none.
