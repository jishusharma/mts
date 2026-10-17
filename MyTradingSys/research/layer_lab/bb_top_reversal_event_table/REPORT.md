# BB top-reversal 15m event table

**Result:** 1,577 DEV events; 1,577 have complete 16-bar forward windows. The table is descriptive gross excursion data, not an edge claim.

## Built

- `event_table.py` computes population-standard-deviation BB(20,2) from the green candle's 20 closes, then requires green close > open and high >= upper band; the next consecutive 15m candle must be red and close below the green open. These setup flags use no later candles. Entry is the following bar open. OURS R is red high minus entry; short MFE is (entry - minimum forward low)/R and MAE is (maximum forward high - entry)/R over 16 bars including the entry bar. Incomplete or invalid forward windows are `NOT_IN_DATA`.
- The NPZ reader filters timestamps to `[2022-01-01, 2024-07-01)` before returning OHLC bars; no later bars were read for this run. Source: `F:/MTS/data/bigtrade/cache/perp/klines_15m.npz`.
- `test_event_table.py` covers hand-derived upper band and R, above-open red rejection, below-band green rejection, and setup causality. The test was run before implementation and failed because `event_table.py` did not exist; after implementation: `python -m pytest MyTradingSys/research/layer_lab/bb_top_reversal_event_table/test_event_table.py -q -p no:cacheprovider` -> **4 passed**.
- DEV run: `python MyTradingSys/research/layer_lab/bb_top_reversal_event_table/event_table.py --output MyTradingSys/research/layer_lab/bb_top_reversal_event_table/events_dev.csv` -> **bars=87552 events=1577 labeled=1577 not_in_data=0**. Mean gross MFE = **2.7692R**; mean gross MAE = **3.0843R**. Temporary event CSV was removed after counting. Trial recorded in `MyTradingSys/research/layer_lab/TRIALS.md`.
- Test registered in `scripts/dev/run_extra_tests.py`; tool registered in `MyTradingSys/system/wiring_registry.json`. No live path or rule was changed. VALIDATION and HOLDOUT were not read.
