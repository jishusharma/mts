# Session momentum (T055 C2) 5m event table

**Result:** DEV 912 daily rows, 911 OK (458 long / 453 short), 1 NOT_IN_DATA; mean gross MFE 2.6997R, MAE 2.8101R. Descriptive gross excursion data, not an edge claim.

## Built
- `event_table.py` calls `session_momentum_events(bar_min=5, session_start_min=0, first_min=30, entry_min=30, min_abs=0.0)` (FORMULAS.md s15 defaults, import read only) on 5m DEV bars. Side = sign of the first-30-minute return; entry = close of the 6th bar (event bar). Forward bars start at the next 5m bar and end at 24:00 UTC of that day (session end, OURS), measured by `forward_excursion` (read only); DEV rows pass `dev_only`/`assert_dev`. Parameters are the module defaults (OURS adaptation to 24/7 BTC; the paper only sources the first-half-hour idea).
- R = ATR14, plain SMA of true range (FORMULAS.md s12), of the 1h bars closed at or before the entry bar open (needs 15 contiguous closed 1h bars).
- Missing data is NOT_IN_DATA with blank numbers: any gap in the six first-30-minute bars, any gap in the day's forward bars, or fewer than 15 contiguous closed 1h bars. The one NOT_IN_DATA row is 2022-01-01 (day 18993): the DEV slice has no 1h history before it.
- Loader slices `t` to `[2022-01-01, 2024-07-01)` before touching other arrays; VALIDATION and HOLDOUT bars were not read.
- Tests (`test_event_table.py`, 10): written first, failed on collection (no `event_table.py`); now `python -m pytest MyTradingSys/research/layer_lab/session_momentum_event_table/test_event_table.py -q -p no:cacheprovider` -> **10 passed**. They cover +0.4% long / -0.4% short / 0 none, window stops at midnight, missing first-30 bar and missing forward bar, hand MFE/MAE (long and short), R ignoring the unclosed hour, thin 1h history, and post-DEV bars dropped.
- DEV run: `python MyTradingSys/research/layer_lab/session_momentum_event_table/event_table.py --output ...events_dev.csv` -> `rows=912 ok=911 not_in_data=1 long=458 short=453 mean_MFE_R=2.6997 mean_MAE_R=2.8101`. CSV deleted after counting. `lookahead_lint.py --new`: no hits in these files.
- Registered in `scripts/dev/run_extra_tests.py` and `wiring_registry.json`; trial row in `TRIALS.md`. No live path or rule changed.
