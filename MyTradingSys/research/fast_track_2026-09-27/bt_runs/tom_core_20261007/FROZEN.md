# FROZEN tom_core_20261007

git HEAD: 533497596cfe5ec9e600fce8d1caf67e1c27e046 (branch research/agenda-2026-10-06); working tree not committed at run time
SetupCandidatesBuilder.java sha256[:16]: d749117a809608ff
verdict.py: 1f6d3b004931e5dd | tom_bt.py: b6ca98235859a80f | tom_bt_run.py: 3c923b2979d7cdfb | l1_patch_mds.py: 5cfd589daa8653e2
Archive adapter (compiled in %TEMP% only): ArchiveHistoricalSource.java f44d1674e5d1e4d7; MarketDataSnapshot.java 2bfe7333976972af
Rules: Tom core unchanged (D1/D3/D4 rulings as committed); verdict.py fail_closed proof direction; no fitted parameters
(walk-forward has nothing to fit: every month is out-of-sample by construction; the split below is descriptive).
Signals: rank-1 candidate; entry limit at zone price; stop/target from math; order life and time exit 8 zone-tf bars;
zone tf = SetupCandidatesBuilder.getSwingTF; one position at a time; stop-first on ambiguous bars.
Fees: entry/target maker 0, stop/timeout taker 0.0005 (Deribit BTC-PERPETUAL as in sim.py); stress: 0.0005 on every fill,
5 bps extra slippage on stop/timeout, target-first ambiguity. Funding not modelled (hold <= 8 zone bars).
Splits: hist 2022-01-20..2025-08-31 | dev 2025-09-01..2026-06-25 | HOLDOUT 2026-06-26..2026-09-26 (run once, this run).
Fabio tags: L1 IS-best frozen params (FABIO_L1_REPORT.md), descriptive only.
