# Tom BTC event study (2026-10-14)

**BLOCKED ? concept labels for the complete DEV candidate set are unavailable. No event outcomes or per-concept statistics were computed, and the card remains open.**

## What was checked

- `MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py:193-256` reads DEV only, detects every candidate, then samples 60 of them and 20 random moments for blind charts. The chart-lab run report records 105 candidates for DEV 2024-12-01..2025-03-31 (`MyTradingSys/research/layer_lab/reports/2026-10-13_tom-btc-chart-lab.md`, ?What was built and run?).
- `MyTradingSys/research/tom_btc_2026-10-13/charts/_key.csv` has chart identity fields (`blind_id,kind,day,anchor,decision_t`); it has no concept marks, stop or target annotations. The chart-lab report says the 80 charts are blind and has no eye-read output.
- The task requires A-C3, A-P1, A-P6, A-P3, A-P4, A-P5, A-P7, and A-P10 long/short-extreme concept splits. `TOM_ON_BTC.md` section 2.3 identifies P1/P6 as footprint concepts and P10 as retail sentiment; the chart-lab input is footprint bars and its loader reads only `orderflow_1m` (`chart_lab.py:178-190`). No P10 sentiment labels or source are part of this candidate archive.
- Source stop/fee floors are in `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:11.4`; BTC all-taker minimum width is 0.40%. `MyTradingSys/backtest/fees.py:10-28` defines the fee profiles. These were read but not applied because the event set cannot be stratified as requested.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| HIGH | `MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py:193-256` | NOT_IN_DATA | Only a 60-candidate sample and 20 random charts are rendered; the complete set of 105 has no marked concept table. | Add a blind label artifact covering all 105 candidates, with each required concept and mark provenance. |
| HIGH | `MyTradingSys/research/tom_btc_2026-10-13/charts/_key.csv` | NOT_IN_DATA | The key has only identity fields and does not contain eye-read annotations. | Supply the completed eye-read labels or a frozen, sourced mechanical labeling specification and data adequate to compute every flag. |
| HIGH | `MyTradingSys/research/tom_btc_2026-10-13/TOM_ON_BTC.md:2.3` | NOT_IN_DATA | A-P10 is retail long/short sentiment, but the chart-lab input/archive has no such series. | Supply the P10 sentiment source aligned to the full DEV candidate timestamps, or remove P10 from the preregistered study scope. |

No outcome run was made, so no trial row was added to `MyTradingSys/research/layer_lab/TRIALS.md`. Validation and holdout were not read. No `event_study.py` or `EVENT_STUDY.md` was created because the required labels are absent; inventing them would produce unsupported results. Follow-up cards: none.
