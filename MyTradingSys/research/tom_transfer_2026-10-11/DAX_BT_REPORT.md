> **SMOKE (partial data): 2026-01 only, dev period only. These numbers test the pipeline; they are NOT a result and must not be quoted as one. The full run overwrites this file.**

# DAX_BT_REPORT: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest)

Spec: `PRE_REG_DAX.md` (frozen 2026-10-11). Run `dax_bt_20261010_SMOKE`, code HEAD `085412ca599d33a0ae91d9b7a06bc7407baf165e`, 2026-10-10 20:36Z.

Hashes: SetupCandidatesBuilder.java `d749117a809608ff`, verdict.py `1f6d3b004931e5dd`, tom_bt.py `d9c417c72a69e86a`, tom_dax_bt.py `1ba261ccfcfbeb4e`, fees.py `2457b5a2c8e93d16`.

## 1. Data and accounting

- DAX snapshots (TomSnapshotGen, 15 min, -Dmts.symbol=GER40): 1 month files; 2976 evaluated, 1453 kept by Java (>= 1 candidate), 438 errors. Market-open filter (a real 1m bar in the 2 minutes before asOf) dropped 202 closed-market snapshots before any verdict; 1251 rows remain. Order-flow mask changed the proof count of 0 DAX candidates (expected 0: the archive's taker-buy is exactly half the volume, so every delta is 0).

- DAX 1m archive `F:\MTS\data\dax_archive\klines`; runs of > 4 days with no bar (download holes or holidays; filled flat for the simulator only): 0.

- BTC matched-proof: 2026-10-06 snapshots re-scored with absorption, cvd_aligned, delta_flip and finished_auction masked; 1800 rows, mask changed 1818 candidates; 0 snapshots from 2026-06-26 on were never read (burned holdout, B147).

- Periods: DAX dev = 2024-11-04..2026-04-10; the holdout was NOT read. BTC-matched: dev only, 2025-09-01..2026-06-25 (hist is not part of the comparison; the holdout is burned).


## 2. Results (one-trade-at-a-time, limit at zone price, stop/target from the rank-1 candidate, 8 zone-tf bars)

Fees: DAX = `FEES_FDAX` (0.000005 of price per side on every leg); BTC = Deribit (maker 0, taker 0.0005) as in the BTC rerun. `daxfee` = net_rr := gross_rr before the verdict; `coded` = Java net_rr. Shift 0 is the pre-registered rule; shift > 0 are EXTENSION arms (section 3). Pass bar: >= 100 filled trades in a period and net R 95% CI lower bound > 0.


| market / verdict / shift / variant | period | n signals | n filled | fill | win | mean R gross [95% CI] | mean R net [95% CI] | null gross (real / null / p) | held across a close | pass bar |
|---|---|---|---|---|---|---|---|---|---|---|
| DAX / daxfee / s0 / A | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / daxfee / s0 / episode | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / daxfee / s0 / watch_episode | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / daxfee / s0 / p4_episode | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / daxfee / s1 / watch_episode | dev | 54 | 44 | 81% | 2% | -0.34 [-0.80, 0.28] | -0.41 [-0.88, 0.22] | -0.345 / 0.016 / 0.756 | 2 | insufficient N (44 < 100) |
| DAX / daxfee / s2 / watch_episode | dev | 367 | 309 | 84% | 4% | -0.40 [-0.64, -0.14] | -0.53 [-0.79, -0.26] | -0.403 / 0.133 / 0.995 | 30 | no edge shown |
| DAX / daxfee / s2 / p4_episode | dev | 54 | 44 | 81% | 2% | -0.34 [-0.80, 0.28] | -0.41 [-0.88, 0.22] | -0.345 / 0.016 / 0.756 | 2 | insufficient N (44 < 100) |
| DAX / daxfee / s3 / A | dev | 24 | 21 (n<30) | 88% | 5% | 0.01 [-0.82, 1.25] | -0.05 [-0.89, 1.20] | - | 0 | insufficient N (21 < 100) |
| DAX / daxfee / s3 / episode | dev | 24 | 21 (n<30) | 88% | 5% | 0.01 [-0.82, 1.25] | -0.05 [-0.89, 1.20] | - | 0 | insufficient N (21 < 100) |
| DAX / daxfee / s3 / watch_episode | dev | 418 | 341 | 82% | 3% | -0.47 [-0.68, -0.23] | -0.58 [-0.81, -0.32] | -0.467 / 0.087 / 1.000 | 28 | no edge shown |
| DAX / daxfee / s3 / p4_episode | dev | 367 | 309 | 84% | 4% | -0.40 [-0.64, -0.14] | -0.53 [-0.79, -0.26] | -0.403 / 0.133 / 0.995 | 30 | no edge shown |
| DAX / coded / s0 / A | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / coded / s0 / episode | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / coded / s0 / watch_episode | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / coded / s0 / p4_episode | dev | 0 | 0 | - | - | - | - | - | 0 | insufficient N (0 filled) |
| DAX / coded / s1 / watch_episode | dev | 35 | 30 | 86% | 0% | -0.19 [-0.82, 0.79] | -0.24 [-0.88, 0.74] | -0.189 / -0.108 / 0.413 | 0 | insufficient N (30 < 100) |
| DAX / coded / s2 / watch_episode | dev | 207 | 183 | 88% | 1% | -0.26 [-0.60, 0.11] | -0.39 [-0.74, 0.00] | -0.264 / 0.067 / 0.766 | 15 | no edge shown |
| DAX / coded / s2 / p4_episode | dev | 35 | 30 | 86% | 0% | -0.19 [-0.82, 0.79] | -0.24 [-0.88, 0.74] | -0.189 / -0.108 / 0.413 | 0 | insufficient N (30 < 100) |
| DAX / coded / s3 / A | dev | 16 | 15 (n<30) | 94% | 0% | 0.25 [-0.87, 1.90] | 0.20 [-0.93, 1.88] | - | 0 | insufficient N (15 < 100) |
| DAX / coded / s3 / episode | dev | 16 | 15 (n<30) | 94% | 0% | 0.25 [-0.87, 1.90] | 0.20 [-0.93, 1.88] | - | 0 | insufficient N (15 < 100) |
| DAX / coded / s3 / watch_episode | dev | 225 | 201 | 89% | 1% | -0.31 [-0.60, 0.05] | -0.43 [-0.75, -0.05] | -0.308 / 0.078 / 0.871 | 15 | no edge shown |
| DAX / coded / s3 / p4_episode | dev | 207 | 183 | 88% | 1% | -0.26 [-0.60, 0.11] | -0.39 [-0.74, 0.00] | -0.264 / 0.067 / 0.766 | 15 | no edge shown |
| BTC-matched / daxfee / s0 / A | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / daxfee / s0 / episode | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / daxfee / s0 / watch_episode | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / daxfee / s0 / p4_episode | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / daxfee / s1 / watch_episode | dev | 39 | 35 | 90% | 3% | -0.65 [-0.87, -0.38] | -53.24 [-150.43, -1.42] | -0.645 / 6.223 / 0.990 | n/a | insufficient N (35 < 100) |
| BTC-matched / daxfee / s2 / watch_episode | dev | 353 | 320 | 91% | 3% | -0.30 [-0.51, -0.04] | -8.28 [-19.62, -1.95] | -0.297 / 0.531 / 0.975 | n/a | no edge shown |
| BTC-matched / daxfee / s2 / p4_episode | dev | 39 | 35 | 90% | 3% | -0.65 [-0.87, -0.38] | -53.24 [-150.43, -1.42] | -0.645 / 6.223 / 0.990 | n/a | insufficient N (35 < 100) |
| BTC-matched / daxfee / s3 / A | dev | 33 | 30 | 91% | 3% | -0.64 [-0.90, -0.34] | -61.89 [-175.25, -1.49] | -0.644 / 2.978 / 0.955 | n/a | insufficient N (30 < 100) |
| BTC-matched / daxfee / s3 / episode | dev | 33 | 30 | 91% | 3% | -0.64 [-0.90, -0.34] | -61.89 [-175.25, -1.49] | -0.644 / 2.978 / 0.955 | n/a | insufficient N (30 < 100) |
| BTC-matched / daxfee / s3 / watch_episode | dev | 401 | 367 | 92% | 3% | -0.28 [-0.49, -0.05] | -6.82 [-16.24, -1.69] | -0.280 / 0.499 / 0.990 | n/a | no edge shown |
| BTC-matched / daxfee / s3 / p4_episode | dev | 353 | 320 | 91% | 3% | -0.30 [-0.51, -0.04] | -8.28 [-19.62, -1.95] | -0.297 / 0.531 / 0.975 | n/a | no edge shown |
| BTC-matched / coded / s0 / A | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / coded / s0 / episode | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / coded / s0 / watch_episode | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / coded / s0 / p4_episode | dev | 0 | 0 | - | - | - | - | - | n/a | insufficient N (0 filled) |
| BTC-matched / coded / s1 / watch_episode | dev | 32 | 29 (n<30) | 91% | 0% | -0.65 [-0.89, -0.35] | -63.84 [-180.88, -1.38] | - | n/a | insufficient N (29 < 100) |
| BTC-matched / coded / s2 / watch_episode | dev | 291 | 267 | 92% | 1% | -0.25 [-0.50, 0.06] | -9.63 [-22.86, -1.95] | -0.248 / 0.514 / 0.905 | n/a | no edge shown |
| BTC-matched / coded / s2 / p4_episode | dev | 32 | 29 (n<30) | 91% | 0% | -0.65 [-0.89, -0.35] | -63.84 [-180.88, -1.38] | - | n/a | insufficient N (29 < 100) |
| BTC-matched / coded / s3 / A | dev | 27 | 25 (n<30) | 93% | 0% | -0.66 [-0.92, -0.33] | -73.91 [-209.77, -1.52] | - | n/a | insufficient N (25 < 100) |
| BTC-matched / coded / s3 / episode | dev | 27 | 25 (n<30) | 93% | 0% | -0.66 [-0.92, -0.33] | -73.91 [-209.77, -1.52] | - | n/a | insufficient N (25 < 100) |
| BTC-matched / coded / s3 / watch_episode | dev | 330 | 307 | 93% | 1% | -0.22 [-0.46, 0.05] | -7.89 [-19.35, -1.76] | -0.224 / 0.483 / 0.886 | n/a | no edge shown |
| BTC-matched / coded / s3 / p4_episode | dev | 291 | 267 | 92% | 1% | -0.25 [-0.50, 0.06] | -9.63 [-22.86, -1.95] | -0.248 / 0.514 / 0.905 | n/a | no edge shown |


### DAX stress: + 1 index point of slippage on stop and timeout legs (dev)

| arm | n filled | mean net R | with +1 pt [95% CI] | median stop distance | exit mix |
|---|---|---|---|---|---|
| daxfee / watch_episode / s1 | 44 | -0.41 | -0.67 [-1.19, 0.01] | 0.038% | target 1 / stop 35 / timeout 8 |
| daxfee / watch_episode / s2 | 309 | -0.53 | -1.05 [-1.58, -0.63] | 0.032% | target 11 / stop 249 / timeout 49 |
| daxfee / p4_episode / s2 | 44 | -0.41 | -0.67 [-1.19, 0.01] | 0.038% | target 1 / stop 35 / timeout 8 |
| daxfee / A / s3 | 21 | -0.05 | -0.31 [-1.20, 0.98] | 0.048% | target 1 / stop 16 / timeout 4 |
| daxfee / episode / s3 | 21 | -0.05 | -0.31 [-1.20, 0.98] | 0.048% | target 1 / stop 16 / timeout 4 |
| daxfee / watch_episode / s3 | 341 | -0.58 | -1.03 [-1.54, -0.64] | 0.038% | target 11 / stop 277 / timeout 53 |
| daxfee / p4_episode / s3 | 309 | -0.53 | -1.05 [-1.58, -0.63] | 0.032% | target 11 / stop 249 / timeout 49 |
| coded / watch_episode / s1 | 30 | -0.24 | -0.44 [-1.11, 0.53] | 0.054% | target 0 / stop 24 / timeout 6 |
| coded / watch_episode / s2 | 183 | -0.39 | -0.90 [-1.76, -0.27] | 0.039% | target 2 / stop 145 / timeout 36 |
| coded / p4_episode / s2 | 30 | -0.24 | -0.44 [-1.11, 0.53] | 0.054% | target 0 / stop 24 / timeout 6 |
| coded / A / s3 | 15 | 0.20 | 0.02 [-1.16, 1.72] | 0.058% | target 0 / stop 11 / timeout 4 |
| coded / episode / s3 | 15 | 0.20 | 0.02 [-1.16, 1.72] | 0.058% | target 0 / stop 11 / timeout 4 |
| coded / watch_episode / s3 | 201 | -0.43 | -0.92 [-1.71, -0.34] | 0.043% | target 2 / stop 157 / timeout 42 |
| coded / p4_episode / s3 | 183 | -0.39 | -0.90 [-1.76, -0.27] | 0.039% | target 2 / stop 145 / timeout 36 |


## 3. Proof-ceiling finding (the pre-registered rule cannot trade on a masked proof set)

With the order-flow proofs masked, only rejection_wick and volume_spike can count: the proof count is at most 2. `compute_verdict` needs proof >= 3 for WATCH and >= 5 for SETUP_FORMING, so at shift 0 the verdict can never leave WAIT_PROOF and every variant has 0 signals on DAX and on matched BTC. The pre-registered comparison is therefore degenerate by construction (the unmasked BTC history already topped out at proof 4; PRE_REG assumed WATCH reachable). Extension arms `--shifts 1,2,3` add k to every candidate's proof count (WATCH needs masked proof >= 3-k; SETUP_FORMING >= 5-k), i.e. they relax the proof gate to what the data can show. They are NOT in the pre-registration, are registered as trials (variant suffix `/s<k>`), and any reading needs the supervisor's decision on how to count them.


## 4. Deviations and caveats (all stated, none tuned)

- **Absorption is masked too.** PRE_REG lists cvd_aligned, delta_flip, finished_auction. Absorption condition 3 (`SetupCandidatesBuilder.java:685-687`) needs the delta sign, which DAX does not have, so it cannot fire there; masking it on BTC is what "exactly as on DAX" requires.

- **Delta noise fixed in the archive format.** `dax_data.convert` printed taker-buy with 6 decimals, so micro volumes (0.001335) gave delta = +-1e-6 and the engine saw phantom aggressor splits (delta_flip, finished_auction, last_3_delta). It now prints 7 decimals: delta is exactly 0. The rows stage masks DAX the same way as BTC as a guard; the accounting line above shows how many DAX candidates the mask changed.

- **Re-ranking sees only the 3 candidates Java printed.** After masking, candidates are re-sorted by (raw, tfRank) as Java does, but a 4th candidate that masking would have lifted into the top 3 is not in the snapshot.

- **Other order-flow dependence in the verdict is not masked (PRE_REG masks proofs only):** the CVD-slope gates in `compute_verdict` and `cvd.last_3_delta` in the proof-direction check still see BTC order flow; on DAX they are flat. Residual BTC/DAX asymmetry.

- **DAX `cvd.last_3_delta` is constant `negative,negative,negative`** (the engine classifies delta 0 as negative), so the proof-direction check (`math_object_builder.py` 'last_3_delta=neg,neg,neg vs LONG') marks every DAX long as `contradiction`: a long SETUP_FORMING is capped to WATCH. Only the SETUP_FORMING-based variants (A, episode, shift >= 3) are touched; the pre-registration did not foresee it.

- **Net R means are driven by tiny-stop trades.** The engine places stops at the nearest swing beyond the zone, which can sit a few cents from it (a BTC candidate with a 0.03 USD stop costs 1588 R in taker fees). Read the gross column and the exit mix beside every net mean.

- **Null** is `random_entry_null` (200 draws, same day, side and distances); on DAX the entry minute is drawn among real bars only (closed minutes cannot be entered). BTC uses `tom_bt_report.random_entry_null` unchanged.

- **Closed minutes** are flat bars at the last close with volume 0 for the simulator only; the timeout counts clock bars; a gap through the stop fills at the reopening bar's open (`min/max(open, stop)`). `held across a close` counts filled trades whose fill..exit span a closed minute. A limit fill on a reopening gap is taken at the limit price (as on BTC), slightly optimistic.

- Days the feed refused (download holes) look like closed days: their snapshots are dropped by the open filter, and a trade spanning a hole would see flat bars; the hole count in section 1 is the check.

- Funding is not modelled (DAX future: none). Stop-first on ambiguous bars. Trial rows: `bt_runs/TRIAL_REGISTRY_SMOKE.csv (smoke rows are kept apart from the real trial count)`, run id `dax_bt_20261010_SMOKE`.
