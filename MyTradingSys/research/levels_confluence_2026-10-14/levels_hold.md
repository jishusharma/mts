# LC1 levels hold — DEV result (2026-10-15)

## Verdict

**KEEP: prior_day_high, prior_day_low, prior_day_poc, naked_poc, 4h_fractal_low, 4h_fractal_high, round_1000, prior_week_high. DROP: prior_day_vah, prior_day_val, daily_open, prior_week_low. L2 reached: 83.8%.** Each KEEP family has a positive 95% day-bootstrap CI lower bound. L2 candidates are restricted to KEEP families.

## Method and data

- Input: `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-YYYY-MM.csv`, Binance BTCUSDT perpetual 1m klines. Loaded 188,640 bars from 2024-11-21 00:00 UTC through 2025-03-31 23:59 UTC. DEV outcomes include 2024-12-01 through 2025-03-31 only; earlier bars seed prior-week and 10-day levels.
- Stop width: `max(0.40% of 00:00 price, 0.10% of level)` (OURS; LC1 PLAN.md, section 1).
- Daily open is represented by the prior completed 1m bar close so the day-level builder reads no bar at or after 00:00. For each first touch per level/day, HOLD means a favorable one-width move precedes penetration by one width; BREAK means penetration occurs first; NEITHER means neither happens by UTC day end. If a bar spans both thresholds, it counts BREAK.
- Five random lines per real level, matched to absolute distance from midnight open, generated with seed `20261014`. A random line not touched during the day is NEITHER and counts as not holding in its five-line control denominator.
- Difference = real hold rate minus random hold rate. CI is 2,000 bootstrap resamples of UTC days (seed `20261014`). KEEP requires lower CI > 0; CI touching zero is DROP.
- For each touched L1, L2 is the nearest farther level on the same side of the midnight open, among all generated candidate level rows. L2 reach and later return-to-L1 are evaluated after the L1 touch.

## Family results

| Family | Touches | Hold | Random hold | Difference | 95% CI | Decision |
|---|---:|---:|---:|---:|---:|---|
| prior_day_high | 57 | 56.1% | 43.2% | +13.0 pp | [3.9, 22.1] pp | KEEP |
| prior_day_low | 60 | 63.3% | 51.3% | +12.0 pp | [2.7, 21.0] pp | KEEP |
| prior_day_poc | 81 | 58.0% | 47.9% | +10.1 pp | [1.0, 19.8] pp | KEEP |
| prior_day_vah | 77 | 50.6% | 46.0% | +4.7 pp | [-4.2, 13.0] pp | DROP |
| prior_day_val | 79 | 57.0% | 54.4% | +2.5 pp | [-7.1, 11.9] pp | DROP |
| daily_open | 121 | 54.5% | 53.4% | +1.2 pp | [-0.2, 3.3] pp | DROP |
| naked_poc | 110 | 54.5% | 43.8% | +10.7 pp | [3.2, 17.7] pp | KEEP |
| 4h_fractal_low | 287 | 57.8% | 44.5% | +13.4 pp | [8.2, 18.6] pp | KEEP |
| 4h_fractal_high | 264 | 57.6% | 41.9% | +15.7 pp | [10.4, 20.8] pp | KEEP |
| round_1000 | 322 | 56.5% | 44.6% | +11.9 pp | [7.7, 15.9] pp | KEEP |
| prior_week_high | 26 | 69.2% | 50.0% | +19.2 pp | [6.9, 32.3] pp | KEEP |
| prior_week_low | 20 | 50.0% | 34.0% | +16.0 pp | [-1.0, 34.0] pp | DROP |

## L1→L2 pairs

| L1 touched | Pairs | L2 touched before day end | L2 reached | Returned to L1 after L2 |
|---|---:|---:|---:|---:|
| All L1 touches; L2 restricted to KEEP families | 1,279 | 1,072 | 83.8% | 917 / 1,072 (85.5%) |

## Reproduction and source locations

- Run command: `python -c "import sys; sys.path.insert(0,'MyTradingSys/research/levels_confluence_2026-10-14'); from levels import levels_by_day; from levels_hold import analyze; from MyTradingSys.backtest.bt.bt_data import load_klines; import datetime as dt; start=int(dt.datetime(2024,11,21,tzinfo=dt.timezone.utc).timestamp()*1000); end=int(dt.datetime(2025,4,1,tzinfo=dt.timezone.utc).timestamp()*1000); bars=load_klines('F:/MTS/data/tom_raw',start_ms=start,end_ms=end); levels=levels_by_day(bars); dev=[b for b in bars if b['t']>=int(dt.datetime(2024,12,1,tzinfo=dt.timezone.utc).timestamp()*1000)]; result=analyze(dev,levels); print(result['families']); print('pairs',len(result['pairs']),'touches',len(result['touches'])); print('l2',sum(p['l2_touched'] for p in result['pairs'])); print('returned',sum(p['returned_l1'] for p in result['pairs']))"`.
- Value-area profile definition and hand-worked examples: `MyTradingSys/backtest/layers/FORMULAS.md:414-428`.
- Causal levels and family construction: `levels.py` (`_profile`, `levels_by_day`). Hold/random/bootstrap/pair calculations: `levels_hold.py` (`outcome`, `_bootstrap_ci`, `analyze`). Synthetic tests: `test_levels.py`.
- Verification: `python -m pytest MyTradingSys/research/levels_confluence_2026-10-14/test_levels.py -q` — **3 passed**. Pytest reported only a cache directory warning.

## Q79 addendum (2026-10-16): touch-bar look-ahead fixed, KEEP re-run on standard DEV

**Defect.** `_touch_side`/`outcome()` took the side from the touch bar's own close and credited a favourable move inside the touch bar; `event_table.py` set `side` the same way and took MFE from the touch bar. Fix: side = previous bar's close vs the level (first bar of a day: that bar's open); the touch bar gets BREAK credit only, never HOLD credit; event-table MFE is measured from the bar after the touch. Tests (red on the old code, 4 failed before the fix): `test_levels.py` (3 new), `test_event_table.py` (1 new).

**Data.** The study DEV above (2024-12..2025-03) lies inside the standard VALIDATION window (2024-07-01..2025-06-30), so it was NOT re-read. The re-run uses standard DEV only: decisions 2022-04-01..2024-06-30, seed bars from 2022-03-21, `load_klines(end_ms=2024-07-01)`, asserted. Old and new code were run on the same bars, so the two columns are comparable. Parameters unchanged: stop width `max(0.40% of 00:00 price, 0.10% of level)` OURS; seed 20261014 OURS; 2,000 day-bootstrap OURS; KEEP rule lower CI > 0 OURS. No SOURCED parameters.

| Family | n | old HOLD | old random | new HOLD | new random | new diff | new 95% CI | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| prior_day_high | 380 | 62.1% | 45.9% | 37.6% | 30.9% | +6.7 pp | [3.2, 10.2] | KEEP |
| prior_day_low | 345 | 63.2% | 46.1% | 40.9% | 33.3% | +7.6 pp | [3.9, 11.5] | KEEP |
| prior_day_poc | 583 | 52.3% | 46.6% | 52.7% | 43.9% | +8.7 pp | [5.4, 12.2] | KEEP |
| naked_poc | 732 | 53.4% | 43.8% | 53.1% | 41.4% | +11.7 pp | [8.7, 14.8] | KEEP |
| 4h_fractal_low | 1963 | 56.7% | 41.7% | 44.9% | 34.9% | +10.0 pp | [8.2, 11.8] | KEEP |
| 4h_fractal_high | 1984 | 58.5% | 43.0% | 46.3% | 36.4% | +9.9 pp | [7.9, 11.7] | KEEP |
| round_1000 | 831 | 59.7% | 42.9% | 45.0% | 35.9% | +9.1 pp | [6.7, 11.5] | KEEP |
| prior_week_high | 150 | 62.0% | 45.1% | 44.7% | 34.1% | +10.5 pp | [4.8, 16.4] | KEEP |
| prior_day_vah | 537 | 58.1% | 49.5% | 48.2% | 42.5% | +5.8 pp | [2.6, 8.9] | passes (not on list) |
| prior_day_val | 539 | 57.9% | 48.3% | 52.3% | 43.5% | +8.8 pp | [5.4, 12.2] | passes (not on list) |
| prior_week_low | 124 | 54.8% | 39.2% | 43.5% | 34.2% | +9.4 pp | [2.9, 15.6] | passes (not on list) |
| daily_open | 822 | 55.2% | 54.7% | 49.3% | 48.0% | +1.3 pp | [-1.3, 3.7] | DROP |

**Result.** All 8 KEEP families survive on standard DEV (lower CI > 0 for each). The raw HOLD rate falls 10-25 pp for the high/low/fractal/round families (the inflation); the POC families do not move, and the edge over the random-line control stays positive (+6.7 to +11.7 pp). Pairs: 8,711 L1 touches, 6,984 L2 reached, 5,913 returned to L1.

**DECISION (OURS)** D1: standard DEV instead of the study window, because the study window is VALIDATION data. D2: the KEEP list stays the original 8; prior_day_vah, prior_day_val, prior_week_low also clear the CI rule on this wider DEV but are not added (they were DROP on the first list; adding them needs one VALIDATION check, not done here). D3: first bar of a day uses its own open as the side reference (no previous bar in the day's rows). D4: `event_table.csv` and `separation.md` were built with the old rule on VALIDATION-window data and are STALE; they were not regenerated because that would read VALIDATION outcomes. Do not use their side/MFE columns.
