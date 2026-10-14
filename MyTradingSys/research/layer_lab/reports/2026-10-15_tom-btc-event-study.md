# Tom BTC event study (2026-10-15)

**BLOCKED - no per-concept outcome estimates were produced.**

## What was checked

- `MyTradingSys/research/tom_btc_2026-10-13/charts/index.csv` contains 80 blind chart IDs; `charts/_key.csv` maps them to candidate/random moments. Neither file contains concept marks or stop/target annotations. The directory has no eye-read marks CSV. The chart-lab report records 105 candidates and 80 sampled charts (60 candidates + 20 random): `MyTradingSys/research/layer_lab/reports/2026-10-13_tom-btc-chart-lab.md:3-10`.
- T3 requires two readers' marks for take/skip, concept visibility, stop and target, blinded from outcomes; T4 calls for outcomes on the marked set and all DEV candidates: `MyTradingSys/research/tom_btc_2026-10-13/TOM_ON_BTC.md:130-137`.
- A-P10 is retail derivative sentiment, explicitly `NOT_IN_DATA`: `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:79` (concept row; heading/table at lines 68-79). Its separate data gap is also listed in `TOM_ON_BTC.md:133-134`.
- BTC DEV is 2024-12-01..2025-03-31; VALIDATION and HOLDOUT were not opened: `MyTradingSys/research/tom_btc_2026-10-13/TOM_ON_BTC.md:121-128`.
- Fees are available read-only: `MyTradingSys/backtest/fees.py:12-17, 20-24`. The spec defines the all-taker 0.40% minimum stop and maker-in 0.20% fee floor: `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:313-330`.

## Findings

| Severity | File:line | Result | Evidence / blocker | Proposed fix |
|---|---|---|---|---|
| HIGH | `charts/index.csv`; `charts/_key.csv` | NOT_IN_DATA | Blind chart metadata exists, but no reader concept marks, selected stop, or target annotations were present in the task tree. A per-concept split based on those annotations cannot be reconstructed from blind IDs without inventing labels. | Complete the registered T3 eye read and place both marks files in the study folder; then run T4 using the frozen annotations. |
| HIGH | `TOM_LAYER_V2_SPEC.md:79` | NOT_IN_DATA | The required A-P10 retail sentiment feature is declared unavailable in historical BTC data, so the requested table for every listed concept cannot contain an evidence-based A-P10 result. | Supply the specified Binance long/short-ratio history or register A-P10 as unavailable and revise the task's required concept set before the study. |
| LOW | `event_study.py`, `EVENT_STUDY.md` | BLOCKED | No study code, concept table, or trial rows were created; without the marks and A-P10 source, emitting a result would misstate the evidence. | Resume after the data/label dependencies above are supplied. |

No outcome calculation, pytest run, or trial was performed. No VALIDATION or HOLDOUT data was read. No `TRIAL_REGISTRY` row is claimed. The card is **not done** because T4 inputs are incomplete.
