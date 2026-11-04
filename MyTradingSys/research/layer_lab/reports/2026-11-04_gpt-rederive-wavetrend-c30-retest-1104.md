SOUND ? audited closed-bar timing, retest window/fill, session attribution, HTF gates, and fee arithmetic; no lookahead found in the inspected paths.

## What was checked

- `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/study.py:80-95,110-168,226-253,269-300,322-324` ? dot timestamps, RSI/divergence, retest entry, trade return, session and HTF tags, window bounds.
- `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/study_long.py:40-80,103-143` ? long-window load bounds, strict/proxy context, and reuse of the same confluence and trade loop.
- `MyTradingSys/backtest/research_kit.py:209-212,240-259,270-289` ? closed-state selection, regime construction, session definition, and first-touch retest fill.
- `MyTradingSys/backtest/layers/timeframe/tf_resample.py:90-123`; `MyTradingSys/backtest/layers/rsi/rsi_core.py:7-13,22-55`; `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:48-57,60-98` ? aggregation and indicator event timestamps.
- Method: static source trace; no market-data run or output-cell metric was independently recomputed in this audit.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `study.py:80-95`; `wt_parity_ref.py` (loaded at `study.py:73-76`) | MATCH | Dot cross and band check use same index `i`; event close is `bar open + timeframe duration`. The resampler emits closed buckets only (`tf_resample.py:90-117`). No next-bar price enters the trigger. | None. |
| LOW | `study.py:110-118,226-230,246-253,285-286`; `rsi_core.py:7-13,42-55` | MATCH | RSI at index `i` is computed from closes through `i`; the confluence reads `rsi[i]`. Divergence pivots require the right-neighbour close, then are stamped at `ts[b+1]` (`rsi_divergence.py:48-57,91-98`); `div_ok` only accepts stamps from `i-3` through `i`. | None. |
| LOW | `study.py:127-145,272-280`; `research_kit.py:209-212,240-259` | MATCH | Context is queried at the dot close. Daily closes are timestamped at next midnight (`study.py:233-237`); weekly/monthly RSI timestamps are likewise the next bar start (`study.py:226-230`) and `_last_closed` admits only close timestamps `<= t`. The long proxy uses the same as-of strict side and weekly RSI (`study_long.py:62-73`). | None. |
| LOW | `study.py:148-168`; `research_kit.py:275-289` | MATCH | Retest scans bars `i+1` through `i+N` inclusive, no more than six bars; first touch fills at midpoint or gap-through open. The signal bar cannot count. Return exits at `j+H` close and uses actual fill price; an unavailable exit is dropped. | None. |
| LOW | `study.py:97-102,153-168,191-214`; `PRE_REG.md:21,51-52` | MATCH | Session arm is deliberately defined by UTC dot-bar close, and filtering occurs before trade construction. A retest may fill in a later session; that trade remains attributed to the signal session, as pre-registered. This is signal-session performance, not fill-session performance. | None for the registered question; label any future fill-session analysis as a separate metric. |
| LOW | `study.py:25-27,171-180`; `research_kit.py:12-14,21-22` | MATCH | Gross is directional percentage return from fill to exit; net is `gross - 0.14` percentage points. `TAKER_RT_PCT=0.14` is the registered round trip (5+5 bp fees plus 2+2 bp slippage). The same cost applies to signal and retest entries; no maker discount is assumed, matching `PRE_REG.md:24-26`. | None. |
| LOW | `study_long.py:40-52,76-80,103-110` | MATCH | End timestamp is `DEV_END` or `VALIDATION_END` and passed to every loader; final bar open is asserted `< hi_ms`. Data loads are bounded before window end; no future context or post-window bar is used by the shown code. | None. |

## Limits

This is a code-path audit, not a fresh numerical rerun of `dev_cells.csv` or `dev_cells_long.csv`; therefore it does not certify reported sample counts, means, p-values, or the fee-net verdict. No data files were read. The session interpretation is confirmed against the pre-registration rather than inferred from output tables.

## Follow-up cards

None.
