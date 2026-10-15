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
