# RV-DSA ledger mechanical check (RV01 check 1) - JIS-NUC, 2026-10-18

Run-and-report only; no code or ledger edited. Ledger: TOM_TRADE_LEDGER.csv (37 rows), groups CSV, layer_index.json, layer_map.json.

| check | violations |
|---|---|
| `date` ISO-parseable when non-empty | 0 |
| non-empty `date` with ASSUMED/NOT_IN_DATA/UNKNOWN trade_date_status | 0 |
| empty `date` AND empty `trade_date_inferred` | 9: T5, T6, T7, T5-m1, T5-p1, T5-a1, T10, T10-a1, T7-m1 |
| canonical group with >1 date (date or inferred) | 0 |
| ENTRY geometry (short: target<entry<stop; long: stop<entry<target) | 0 violated; 1 unparseable: T6 (stop and target are `n/s`) |
| group n_rows / member ids vs groups CSV | 0 mismatches; 0 rows without a group |
| frame pointers exist (68 checked; bare names resolved against sibling path) | 1: T3b-x `sheets/ujedEcmvBMk_02.jpg (cells t=460-520)` - pointer carries a trailing annotation; the file itself exists |
| layer_index.json paths (80) | 0 missing |
| layer_map.json paths (42) | 0 missing (paths are relative to MyTradingSys/) |

Script: scratch only, not committed.
