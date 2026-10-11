# FROZEN tom_core_20260929

git HEAD: 27dceb64a123414ed8d643dd927828f08fccdbda (branch fast-track); working tree not committed at run time
SetupCandidatesBuilder.java sha256[:16]: c112e6c289f9b1b0
verdict.py: 5e239693168a8dcf | tom_bt.py: dbae498e4b5493c2 | tom_bt_run.py: 3c923b2979d7cdfb | l1_patch_mds.py: 5cfd589daa8653e2
Archive adapter (staged .new, compiled in %TEMP% only): ArchiveHistoricalSource.java.new 1f3e7e7ca5b35e5d; MarketDataSnapshot.java.archive_mode.new c2cccda06f852b85
Rules: Tom core unchanged (D1/D3/D4 rulings as committed); verdict.py fail_closed proof direction; no fitted parameters
(walk-forward has nothing to fit: every month is out-of-sample by construction; the split below is descriptive).
Signals: rank-1 candidate; entry limit at zone price; stop/target from math; order life and time exit 8 zone-tf bars;
zone tf = SetupCandidatesBuilder.getSwingTF; one position at a time; stop-first on ambiguous bars.
Fees: entry/target maker 0, stop/timeout taker 0.0005 (Deribit BTC-PERPETUAL as in sim.py); stress: 0.0005 on every fill,
5 bps extra slippage on stop/timeout, target-first ambiguity. Funding not modelled (hold <= 8 zone bars).
Splits: hist 2022-01-20..2025-08-31 | dev 2025-09-01..2026-06-25 | HOLDOUT 2026-06-26..2026-09-26 (run once, this run).
Fabio tags: L1 IS-best frozen params (FABIO_L1_REPORT.md), descriptive only.

## NOTE 2026-10-09 (B147)
HOLDOUT 2026-06-26..2026-09-26 was read TWICE for Tom (this run and tom_core_20261007). It is burned for Tom: any further Tom result on it is not out-of-sample. Treat the live rule as 'insufficient N' until B147 attribution of the 120,892 to 90,699 row drop is done.
