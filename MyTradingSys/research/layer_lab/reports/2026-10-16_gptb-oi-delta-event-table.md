# BLOCKED — OI data unavailable locally

The four-state DEV event-table implementation and its synthetic tests are complete, but empirical rows cannot be produced: the local inventory found 0 OI files, 78 funding files and 0 whale files. The OI-dependent period is `NOT_IN_DATA`; the card is not marked done.

| Severity | Finding | Evidence | Action |
|---|---|---|---|
| HIGH | Empirical OI event rows and forward outcomes are unavailable. | `python MyTradingSys/research/layer_lab/oi_delta_event_table/event_table.py --inventory` returned `oi: []`; prior study source points to JIS-NB `runtime_data/snapshots` and `outcome_labels.json`. | Provide DEV OI and aligned price bars, then rerun this table. |
| LOW | Synthetic implementation tests pass. | `python -m pytest MyTradingSys/research/layer_lab/oi_delta_event_table/test_event_table.py -q -p no:cacheprovider` → `3 passed`. | No code change required for the tested behaviors. |

Files: `oi_delta_event_table/event_table.py`, `test_event_table.py`, `REPORT.md`; test registration in `scripts/dev/run_extra_tests.py`; REPRO declaration in `system/wiring_registry.json`. The referenced 2026-10-10 study is read-only. No trial row was added because no empirical run occurred.

Follow-up cards: none.
