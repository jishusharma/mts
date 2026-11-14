# PRE_REG Lint: Nov 5–11 Studies

Scope: 8 study folders under `MyTradingSys/research/` from 2026-11-05 to 2026-11-11.
Counts (OURS): 5 of 8 folders have `PRE_REG.md`; 3 of 8 have no `PRE_REG*.md`. Among the 5 present `PRE_REG.md` files, 2 (`mtf_lead_lag_2026-11-09` and `with_trend_session_2026-11-11`) have `PRE_REG.md` committed before results, 2 (`anticipation_map_2026-11-05` and `bigcandle_story_2026-11-05`) were committed in the same commit as their results, and 1 (`tom_swing_2026-11-09`) has no results commit yet.

## Summary Table

| Study | PRE_REG present | SOURCED/OURS labels | Frozen split | n floor | Kill criterion | ## Context (Regime/Phase/Session/Entry) | PRE_REG predates results (git log) | Key file:line |
|---|---|---|---|---|---|---|---|---|
| `anticipation_map_2026-11-05` | Y | Y | Y | N | N | Y (4/4) | N (same commit `93841e3ea`) | `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:9-29` |
| `bigcandle_story_2026-11-05` | Y | Y | Y | Y | N | Y (4/4) | N (same commit `b2010203f`) | `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:9-30` |
| `value_area_acceptance_2026-11-05` | N | N/A | N/A | N/A | N/A | N/A | N/A (no PRE_REG; `RESULT.md` in `b4e80f81c`) | `MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md:1` |
| `auction_forward_2026-11-09` | N | N/A | N/A | N/A | N/A | N/A | N/A (no PRE_REG; no results) | `MyTradingSys/research/auction_forward_2026-11-09/forward_log.py:1` |
| `mtf_lead_lag_2026-11-09` | Y | PARTIAL (SOURCED only; no OURS) | Y | N | Y | Y (4/4) | Y (`719a0b214` < `5f27287b6`) | `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:5-27` |
| `tom_swing_2026-11-09` | Y | Y | N | Y | N | Y (4/4) | N/A (no results yet; `b9c4bf568`) | `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:12-64` |
| `us_open_first3m_2026-11-11` | N | N/A | N/A | N/A | N/A | N/A | N/A (no PRE_REG; `RESULT.md` in `6bd8eb5ca`) | `MyTradingSys/research/us_open_first3m_2026-11-11/RESULT.md:1` |
| `with_trend_session_2026-11-11` | Y | Y | Y | Y | Y | Y (4/4) | Y (`a89bb7f40` < `8601c65fb`) | `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:1-38` |

## Per-Study Details

### 1. `anticipation_map_2026-11-05`
- **Files:** `PRE_REG.md`, `RESULT.md`, `study.py`
- **SOURCED/OURS labels (Y):** `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:9` ("SOURCED.") and `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:13` ("Definitions (all OURS, fixed before the run)").
- **Frozen split (Y):** `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:10` ("DEV only: 2022-01-01 to 2024-06-30; the loader drops every bar at or after 2024-07-01. VALIDATION/HOLDOUT not read.") and `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:29` ("FROZEN_UTC: 2026-11-05T00:58:28Z").
- **n floor (N):** No minimum `n` floor or THIN threshold in `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:28` ("RESULT.md: Regime mix: line, then the table of 8 cells (n, share of the state, continue, undone, OI keeps sign).").
- **Kill criterion (N):** No kill line; `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:3` ("Descriptive, fee-free; no entries, no edge claim, so no costs and no fees.py import.").
- **## Context (Y, 4/4):** `MyTradingSys/research/anticipation_map_2026-11-05/PRE_REG.md:21-25` has `Regime:` (`:22`), `Phase:` (`:23`), `Session:` (`:24`), `Entry:` (`:25`).
- **Git log:** `93841e3ea` (`2026-11-05T06:36:27+05:30`) added `PRE_REG.md`, `RESULT.md`, and `study.py` together.

### 2. `bigcandle_story_2026-11-05`
- **Files:** `fetch_data.py`, `PRE_REG.md`, `RESULT.md`, `study.py`, `tables.md`, `test_bigcandle_story.py`, `test_study_spec.py`, `walkthrough.md`
- **SOURCED/OURS labels (Y):** `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:9` ("SOURCED.") and `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:12` ("Definitions (all OURS, fixed before any outcome column was read)").
- **Frozen split (Y):** `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:10` ("DEV only: 2022-01-03 to 2024-06-30. Holdout never read for any table.") and `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:30` ("FROZEN_UTC: 2026-11-05T14:00:00Z").
- **n floor (Y):** `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:20` ("Wilson 95 % CI on every rate; n per cell; n < 30 = THIN.").
- **Kill criterion (N):** No kill line; `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:3` ("Descriptive, fee-free; no entries, no trade rule, no edge claim, so no costs and no fees.py import.").
- **## Context (Y, 4/4):** `MyTradingSys/research/bigcandle_story_2026-11-05/PRE_REG.md:22-26` has `Regime:` (`:23`), `Phase:` (`:24`), `Session:` (`:25`), `Entry:` (`:26`).
- **Git log:** `b2010203f` (`2026-11-05T19:37:16+05:30`) added `PRE_REG.md`, `RESULT.md`, `tables.md`, `walkthrough.md`, `study.py`, `fetch_data.py`, `test_study.py` together.

### 3. `value_area_acceptance_2026-11-05`
- **Files:** `accept80.py`, `RESULT.md`
- **PRE_REG present (N):** No `PRE_REG*.md` file exists; `MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md:1` is the result file.
- **Git log:** `b4e80f81c` (`2026-11-05T18:50:07+05:30`) added `RESULT.md` and `accept80.py`.

### 4. `auction_forward_2026-11-09`
- **Files:** `forward_log.py`, `test_forward_log.py`
- **PRE_REG present (N):** No `PRE_REG*.md` file exists; `MyTradingSys/research/auction_forward_2026-11-09/forward_log.py:1` is the logger module.
- **Git log:** `0753ff25d` (`2026-11-09T06:54:35+05:30`) re-landed `forward_log.py` and `test_forward_log.py` (no results file).

### 5. `mtf_lead_lag_2026-11-09`
- **Files:** `lead_lag.py`, `PRE_REG.md`, `REPORT.md`, `RESULT_dev.json`, `RESULT_val.json`, `test_lead_lag.py`
- **SOURCED/OURS labels (PARTIAL):** `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:15` ("Malkan's 40/60 lines (SOURCED).") uses `SOURCED`, but `OURS` does not appear anywhere in `PRE_REG.md` (e.g., WaveTrend 10/21, 7-day lead window, R1–R3 rules in `:16-18` are unlabeled).
- **Frozen split (Y):** `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:7` ("Regime: DEV 2019-11-08 .. 2023-12-31 pooled; VALIDATION 2024-01-01 .. 2026-11-07 opened once, after DEV rules are frozen in the DEV commit.") and `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:3` ("Frozen by B (JIS-NUC, Claude Opus) on 2026-11-08 before any lead-lag number was computed.").
- **n floor (N):** No minimum `n` floor specified in `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:23` ("Lead table per TF pair (n, median, IQR, share with a lead)").
- **Kill criterion (Y):** `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:25-27` ("## Kill line" and "A rule is a lead only if its VALIDATION hit rate beats the base rate of a 1d flip in any random 7-day window by 10 points or more, and its fee-net forward return beats the baseline at 3 days by more than 2 SE.").
- **## Context (Y, 4/4):** `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:5-10` has `- Regime:` (`:7`), `- Phase:` (`:8`), `- Session:` (`:9`), `- Entry:` (`:10`).
- **Git log (Y):** `PRE_REG.md` committed in `719a0b214` (`2026-11-09T03:01:17+05:30`), predating `RESULT_dev.json` (`5f27287b6`, `2026-11-09T03:01:30+05:30`), `RESULT_val.json` (`d86001f21`, `2026-11-09T03:01:57+05:30`), and `REPORT.md` (`fd6c0daf7`, `2026-11-09T03:02:58+05:30`).

### 6. `tom_swing_2026-11-09`
- **Files:** `extract_M7ompiwv5co.md`, `NOT_IN_DATA.md`, `PRE_REG.md`, `TRENDLINE_MAPPING.md`
- **SOURCED/OURS labels (Y):** `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:25-41` labels P01–P17 with `**OURS**` / `**SOURCED**`, e.g. `:25` ("**OURS**") and `:26` ("**SOURCED** (`1d`) + **OURS** (`4h`)").
- **Frozen split (N):** No DEV/VALIDATION/HOLDOUT split; `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:25` uses `2017-08-17` to `2026-11-08` and `:61-64` list `2017–2026` as one window.
- **n floor (Y):** `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:39` ("Sample Size Target") and `:61-64` (`Target Sample Size (n)` `>= 200` for 4h cells, `>= 100` for 1d cells).
- **Kill criterion (N):** No kill line or refutation rule in `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:8` ("Specification and Pre-Registration only; **no backtest execution or live orders in this card**.").
- **## Context (Y, 4/4):** `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:12-17` has `- **Regime:**` (`:14`), `- **Phase:**` (`:15`), `- **Session:**` (`:16`), `- **Entry:**` (`:17`).
- **Git log:** `PRE_REG.md` committed in `b9c4bf568` (`2026-11-10T19:40:04+05:30`); no results file exists yet.

### 7. `us_open_first3m_2026-11-11`
- **Files:** `RESULT.md`, `results.json`, `study.py`
- **PRE_REG present (N):** No `PRE_REG*.md` file exists; `MyTradingSys/research/us_open_first3m_2026-11-11/RESULT.md:1` is the result file.
- **Git log:** `6bd8eb5ca` (`2026-11-11T20:21:02+05:30`) added `RESULT.md`, `results.json`, and `study.py`.

### 8. `with_trend_session_2026-11-11`
- **Files:** `PRE_REG.md`, `result_a.json`, `RESULT_A.md`, `shape_b_census.py`, `SHAPE_B_COUNTS.md`, `SHAPE_B_RESULT.md`, `test_shape_b_census.py`, `test_with_trend_census.py`, `with_trend_census.py`
- **SOURCED/OURS labels (Y):** `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:3` ("Labels: SOURCED = cited, OURS = chosen here, frozen.") and `:16-28` label each Shape A item `OURS` or `SOURCED`.
- **Frozen split (Y):** `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:1` ("frozen 2026-11-11 before any return is computed"), `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:6` ("7 years pooled (2019-11-08 .. 2026-11-10)"), and `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:33` ("DEV 2022-01-01 .. 2024-06-30 ONLY (HOLDOUT from 2025-07 and VALIDATION 2024-07..2025-06 never loaded).").
- **n floor (Y):** `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:38` ("n < 100 in a cell = INCONCLUSIVE, never a pass.") and `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:33` ("if n < 30 on DEV: stop, Shape B goes to the testnet-forward slot with no return computed, and the result says INSUFFICIENT n.").
- **Kill criterion (Y):** `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:37-38` ("## Kill line (Shape A, per session and pooled)") and `:34` ("Refuted if any: arm A or B net R <= 0 maker; taker net R <= 0; not beating the trigger alone by 1 SE; not beating the random entries; (testnet: net R <= 0 after 30 trades).").
- **## Context (Y, 4/4):** `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md:5-9` has `- Regime:` (`:6`), `- Phase:` (`:7`), `- Session:` (`:8`), `- Entry:` (`:9`).
- **Git log (Y):** `PRE_REG.md` committed in `a89bb7f40` (`2026-11-11T21:18:38+05:30`), predating `RESULT_A.md`, `SHAPE_B_COUNTS.md`, `SHAPE_B_RESULT.md`, and `result_a.json` (`8601c65fb`, `2026-11-11T21:29:06+05:30`).
