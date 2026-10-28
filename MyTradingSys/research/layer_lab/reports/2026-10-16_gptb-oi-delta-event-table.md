# BLOCKED — OI data unavailable locally

The synthetic event-table implementation is present and its tests pass, but the requested empirical DEV table cannot be populated: local inventory found 0 OI files, 78 funding files and 0 whale files. Missing OI remains `NOT_IN_DATA`; there are zero empirical rows.

## Checked

- Inventory command: `python MyTradingSys/research/layer_lab/oi_delta_event_table/event_table.py --inventory` -> `oi: []`, 78 funding candidates, `whale: []`.
- Test command: `python -m pytest MyTradingSys/research/layer_lab/oi_delta_event_table/test_event_table.py -q -p no:cacheprovider` -> `3 passed`.
- The 2026-10-10 study source is read-only; it points to `runtime_data/snapshots` and `runtime_data/outcome_labels.json` in its `SNAPS` and `LABELS` assignments. These inputs are unavailable in this checkout.
- Implementation: `MyTradingSys/research/layer_lab/oi_delta_event_table/event_table.py` (`inventory`, `classify`, `build_event_table`). Test registration: `scripts/dev/run_extra_tests.py` (`EXTRA`). Wiring: `MyTradingSys/system/wiring_registry.json` (REPRO entry).

## Findings

| Severity | Finding | Evidence | Action |
|---|---|---|---|
| HIGH | Empirical OI event rows and forward outcomes cannot be calculated here. | Inventory command returned zero OI candidates; prior-study raw snapshots and outcome labels are missing. | Supply local DEV OI and aligned price bars, then rerun. |
| LOW | Synthetic logic checks pass. | Test command returned `3 passed`, covering four labels, hand-computed R/MFE/MAE, missing OI, and as-of labeling. | Preserve the current test coverage. |
| MED | The required red-first run is not evidenced by this session. | The module and test file were already present at task start; the draft's earlier collection-failure claim cannot be independently confirmed. | Record the limitation; do not claim red-first completion. |

No empirical trial was run and no `TRIALS.md` row was added. Per the task's blocked-input instruction, the card was not marked done. No shipping or release is claimed.
