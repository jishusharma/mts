# RV05 [MED] Fabio ledger: frame-by-frame pass over rows the first audit did not read (24580c0)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV05. Report: `MyTradingSys/research/revalidation/RV05_<UTC date>.md`.

Scope in: MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv (72 rows), FABIO_TRADE_LEDGER.md,
MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md (+ _evidence.json), F:/MTS/data/fabio_videos.
Scope out: edits, the three HIGH repairs themselves (already carded), transcripts re-extraction.
Why: the first audit says rows not named in its findings were checked on arithmetic and provenance only, "not re-read frame by
frame". 62 images, 4 of the contact sheets were opened.
Checks: open every cited frame for the rows NOT named H1-H3/M1-M4 (list them in the report); compare entry, stop, qty, side, STP label
dollars, instrument/contract header (NQ vs ES, contract month) and any visible date or clock. MATCH/MISMATCH/NOT_IN_DATA per row.
Also: the `date` column uses `2026` or months only; list rows whose contract month contradicts the stated date (NQ-202512 expired
2025-12-19).
Already known: H1 (47 rows dated `2026` show an expired Dec-2025 contract), H2 (5 entry cells off vs STP label), H3 (F13-x outcome
-2910 vs STP -1760).
