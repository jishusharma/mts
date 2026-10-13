# RV01 [HIGH] Tom ledger repairs (2868d6c, 2979309, 4ceb46c)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV01. Report: `MyTradingSys/research/revalidation/RV01_<UTC date>.md`.

Scope in: MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv (37 rows, 27 columns), TOM_TRADE_LEDGER.md,
TOM_LEDGER_CANONICAL_GROUPS.csv, MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md (+ _evidence.json),
frames F:/MTS/data/tom_videos (frames, sheets, captions).
Scope out: any edit, split manifest, holdout, DAX backtest.
Why risky: the ledger is the only evidence base for the Tom v2 spec (Opus); three repair commits rewrote 76 rows in one day,
and the repair cards were closed by the same model that wrote the ledger. The frame audit said 4 HIGH + 4 MED.
Checks:
1. Mechanical (script it, print the counts): ISO-parseable `date` per row; `date` vs `trade_date_status` / `trade_date_inferred` (a
   NOT_IN_DATA or ASSUMED status must not leave a plain ISO date a consumer would treat as fact); same-canonical-group rows share
   one trade date; side vs stop/target geometry per ENTRY row (short: target < entry < stop); group counts vs
   TOM_LEDGER_CANONICAL_GROUPS.csv n_rows; every frame pointer exists on disk.
2. Provenance: for each of the 10 rows whose note or evidence_unresolved says "CORRECTED", "frame-observed" or "INFERRED", open the
   cited frame and compare entry/stop/target/qty with the label on the chart.
3. Repair fidelity: for every HIGH/MED in the frame audit report, check the CSV row now states the fix (cite audit ID -> CSV id).
4. Counts: 37 rows / 12 canonical groups / T8 is a candidate only: recompute from the CSV, compare to the .md header text.
Already known (confirm or refute): (a) `date` column holds prose for T9, T10, T11 and an ISO date for T5, T6, T7 although
trade_date_status is NOT_IN_DATA; (b) T6 date 2026-06-02 vs T10 (same group) 2026-06-08; (c) T11 UNRESOLVED but T11-x 2026-09-01;
(d) T1 initial stop 24485 is 4 points, flagged "moved" but initial SL unrecorded; (e) CSV `side` holds action words on management rows
(T12-m1 `stop_tighten`).
