# LC1 levels hold — DEV result (2026-10-15)

> **SUPERSEDED 2026-10-28 (T05-F5): the KEEP list below and in the Q79 addendum is void. On the touched-only distance-matched control 0 of 12 families are KEEP (see the last section). Do not use the 8-family list as a prior.**

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

## T05-F5 re-statement (2026-10-28): fair control, KEEP list is EMPTY

**Defect (T05-F5, confirmed).** The published control placed each random line at midnight open +/- the real level's own distance, so about half of the 5 lines ARE the real level (measured 0.49-0.51 for 11 families; 0.77 for daily_open), and a control line never touched in the day counted as a non-hold in the denominator (measured 32-85% of lines untouched for 11 families), which deflates the control hold rate. A real level is only scored when touched, so the two sides were not like for like.

**Fix.** `levels_hold.py` now decides on the touched-only distance-matched control: for every candidate level (touched or not) 20 random lines (OURS), distance drawn from the pool of the same family's candidate-level distances in the same calendar month, sign random, a line counts only if touched, hold rate = holds / touches. Verdict rule unchanged (lower 95% day-bootstrap CI of real minus control > 0 = KEEP; 2,000 resamples). `analyze()` keeps the published control as `legacy_*` columns (`legacy_random_hold_rate`, `legacy_difference`, `legacy_ci95`, `legacy_verdict`, `legacy_equal_real_share`, `legacy_untouched_share`); `random_hold_rate`, `difference`, `ci95`, `verdict` are now the fair control. `pairs` is restricted to the fair KEEP set, so it is empty. Tests: `test_levels_hold_fair.py` (red before the change: ImportError on the new helpers; green after), `test_levels.py`, `test_event_table.py`, `test_ladder.py` all pass (21).

**Data and parameters.** Standard DEV only: decisions 2022-04-01..2024-06-30, seed bars from 2022-03-21, `load_klines(end_ms=2024-07-01)` asserted; no VALIDATION or HOLDOUT read. Run: `python MyTradingSys/research/levels_confluence_2026-10-14/levels_hold_fair_run.py` -> `lc1_fair_dev.csv`. Parameters (all OURS, none SOURCED): stop width `max(0.40% of 00:00 price, 0.10% of level)`; 20 fair lines per level; month x family distance pool; fair seed 20261016 (T05 audit seed); legacy seed 20261014; 2,000 bootstrap; KEEP rule lower CI > 0. All 12 rows equal `dsa_backtest_audit_2026-10-16/scripts/T05/out/lc1_fair.csv` (counts exactly, rates and CIs to 1e-9; 0 mismatches).

| Family | Touches | Hold | Fair ctl touches | Fair ctl hold | Diff (pp) | 95% CI (pp) | Verdict | Legacy diff (pp) / verdict | Legacy ctl = real level / untouched |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| prior_day_high | 380 | 37.6% | 7978 | 49.5% | -11.9 | [-16.5, -7.1] | DROP | +6.7 KEEP | 0.51 / 0.53 |
| prior_day_low | 345 | 40.9% | 7825 | 49.7% | -8.8 | [-14.1, -3.7] | DROP | +7.6 KEEP | 0.50 / 0.57 |
| prior_day_poc | 583 | 52.7% | 11059 | 51.1% | +1.6 | [-2.3, +5.5] | DROP | +8.7 KEEP | 0.50 / 0.32 |
| prior_day_vah | 537 | 48.2% | 10597 | 50.7% | -2.4 | [-6.6, +1.8] | DROP | +5.8 KEEP | 0.50 / 0.35 |
| prior_day_val | 539 | 52.3% | 10428 | 50.9% | +1.4 | [-2.8, +5.4] | DROP | +8.8 KEEP | 0.49 / 0.37 |
| daily_open | 822 | 49.3% | 16436 | 49.4% | -0.1 | [-3.1, +2.8] | DROP | +1.3 DROP | 0.77 / 0.00 |
| naked_poc | 732 | 53.1% | 14797 | 50.6% | +2.6 | [-0.8, +6.1] | DROP | +11.7 KEEP | 0.51 / 0.65 |
| 4h_fractal_low | 1963 | 44.9% | 41989 | 50.0% | -5.1 | [-7.3, -2.6] | DROP | +10.0 KEEP | 0.50 / 0.71 |
| 4h_fractal_high | 1984 | 46.3% | 42037 | 49.8% | -3.5 | [-5.9, -1.0] | DROP | +9.9 KEEP | 0.50 / 0.71 |
| round_1000 | 831 | 45.0% | 16595 | 50.3% | -5.3 | [-8.3, -1.8] | DROP | +9.1 KEEP | 0.50 / 0.59 |
| prior_week_high | 150 | 44.7% | 2784 | 50.1% | -5.4 | [-13.5, +2.6] | DROP | +10.5 KEEP | 0.50 / 0.82 |
| prior_week_low | 124 | 43.5% | 2866 | 48.2% | -4.6 | [-13.1, +3.7] | DROP | +9.4 KEEP | 0.49 / 0.85 |

**KEEP list (DEV 2022-04-01..2024-06-30, fair control): none. The published 8 (prior_day_high, prior_day_low, prior_day_poc, naked_poc, 4h_fractal_low, 4h_fractal_high, round_1000, prior_week_high) all lost; no family gained.** Five families hold LESS often than their matched control with the whole CI below zero (prior_day_high, prior_day_low, 4h_fractal_high, 4h_fractal_low, round_1000); the other seven straddle zero.

**DECISION (OURS) D5:** the fair control's distance pool includes the real level's own distance (as in the T05 reference, so the numbers match its csv); the chance a fair line equals the real level is 0.2-1.8% for 11 families, and 39.7% for daily_open (its distance is 0 every day, so the pool is degenerate; DROP either way). **D6:** `event_table.csv`, `separation.md`, `ladder_dev.md` and the 8-family `KEEP` sets in `event_table.py`, `ladder_run.py`, `live_levels_confluence.py` and the imbalance filter were built on the voided list; they are not edited here and each has a re-point card (ref re-state-lc1-keep-list-on-the-touched-on).

**Independent re-derivation (2026-10-28, Opus builder on DESKTOP-F7IU69N, separate implementation written before this section landed).** A second port of the fair control (own code, own data fetch: Binance USD-M BTCUSDT 1m monthly klines from public data.binance.vision, 1,199,520 bars / 1,183,680 decision bars, the same counts as T05) reproduced `T05/out/lc1_fair.csv` exactly: 12 families x 12 fields (touches, rates, diff, CI bounds, verdict, legacy diagnostics; legacy random rate and verdict against `lc1_orig_reproduction.csv`), 0 mismatches. In that run 9,600 of 494,840 fair lines (1.9%) equal the real level (D5). Strict variant, a line equal to the real level redrawn (up to 100 tries, 0 equal lines left): verdict still DROP for all 12, KEEP none; fair diff moves by at most 1.6 pp (prior_week_high -3.9 [-11.7, +4.6], prior_week_low -6.1 [-15.1, +2.5], prior_day_poc +2.7 [-1.2, +6.7], naked_poc +2.7 [-0.7, +6.2]; the five CI-below-zero families stay below zero). So D5 does not move the result. `dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py` now reads the published-run columns through `legacy_*` (they moved there), so a rerun of the audit script still reproduces the published run.
