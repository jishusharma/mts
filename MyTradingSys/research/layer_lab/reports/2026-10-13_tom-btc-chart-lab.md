# Tom BTC chart lab (2026-10-13)

**105 candidates; 80 blind charts (60 candidates + 20 random); pytest 1 passed.**

## What was built and run

- `MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py:26-50` computes the prior calendar day's 70% value area from footprint bins; this value-area convention and all numeric thresholds are OURS.
- `MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py:81-131` scans the 4-hour windows from 00:00 UTC, 07:00 UTC, and 09:30 America/New_York; each directional extreme is checked independently, and the decision occurs on its third consecutive 1-minute non-extension. Candidate size must exceed the lower median of the prior 20 same-anchor completed legs and clear prior-day VAH/VAL.
- `MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py:134-190` renders only rows through the decision time: 5-minute candles, prior-day VAH/VAL/POC, session profile, per-bar delta, and footprint text for the three highest-volume visible bars. The chart labels OURS values and the 4-hour, prior-20, 70%-value-area, and third-stall rules.
- `MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py:193-256` loads DEV rows only, samples 60 candidates and 20 same-window random moments with seed 20261013, then writes blind chart IDs and a separate key.
- Data command: `python MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py` against `F:\MTS\data\orderflow_1m` (read-only), DEV 2024-12-01..2025-03-31. Archive coverage is 120/121 calendar days: 2024-12-02..2025-03-31; 2024-12-01 is missing. Dec 1 and Dec 2 have no prior-day profile warm-up; the following 119 DEV days have a prior date in the archive.
- Result: `candidates=105 sampled=60 random=20 per_anchor={'00:00': 35, 'US_CASH': 40, '07:00': 30} charts=80`. Outputs: `MyTradingSys/research/tom_btc_2026-10-13/charts/` contains 80 PNGs, `index.csv` has 80 blind IDs, and `_key.csv` has 80 mappings.
- Test: `python -m pytest MyTradingSys/research/tom_btc_2026-10-13/test_chart_lab.py -q` -> `1 passed`. Before implementation, the same test failed to collect with `ModuleNotFoundError: No module named 'chart_lab'`. The passing synthetic case verifies the third stall bar and that the last plotted 1-minute constituent is the decision bar. Pytest emitted a cache-directory warning from the existing `.pytest_cache`; the test passed.

## Findings

| Severity | File:line | Result | Evidence | Follow-up |
|---|---|---|---|---|
| LOW | `F:/MTS/data/orderflow_1m` | MATCH | 120 DEV date files exist; 2024-12-01 is absent. The configured window begins on that date (`TOM_ON_BTC.md:121`). | None |
| LOW | `charts/` | MATCH | 80 PNGs, 80 index rows, and 80 key rows verified by counting files/CSV records. The index contains only blind IDs and filenames. | None |
| LOW | `test_chart_lab.py:13-31` | MATCH | Test passed and asserts decision timing plus no plotted constituent after the decision bar. | None |

No validation or holdout data was opened. No backtest or outcome calculation was run. Follow-up cards: none.
