# BTC candle-close research audit

FIX-FIRST for an edge/cycle-probability claim; exploratory study is usable within its stated scope.

Checked: candle_close_2026-10-14/METHOD.md (full), RESEARCH.md (full), study.py (full), results.json (126 rows), verification.json; existing candle pilot pre-registration and 108 P1 result rows; Krown qEfES84jwwo and 14bxwxC8gBQ extracts passed quote verification. Data: Binance BTCUSDT perpetual January 2022-June 2024, 1,313,280 minute rows. External source URLs and verification scope are in RESEARCH.md.

| Severity | Evidence location | Assessment | Finding / next action |
|---|---|---|---|
| HIGH | METHOD.md:24-30; REPORT.md limitations | MATCH | First daily event versus all nearby controls differs in opportunity weighting. Do not interpret negative lift causally; independent-audit card covers a first-opportunity null. |
| HIGH | METHOD.md:35-45; RESEARCH.md bottom/top section | NOT_IN_DATA | Anonymous trader and source trade ledger unavailable; no faithful YouTube replication or cycle-bottom odds. Cycle design card defines causal labels/power; exact source remains unidentified. |
| HIGH | results.json candidates=0 and all 126 screen14_bps<0 | MATCH | No pooled candidate passes DEV screen; do not spend validation or claim a tradable edge. |
| MED | DATA_AMENDMENT.md | MATCH | Two pre-outcome failures: timestamp resolution and read-only ndarray. Both reproduced/corrected; archive has zero actual gaps. |
| MED | METHOD.md inference; REPORT.md limitations | MATCH | Seven-day block and approximate normal-Bonferroni screening are not proof of calibration; regimes/subgroups remain exploratory. |
| LOW | candle_patterns_2026-10-04/p1_results.json | MATCH | 36 daily FAIL +18 insufficient; 48 hourly FAIL +6 insufficient. Prior report's zero survivors matches complete raw rows. |

Follow-ups: candle-close-independent-audit, candle-close-cycle-labels. Full report: ../candle_close_2026-10-14/REPORT.md. No live change or holdout read.
