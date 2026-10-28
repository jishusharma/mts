# BLOCKED — G2 DAX ASK candles

BLOCKED — the required spread measurement cannot be produced under the supplied data-access rule.

## Work completed

- Added BID-default / ASK-selectable Dukascopy URLs and fetching, ASK-compatible BI5 parsing, exact `open_ms` spread pairing, and a `spread` CLI subcommand in `MyTradingSys/backtest/dax_data.py:30-145`.
- Added ASK URL/parse/filler and exact-time/no-forward-fill tests in `MyTradingSys/backtest/test_dax_data.py:36-50`. They failed on the original code (3 failed, 4 passed), then passed after implementation.
- The test is already registered in `scripts/dev/run_all_tests.py:56`.
- Verification: `python -m pytest MyTradingSys/backtest/test_dax_data.py -q` → 7 passed (one pytest cache warning).

## Blocker

The task requests DAX observations from 2024-11-04 through 2026-04-10, but the controlling instruction says: “Only DEV bars (open before 2024-07-01) may be read; slice them out, never inspect later bars.” These requirements conflict, so I did not read DAX bar contents from the requested later period. The ASK raw archive is not present in the known data location (`F:/MTS/data/dax_raw_ask`); an authorized one-day Dukascopy ASK request was also denied by the sandbox with `WinError 10013` (socket access forbidden). Consequently no valid DEV spread observations, `spreads.csv`, or `SPREADS.md` can be produced, and the card must remain open.

Reference: `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md:17-18` specifies the preregistered DEV range and frozen cost assumptions; `MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:236-244` contains the prior 10-day reference table (1.15 / 1.65 / 2.65 pt). That prior table is not a substitute for the requested fresh DEV sample.

## Cost-table proposal

No new OURS (measured) cost-table row is proposed because the requested sample could not be measured. The existing G2 figures are SOURCED to the reference above and remain a prior result only; `PRE_REG_DAX.md` was not edited.

## Follow-up cards

None.
