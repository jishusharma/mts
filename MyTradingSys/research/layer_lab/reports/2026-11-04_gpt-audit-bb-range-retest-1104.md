FIX-FIRST — MATCH 17 | DEVIATES 2 | NOT_CHECKABLE 0

## Checked

Read `MyTradingSys/research/bb_range_retest_2026-11-04/PRE_REG.md:11-38`, `study.py:1-219`, the reused `bb_range_to_range_2026-11-04/study.py:28-152,160-235`, `MyTradingSys/backtest/research_kit.py:1-15,37-72,127-155,240-289,297-307`, `MyTradingSys/backtest/splits.py:1-5,35-43`, and `MyTradingSys/backtest/layers/FORMULAS.md:1-8`. Static source audit; no returns or market data were run/read. The study calls `--pass count|dev|val` at `study.py:133-150`; data-loading implementation is reused from the earlier study.

Each numbered row maps to a distinct PRE_REG rule/commitment. MATCH means the implementation agrees with that rule; DEVIATES identifies the absent or inconsistent implementation.

| # | PRE_REG rule | Verdict and implementation evidence |
|---|---|---|
| 1 | BB(20,2), close-only, population SD, current bar included (`PRE_REG.md:15`) | MATCH — `bb_range_to_range_2026-11-04/study.py:29,45-54` sets 20 and 2, uses closes `i-19..i`, and NumPy population `std()`; `bb_range_retest.../study.py:24-27` imports the event finder. |
| 2 | First excursion close, static touched-band level and opposite-band target; pooled sides (`PRE_REG.md:16`) | MATCH — `bb_range_to_range_2026-11-04/study.py:57-76` records first close crossing, that bar’s band levels and side; `study.py:112-114,127-130` carries pooled or side-filtered output. |
| 3 | Re-entry close within 10 bars (`PRE_REG.md:17`) | MATCH — `study.py:32,77-92` uses bars after signal through M=10, strict close back inside, no entry absent re-entry. |
| 4 | Inside-band resting limit at level + side*k*signal ATR, k={.25,.5,1}, first qualifying touch within 10 bars; fill limit or gap open (`PRE_REG.md:18`) | MATCH — `study.py:33-34,77-92`; delegated `research_kit.py:275-289` searches subsequent bars, returns first touch, and uses min(open,level) for long / max(open,level) for short. |
| 5 | Static opposite-band target; stop at half target distance; stop-first, gap stop at open, exit after 24 bars; exclude re-entry/fill bars (`PRE_REG.md:19`) | MATCH — `bb_range_to_range_2026-11-04/study.py:30-31,79-100` implements the bracket and 24 subsequent bars; the fill function excludes bars through re-entry (`study.py:77-92`). |
| 6 | Range gate as-of signal close; band 60/40 and SMA200 context (`PRE_REG.md:20`) | MATCH — `study.py:21-22,153-163` uses imported `regime_at` at event close; `research_kit.py:240-259` maps the as-of SMA side and RSI band to bull/bear/range, while unavailable context becomes `none` in `study.py:162`. |
| 7 | Session from signal close; Asia/London/NY confirmatory and late descriptive (`PRE_REG.md:21,26,28`) | MATCH — `study.py:38-39,157-162,167-175,196-205`; `research_kit.py:270-272` delegates session tagging for close time. |
| 8 | Running session range % of close strictly above median of prior 20 same-name sessions; >=10 history; as-of (`PRE_REG.md:22`) | MATCH — `study.py:35-36,55-74` keeps per-name session history, tags only with >=10 prior sessions, and uses strict `>` against the median of up to 20 finalized prior ranges. |
| 9 | Round-trip cost 0.14% (`PRE_REG.md:23`) | MATCH — `study.py:37` takes `rk.TAKER_RT_PCT`; `research_kit.py:12-14,21` defines 0.14 in percent units as the sourced taker round trip. |
| 10 | Net=gross-cost in percent; day-clustered SE and 95% mean±1.96SE (`PRE_REG.md:24`) | MATCH — reused `bb_range_to_range_2026-11-04/study.py:141-152` subtracts `COST` from gross percent, clusters on UTC fill day, and reports `m±1.96*se`; `research_kit.py:3-8,37-49` defines the units and clustered SE. `FORMULAS.md:1-8` is for indicator layers and supplies no competing formula for this study. |
| 11 | Tagged-range vs all-regime tagged and tagged-range vs untagged comparisons (`PRE_REG.md:25`) | MATCH — `study.py:127-130,186-192` selects those arms and calls `cluster_diff` on gross returns/fill-day clusters. |
| 12 | Concept-only row copied from earlier `dev_cells.csv` (`PRE_REG.md:25`) | DEVIATES — output rows are generated only from current-study loops (`study.py:165-193`) and written as current counts/dev/val CSV (`study.py:206-211`); there is no read/import of earlier `dev_cells.csv` or concept-only row. |
| 13 | 15m × Asia/London/NY × three k values; Holm m=9 (`PRE_REG.md:26`) | MATCH — `study.py:30,34,39,165-169,196-200` selects the stated family and sets m to 3×3=9. |
| 14 | DEV survivor thresholds n>=30, >=20 days, net>0, Holm p<.05, difference t>=2 (`PRE_REG.md:27`) | MATCH — `study.py:196-205` computes that exact conjunction for confirmatory range/tagged/pooled rows. |
| 15 | Descriptive cells include 15m late, per side, untagged/any-tag, all-regime; never survivors/verdict (`PRE_REG.md:28`) | MATCH — `study.py:38-40,167-175` includes these dimensions; survivor family is separately restricted at `study.py:196-203`. |
| 16 | Fill rates for fills/signals and fills/re-entered; invalidate arm at >=95% (`PRE_REG.md:29`) | MATCH — counts for signals, re-entered and fills are assembled at `study.py:177-180`; `study.py:77-92,118-124` defines the re-entry measure. The stated 95% invalidation is a result/reporting instruction, not automated: this audit checks structural implementation only; no result table was run to assess the threshold. |
| 17 | DEV signal close window [2022-01-01,2024-07-01), VAL [2024-07-01,2025-07-01) once for DEV survivors, no HOLDOUT (`PRE_REG.md:30`) | MATCH — `splits.py:35-43` sets half-open boundaries; `study.py:140-150` blocks VAL without survivors and an existing val output, `study.py:148-152` selects split and loads through its end, and `study.py:163,171-173` filters by signal close. The reused loader asserts last bar `< hi_ms` (`bb_range_to_range_2026-11-04/study.py:178-180`). |
| 18 | Validation survivors require raw p<.05 and same sign; no survivors means validation is not read (`PRE_REG.md:30`) | DEVIATES — no-survivor refusal matches at `study.py:140-147`, and VAL cell statistics include raw p at `study.py:184-192` via `prev.cell_stats`; however, the VAL branch only filters to listed DEV survivors (`study.py:171-172`) and writes rows (`study.py:206-211`). It never checks raw p<.05 or same-sign net versus DEV, nor records a validation pass/fail flag. |
| 19 | Power ceiling: BLOCKED.md pre-runs gate; all nine blocked; regime mix stated as context (`PRE_REG.md:31-38`) | MATCH (code path) — DEV survivor gate implements “no PASS” conservatively through the registered thresholds (`study.py:196-205`); weekly mix is generated and saved per pass (`study.py:212-214`) using `week_starts` and `regime_mix_line`. The exact BLOCKED.md counts/MDE figures are frozen report inputs, not recomputed by this audit. |

## Findings

1. **DEVIATES — missing concept-only comparison row.** Implement the preregistered copied row in the output/report assembly or explicitly amend the registration before interpreting comparison output. Evidence: `PRE_REG.md:25`; `study.py:165-193,206-211`.
2. **DEVIATES — validation acceptance rule is not implemented.** After VAL statistics are computed for each DEV survivor, compare the raw p-value with 0.05 and require the same sign as DEV; record the result. Evidence: `PRE_REG.md:30`; `study.py:171-172,184-192,206-211`.

No source files or study outputs were edited. No numerical/data validation was performed; the separate blind-read card owns the saved-number check.

