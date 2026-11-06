# COUNT before outcome (card backtest-pre-us-failed-break-dev-run, run_dev.py --count)

Written and committed BEFORE any outcome column was computed (PRE_REG section 7).
Regime mix: 130 weeks DEV: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)
- primary cell (window 07-13Z): episodes n = 235 (signal days 235, signals 322, skipped 0), DEV 912 days, first 5 ineligible, 0 missing minutes.
- variant window end 12:00: n = 188.
- N_min = 250, so the primary cell is INCONCLUSIVE by section 7 regardless of any outcome (n 235 < 250). The full run still prints every cell, descriptive only.
