# OI Delta Event Table

**BLOCKED — 0 local OI data files were found, so no DEV event rows or forward outcomes can be computed.** Funding files exist (78); whale data files found: 0. OI-dependent periods remain `NOT_IN_DATA`.

## Built

- `event_table.py` inventories candidate local inputs and builds a CSV table from supplied event and bar CSVs. It applies the four directional sign states recorded by the 2026-10-10 classifier, computes forward return/MFE/MAE in R, and prevents bars at or before the event timestamp from entering forward outcomes.
- Missing OI is an explicit `NOT_IN_DATA` status with blank outcome fields. Flat-sign inputs are not one of the four directional events.
- DEV window is 2022-01-01 through 2024-12-31, exclusive of 2025-01-01. No VALIDATION or HOLDOUT data is read.

## Inventory and rows

Command: `python MyTradingSys/research/layer_lab/oi_delta_event_table/event_table.py --inventory`

| Source category | Matching local files | Event rows computed |
|---|---:|---:|
| OI | 0 | 0 |
| Funding | 78 | 0 |
| Whale | 0 | 0 |

The reusable table function is covered by synthetic fixtures only. There are no empirical OI event rows to report because neither full-precision OI data nor the old snapshot/label inputs are present in this checkout. The referenced 2026-10-10 script points to `runtime_data/snapshots` and `runtime_data/outcome_labels.json` under the JIS-NB checkout; these paths are not local inputs here.

## Tests

- Red first: `python -m pytest MyTradingSys/research/layer_lab/oi_delta_event_table/test_event_table.py -q` failed at collection because `event_table.py` did not yet exist.
- Green: `python -m pytest MyTradingSys/research/layer_lab/oi_delta_event_table/test_event_table.py -q -p no:cacheprovider` → `3 passed`.
- Tests verify four labels, hand-computed R/MFE/MAE, missing OI as `NOT_IN_DATA`, and event labeling from as-of fields only.

## Findings

| Severity | Finding | Evidence | Action |
|---|---|---|---|
| HIGH | Empirical OI event table cannot be populated in this environment. | Inventory returned 0 candidate OI files; the prior study's runtime snapshots and labels are absent. | Supply the local DEV OI plus price bars before computing event rows. |
| LOW | Funding archives are present but do not substitute for OI. | Inventory returned 78 funding files and no OI files. | Keep funding separate until an OI event dataset is available. |

No trial row was added: no empirical run took place. No follow-up card was created.
