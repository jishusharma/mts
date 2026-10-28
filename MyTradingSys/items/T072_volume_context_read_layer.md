# T072 - volume_context: time-adjusted volume read for the market guide (observation only)

Opened 2026-10-09 by MTS-2026-10-09-APP-ANA-btc-volume. Status QUEUED. Source: MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md section 5 A1.

## Scope
Add a read-only block to scripts/dev/market_guide.py (observation only; never imported by execution code; never a Tom/Fabio filter or proof).
For the newest CLOSED 4h bar and 1d bar of BTCUSDT print:
- RVadj: volume / median of the same 4h slot over the previous 20 days (1d: same weekday over the previous 8 weeks). Label SPIKE at >= 2, HEAVY at >= 1.5, DRY at <= 0.8, else NORMAL (thresholds from PRE_REG_VOLUME_2026-10-09.md section 4; NO-SOURCE-TRADER).
- Taker delta share DP = (2 x taker-buy volume - volume) / volume, with its z-score against the previous 60 bars.
- Time flags: weekend, session group (00-08 / 08-16 / 16-24 UTC), hours since the US cash open is NOT shown (DST not modelled).
- Expected next-bar range multiple for the current RVadj bucket (table from V0_RESULTS.md section 2: 1d 1.00 / 1.01 / 1.10 / 1.40 / 1.22; 4h 0.94 / 1.01 / 1.13 / 1.25 / 1.34 for buckets < 0.7 / 0.7-1.3 / 1.3-2 / 2-3 / >= 3).
- The line "descriptive, not a signal" and verdict tag NO-EDGE (direction) from scripts/dev/market_guide_verdicts.json key "volume".

## Inputs
market_data/klines/BTCUSDT_{1h}.json only has volume, not taker-buy volume: check the kline file fields first; if taker-buy is absent print DP as n/a and say so. 4h is built from 1h; 1d from 1h or the daily file.

## Tests (derive from the spec, not from code)
Copy the hand-derived cases in research/volume_2026-10-09/test_volume.py: rv_adj same-slot median (outlier among priors does not move it), delta share (2x7-10)/10 = 0.4, slot and weekend keys, no look-ahead (changing a later bar leaves earlier values unchanged). New tests must fail on a mutant (research/volume_2026-10-09/mutation_check.py shows the method).

## Out of scope
Any rule, alert, side or position change. Weekly volume. Intraday (1m) absorption: that is T071.
