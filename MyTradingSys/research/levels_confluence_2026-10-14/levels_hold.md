# LC1 levels hold — DEV result (2026-10-15)

## Verdict

**CURRENT (2026-10-28, T05-F5 re-statement, section at the end): KEEP none of 12 on the touched-only, distance-matched fair control (standard DEV 2022-04-01..2024-06-30). The 8-family list below and in the Q79 addendum came from an unfair control and is withdrawn.**

Superseded first verdict (2026-10-15, legacy control): **KEEP: prior_day_high, prior_day_low, prior_day_poc, naked_poc, 4h_fractal_low, 4h_fractal_high, round_1000, prior_week_high. DROP: prior_day_vah, prior_day_val, daily_open, prior_week_low. L2 reached: 83.8%.** Each KEEP family has a positive 95% day-bootstrap CI lower bound. L2 candidates are restricted to KEEP families.

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

## T05-F5 re-statement (2026-10-28): fair control, KEEP list = none

**Defect (T05-F5, `dsa_backtest_audit_2026-10-16/T05_placebo_nulls.md` sections 3 and 5).** The published control drew midnight +/- the level's own distance with a random sign, so about half the control lines ARE the real level, and a control line never touched in the day counted as a non-hold, which pulls the control hold rate down and inflates the difference.

**Fix (`levels_hold.py` `fair_control`, verdict column).** For every candidate level of a family (touched or not), 20 lines whose distance from the midnight open is drawn from the same family's distances in the same calendar month, random sign; a line equal to the real level is redrawn (up to 100 tries); a line counts only when touched (control hold rate = holds / touched lines, like the real levels). Same HOLD rule, stop width and 2,000-draw ratio-of-sums day bootstrap; KEEP = lower 95% CI > 0. The published control stays as legacy columns (`random_hold_rate`, `difference`, `ci95`, `legacy_verdict`). Test: `test_levels_hold_fair.py` (hand fixture; red on the old code with KeyError on the missing fair columns, green now).

**Data.** Standard DEV only: decisions 2022-04-01..2024-06-30, seed bars from 2022-03-21, `end_ms` 2024-07-01 asserted; Binance USD-M BTCUSDT 1m monthly klines (public data.binance.vision, 1,199,520 bars, 1,183,680 decision-window bars, the same counts as the T05 run). Levels built per day from a 14-day window (`t05_lc1.windowed_levels`). VALIDATION and HOLDOUT not read.

**Reproduction check.** `analyze(..., exclude_real=False)` reproduces `dsa_backtest_audit_2026-10-16/scripts/T05/out/lc1_fair.csv` exactly: 12 families x 12 fields (touches, rates, diff, CI bounds, verdict, legacy diagnostics, legacy random rate and verdict vs `lc1_orig_reproduction.csv`), 0 mismatches. In that mode 9,600 of 494,840 control lines (1.9%) equal the real level; the final run below redraws them (0 equal).

| Family | n | HOLD | legacy random | legacy diff pp | legacy CI rule | fair ctl lines touched | fair ctl HOLD | fair diff pp | fair 95% CI pp | verdict | T05 csv (no redraw) | legacy draws = real / untouched |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---|---|
| 4h_fractal_high | 1984 | 46.3% | 36.4% | +9.9 | KEEP | 42056 | 49.9% | -3.6 | [-6.0, -1.2] | DROP | -3.5 [-5.9, -1.0] DROP | 50% / 71% |
| 4h_fractal_low | 1963 | 44.9% | 34.9% | +10.0 | KEEP | 42023 | 50.0% | -5.2 | [-7.4, -2.7] | DROP | -5.1 [-7.3, -2.6] DROP | 50% / 72% |
| daily_open | 822 | 49.3% | 48.0% | +1.3 | DROP | 16436 | 50.0% | -0.7 | [-5.0, +3.5] | DROP | -0.1 [-3.1, +2.8] DROP | 76% / 0% |
| naked_poc | 732 | 53.1% | 41.4% | +11.7 | KEEP | 15003 | 50.5% | +2.7 | [-0.7, +6.2] | DROP | +2.6 [-0.8, +6.1] DROP | 50% / 65% |
| prior_day_high | 380 | 37.6% | 30.9% | +6.7 | KEEP | 7876 | 49.4% | -11.7 | [-16.4, -7.2] | DROP | -11.9 [-16.5, -7.1] DROP | 49% / 52% |
| prior_day_low | 345 | 40.9% | 33.3% | +7.6 | KEEP | 7723 | 50.1% | -9.2 | [-14.1, -4.0] | DROP | -8.8 [-14.1, -3.7] DROP | 51% / 56% |
| prior_day_poc | 583 | 52.7% | 43.9% | +8.7 | KEEP | 11150 | 50.0% | +2.7 | [-1.2, +6.7] | DROP | +1.6 [-2.3, +5.5] DROP | 50% / 32% |
| prior_day_vah | 537 | 48.2% | 42.5% | +5.8 | KEEP | 10637 | 50.7% | -2.5 | [-6.8, +1.8] | DROP | -2.4 [-6.6, +1.8] DROP | 51% / 35% |
| prior_day_val | 539 | 52.3% | 43.5% | +8.8 | KEEP | 10393 | 50.4% | +2.0 | [-2.2, +6.1] | DROP | +1.4 [-2.8, +5.4] DROP | 50% / 36% |
| prior_week_high | 150 | 44.7% | 34.1% | +10.5 | KEEP | 2845 | 48.5% | -3.9 | [-11.7, +4.6] | DROP | -5.4 [-13.5, +2.6] DROP | 50% / 83% |
| prior_week_low | 124 | 43.5% | 34.2% | +9.4 | KEEP | 2895 | 49.6% | -6.1 | [-15.1, +2.5] | DROP | -4.6 [-13.1, +3.7] DROP | 51% / 84% |
| round_1000 | 831 | 45.0% | 35.9% | +9.1 | KEEP | 16471 | 49.4% | -4.4 | [-7.5, -1.1] | DROP | -5.3 [-8.3, -1.8] DROP | 50% / 59% |

**Result.** KEEP: none of 12 (published list: 8). Lost: prior_day_high, prior_day_low, prior_day_poc, naked_poc, 4h_fractal_high, 4h_fractal_low, round_1000, prior_week_high; gained none. A touched random line holds about 50% of the time; no family beats that with a CI above zero, and 5 families (4h fractal high/low, prior-day high/low, round_1000) hold LESS often than a random touched line (CI entirely below zero), i.e. they break more often. Verdicts match the T05 csv for all 12. L1->L2 pairs: 0 (pairs are restricted to KEEP families). HOLD columns are unchanged from the Q79 table (same real touches).

**Parameters.** All OURS: stop width, seed 20261014 (legacy), seed 20261016 and 20 lines (fair, from the T05 audit), redraw cap 100, 2,000-draw bootstrap, KEEP rule. No SOURCED parameters.

**DECISION (OURS)** D5: the verdict and pairs use the fair control; legacy numbers stay in the output for comparison only. D6: controls are drawn for every candidate level, touched or not (as in T05), so the control sample is not conditioned on the real level being touched. D7: a draw equal to the real level is redrawn rather than kept (the card's "never the real level"); this moves the fair diff by at most 1.6 pp and changes no verdict against the T05 csv. D8: consumers below are listed, not edited (scope); the coordinator asked this run to file no cards, so they go to the hand-off as follow-ups.

**Consumers of the withdrawn 8-family KEEP list (each needs its own follow-up; nothing edited here).**
- `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py:1-21` (live alert layer, `KEEP` tuple; live path).
- `levels_confluence_2026-10-14/event_table.py:16` (`KEEP`), used by `ladder_run.py:95` and `ladder_dev.md:15` (LC3 ladder ideas built on KEEP levels).
- `imbalance_qriptal_2026-10-16/filter/filter_join.py:37` and `filter/RESULT.md:9` (5,976 fades of the 8 KEEP families).
- `opr_weekly_low_round_sweep_2026-10-16/RESULT.md:5` and `study.py:266` (cite round_1000 KEEP as related evidence).
- `v1_plan_2026-10-20/D4_LAYER_DECISION.md:10` (Levels Confluence slot earned by the KEEP rule), `layer_readiness_2026-10-16/LAYER_READINESS.md:113`, `krown_audit_2026-10-22/LAYER_CONFLUENCE_DESIGN.md:44` (KEEP families as the LOCATION input).
