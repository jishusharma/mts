FIX-FIRST — 18 MATCH, 2 DEVIATES, 0 NOT_CHECKABLE

# GPT audit: Bollinger range-to-range by session

## Verdict

FIX-FIRST. The declared cell construction, event/bracket mechanics, cost netting, splits, and regime-mix reporting are implemented. Validation computes metrics for DEV survivors but does not apply or record the PRE_REG validation eligibility rule (raw p < 0.05 and same sign); this is a decision/reporting deviation, not a signal-loop deviation. The report contains 20 numbered PRE_REG checks.

## What was checked

Read `MyTradingSys/research/bb_range_to_range_2026-11-04/PRE_REG.md` (parameters, power gate, result contract, context), `MyTradingSys/research/bb_range_to_range_2026-11-04/study.py` (lines 1–240), `MyTradingSys/backtest/layers/FORMULAS.md` (especially lines 352–358 for net convention and 657–659 for per-leg fee model), and `MyTradingSys/backtest/research_kit.py` plus `MyTradingSys/backtest/splits.py` for the referenced helper definitions/constants. This is a source audit; no market data or returns were read or computed.

## Findings

| # | PRE_REG rule | Status | Code evidence / finding |
|---:|---|---|---|
| 1 | BB(20,2), CLOSE, population SD, current bar included | MATCH | `study.py:29,45-54` sets 20/2; `std()` default is population SD; window is `i-19..i`. |
| 2 | Range tag from weekly/monthly RSI 60/40 plus daily SMA200, as-of signal close; untagged not range | MATCH | `study.py:107-110,181`; `research_kit.py:240-259` implements as-of daily and last-closed weekly/monthly regime and returns `None` when unavailable. |
| 3 | First close excursion only; long <= lower, short >= upper; sides pooled | MATCH | `study.py:57-75`, especially `i=20` onward, strict prior excursion check at `:68-70`; both sides emitted. |
| 4 | Target is opposite signal-bar band, static | MATCH | `study.py:58-60,68-75`; target captured from opposite band at event creation and passed unchanged to bracket at `:131`. |
| 5 | Stop distance 0.5 of target distance; 2:1 reward/risk; stop-first, gap-through stop at open | MATCH | `study.py:79-100`; `:85` stop geometry, stop branches before target (`:91-94,96-99`), open-aware stop fill (`min` long / `max` short). |
| 6 | Timeout at close of 24th post-entry bar | MATCH | `study.py:30,79-82,86-100`; examines `j+1..j+24`, returns close of `j+24`. |
| 7 | Signal entry at signal-bar close | MATCH | `study.py:123-126`. Exit routine starts at `j+1` (`:88`), so entry bar is not reused. |
| 8 | Retest: 10 following bars, band limit, gap-open fill, no touch skip; fill bar excluded from exits | MATCH | `study.py:32,127-130`; helper `research_kit.py:275-289` scans `i+1..i+n`, fills at level/open, returns None on miss; bracket begins after fill bar (`study.py:88`). |
| 9 | Session assigned from signal-bar close; cutoffs 08/13/21 UTC | MATCH | `study.py:74,103-105,186-187`; `research_kit.py:270-272` routes UTC close time to the documented session helper. |
| 10 | Wide descriptive stratum: current width vs median of prior 500 widths; not confirmatory | MATCH | `study.py:33,60,71-75`; preceding widths only, descriptive selection appears at `:195-200`; family filter excludes it at `:217-220`. |
| 11 | Phase not gated | MATCH | No phase classification/gate in `study.py`; regime filters are limited to `GATES` `range/all/bull/bear` at `:39` and `gate_events` `:107-110`. PRE_REG Context says phase is not part of this study. |
| 12 | TFs 15m, 1h, 4h, and BTC 1m resampled | MATCH | `study.py:35-36,161,183-185`; 1m loader is resampled to each declared TF. |
| 13 | Cost is 0.14% RT; net = gross - cost, percent units | MATCH | `study.py:34,141-152`; `COST = rk.TAKER_RT_PCT`, net = gross minus constant. `research_kit.py:21` sets 0.14. FORMULAS.md:352-358 documents the distinct layer fee/slippage convention; this study explicitly sources the research-kit cost and does not claim the layer simulator fee model. |
| 14 | Day-clustered SE and mean ±1.96 SE CI | MATCH | `study.py:135,141-152`; day is UTC epoch day at fill bar; `cluster_mean_se(net,d)`, and CI uses ±1.96 SE. |
| 15 | Ungated comparator includes every regime incl. untagged; gate effect range minus ungated with shared-day clustering; bull/bear controls | MATCH | `study.py:107-110,189-213`; `all` preserves all events; range comparison calls shared-day `cluster_diff`; gate grid includes bull/bear. Fixed cost cancels from the difference. |
| 16 | Confirmatory family exactly 6 cells; Holm m=6; others descriptive | MATCH | `study.py:37-42,217-226`; three sessions × two entries, 15m/range/both/any, `m=6`, Holm; remaining combinations do not enter family. |
| 17 | DEV survivor criteria n≥30, days≥20, net>0, Holm p<.05, range-vs-ungated t≥2 | MATCH | `study.py:41,217-226`; all five conditions applied in survivor boolean. |
| 18 | DEV window signal closes [2022-01-01, 2024-07-01); loaded bars capped at exclusive end; validation [2024-07-01,2025-07-01) once for DEV survivors; HOLDOUT not loaded | MATCH | `study.py:167-179,192,196-200`; `splits.py:35,40-43`; loader receives `hi_ms` and asserts final bar `< hi_ms`; VAL pass filters to survivors and refuses existing `val_cells.csv`. Note sibling loader/context construction is reused via `study.py:23-26`. |
| 19 | Validation eligibility: survivors require raw p<.05 and same sign | DEVIATES | `study.py:196-200` selects DEV survivors for VAL, and `:207` writes VAL stats, but no code compares validation raw `p` with .05 or checks the sign against DEV. Add an explicit per-survivor validation classification/output; do not infer eligibility from the metrics table. |
| 20 | Verdict ceiling: no survivor => FAIL for confirmatory rule; survivor requires validation; PASS also needs causal replay and independent trade-loop rerun; descriptive cells no verdict | DEVIATES | `study.py:216-236` writes survivor list and cells/regime line but contains no verdict/validation classification output and no explicit PASS ceiling/replay/re-run status. The PRE_REG requires at minimum classifying validation and forbids PASS absent replay and independent rerun. |

## Follow-up

No follow-up card created. Source fix recommended: make the validation pass emit a per-DEV-survivor check of raw validation p < 0.05 and sign agreement, and record the PRE_REG verdict ceiling in the result writer.