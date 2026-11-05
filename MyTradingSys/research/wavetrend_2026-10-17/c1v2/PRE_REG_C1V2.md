# PRE-REGISTRATION v2: WaveTrend C1 divergence, detector c1-v2, BTCUSDT perp, DEV (frozen 2026-11-05)

Card `wavetrend-c1-v2`. Supersedes nothing: the v1 PRE_REG.md, atlas outputs and RESULT.md stay frozen as written. This file
registers a NEW C1 trial with the corrected detector. Written after the count-only pass below and BEFORE any outcome read.

## 0. What was read to produce this file
Bars (H, L, close via `count_events.load_dev`/`resample`/`wt_series`) and event timestamps only. No return, MFE/MAE, fee,
funding, VALIDATION (>= 2024-07-01) or HOLDOUT bar was read. The loader refuses any bar >= 2024-07-01.

## 1. What changed vs v1 (the defect)
v1 (`count_events.ev_C`) confirms price pivots, then compares wt1 VALUES at the price-pivot bars; the WT side is never a
confirmed pivot (AUDIT_2026-10-18 finding 1, DISPOSITION_2026-10-19, repro `repro_c1_spec_mismatch.py`). The spec
(ATLAS_STUDY_SPEC s2, C1 row) needs both. c1-v2 (`c1_v2.py`, VERSION `c1-v2`) pairs the confirmed price-pivot list with the
confirmed wt1-pivot list one-to-one, |p - q| <= G; event time t_ev = max(p + k, q + k) (later confirmation, causal).
Zone guard unchanged (both WT pivot values strictly on the event side). Tests: `test_c1_v2.py` (v1 fails the fixture, v2
passes; both sides; confirmation delay; future spike), `test_c1v2_counts.py` (runner).

## 2. Frozen inputs (exact)
| item | value |
|---|---|
| data | F:/MTS/data/tom_raw/klines BTCUSDT-1m 2022-01 .. 2024-06 (30 files), re-verified byte for byte by `c1v2_counts.manifest_check` before counting |
| input_manifest.json | sha256 `cd348590166eb4e319c4ccb4cff15e08bdeb66816cea2bb2af1dcd1b3e63b611` |
| c1_v2.py / c1v2_counts.py | git blob `db36eda3a344` / `58e023c07b4a` |
| count_events.py / select_cells.py (frozen v1) | git blob `6dcc6deb8eb0` / `805e3d568cfe` |
| k, G | 2, 20: the v1 PRE_REG s2 values, reused unchanged, no grid (OURS) |
| WT params 10/21/4, hlc3 | SOURCED (PARITY_CONTRACT s2) |
| FLOOR, selection rule | 153 event-days, select_cells.py rule as frozen in PRE_REG s4 (OURS) |

## 3. Event counts (DEV, all sides, no context; events / distinct event-days)
| TF | C1 v1 (sanity, equals PRE_REG s2) | C1 c1-v2 | c1-v2 up / lo | mde_d (Holm 12) |
|---|---|---|---|---|
| 5m | 3840 / 907 | 7136 / 912 | 3633 / 3503 | 0.123 |
| 15m | 1288 / 694 | 2382 / 891 | 1194 / 1188 | 0.124 |
| 1h | 392 / 331 | 622 / 519 | 329 / 293 | 0.163 |
| 4h | 104 / 102 | 139 / 137 | 72 / 67 | 0.317 |
| 1d | 15 / 15 | 15 / 15 | 9 / 6 | 0.957 |
Files: `counts/c1v2_counts_k2_G20.csv` (context-binned), `counts/v1_C1_sanity.csv`, `counts/c1v2_SELECTION.md`.
The v1 sanity rows reproduce the frozen PRE_REG s2 C1 row exactly, so the pipeline and data are unchanged.

## 4. Frozen cells (rule applied mechanically to the c1-v2 rows; no choice made by hand)
| cell | TF | event | context | events | event_days | side up / lo | mde_d |
|---|---|---|---|---|---|---|---|
| W01v2 | 5m | C1_v2 | htf:htf_mid | 5693 | 909 | 2872 / 2821 | 0.123 |
| W02v2 | 5m | C1_v2 | trend:trend_with | 4865 | 907 | 2477 / 2388 | 0.123 |

## Context
- Regime: W02v2 = EMA(200) trend state gate (trend_with, the event side agrees with the trend); W01v2 = higher-TF wt1 state gate (htf_mid); no bull/bear gate beyond that, because the cell rule chose these bins on counts.
- Phase: none, because C1 is itself the phase trigger (exhaustion divergence); no separate phase filter is registered.
- Session: none, because the atlas covers all UTC hours; the random-clock control is matched on UTC hour slot instead.
- Entry: open of bar t_ev + 1 in the implied direction (side +1 = short, side -1 = long), as v1 PRE_REG s6.

## 5. Outcome, arms and the paired-control method (frozen now, run only by a later card)
- Primary outcome: signed gross return open(t_ev + 1) -> close(t_ev + 12), 5m bars (v1 PRE_REG s6, unchanged). H=4, H=48, MFE/MAE: descriptive, outside Holm.
- Arms per cell: (1) C1_v2 alone at 5m, (2) context alone (same bin, no C1_v2 event, hour-of-day matched), (3) conjunction (the cell), (4) random clock matched on TF, UTC hour slot and vol tercile (200 draws, v1 s6 pool rules).
- Paired-control method (replaces the v1 independence z-test the audit rejected): `paired_inference.py` (commit 4463a42e7, tests `test_paired_inference.py`): block = UTC day; per arm, the day's observations are averaged first; only days with >= 1 observation in both arms enter (dropped days counted and reported); D_d = mean(conjunction_d) - mean(control_d); statistic = mean of D_d with equal day weight; p = two-sided sign-flip randomization of D_d (exact when days <= 16, else seeded Monte Carlo); CI = seeded percentile bootstrap over whole days.
- Primary test per cell: conjunction vs random clock with the method above; **Holm over m = 2**. A cell passes the incremental-information screen only if the conjunction also beats arm 1 and arm 2 by the same paired method (same sign, p < 0.05 unadjusted); otherwise "no incremental information".
- Output gross, descriptive. No strategy, no fee-net claim. VALIDATION once and HOLDOUT sealed belong to a separate strategy PRE_REG.

## 6. Gate before any outcome read
1. This file is frozen in git (its commit is the freeze stamp) and `prereg_context_lint.py` passes.
2. The companion CODEX audit card reviews `c1_v2.py` + this file (pairing rule, causal t_ev, paired method) and finds no blocking defect.
3. Only then may a new card (`wavetrend-c1v2-dev-outcomes`) compute section 5, once, as trials WT-C1V2-A01/A02.

## 7. Trial ids (TRIAL_LEDGER.csv rows)
WT-C1V2-T01 count-only (k=2, G=20, no grid). Outcome trials WT-C1V2-A01 = W01v2, WT-C1V2-A02 = W02v2 (one primary test each).

## 8. Known weaknesses (read before trusting any later number)
1. DEV was already read for C1 v1 outcomes (v1 cell W08, 1h C1 htf_mid): this is a second look at the same split with an adjacent definition; any pass is DEV-only and needs VALIDATION.
2. c1-v2 fires MORE than v1 (5m 7136 vs 3840): pairing within G = 20 bars lets a price pivot pair with a WT pivot up to 20 bars away. G = 20 is OURS and inherited, not re-tuned.
3. Both cells are 5m and heavily clustered (~6 events per event-day); day blocks carry the inference, so the effective n is ~909 days, not ~5000 events.
4. Lock-step pairing skips a pivot that has no partner within G; a different pairing rule (nearest-neighbour) would give other counts. That rule is not tested here and would be a new trial.
