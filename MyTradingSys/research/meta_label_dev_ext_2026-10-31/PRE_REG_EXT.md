# PRE_REG_EXT: meta-label rerun on the pre-DEV window, Fabio Model C price-only stand-in (ours)

Card `meta-label-fabio-c-dev-ext-power` (ROADMAP 2.2, NOT ENOUGH DATA branch). Written and committed BEFORE any trade list of the extension window was generated and before any outcome-by-feature number of it was read. Frozen parent protocol: `research/meta_label_tom_fabio_2026-10-31/PRE_REG.md` (not edited). Already known before this file, from P0 (DEV, not this window): 162 trades in the top third, top third -0.003 R, unconditional sd 2.3817 R, filled n 518. Nothing of the extension window is known except that the files exist.

## 1. Window and data (all OURS unless marked)
- Requested window 2019-09..2022-03. Binance USD-M perp 1m klines are public only from 2019-12-31 and the first month on disk is 2020-01 (`F:/MTS/data/dev_ext_2019_2021/klines`, `dev_ext.py`), so the real window is bar open in [2020-01-01, 2022-04-01). 2019-09..2019-12 has no data on this host: DECISION (OURS) it is not mixed in from spot (basis, other venue). 2022-01..03 comes from the desk's own 1m files (`F:/MTS/data/tom_raw/klines`), the three warm-up months that precede the desk's DEV start 2022-04-01; trades are generated for entry days 2020-01-02..2022-03-31 (the first day is warm-up for the opening balance bars).
- Hard cut: no bar with open >= 2022-04-01 00:00 UTC is read by any loader of this rerun (the loader raises). VALIDATION (2024-07-01..) and HOLDOUT are never opened. DEV 2022-04-01..2024-06-30 is not re-read either (P0 already did).
- Funding: `dev_ext_2019_2021/funding/*.csv` for 2020-01..2021-12 and `candle_close_dev_2022_2024/BTCUSDT-fundingRate-2022-0{1,2,3}.zip` for 2022-01..03 (the Dumps folder of P0 is absent on this host; same Binance series).

## 2. Setup, features, model: frozen, unchanged
- Setup: `studies/fabio_v3.py` DEFAULT model C (m 15, push OFF, f 0.5 %, rule exit = hold to window end, no target), fees and slippage as the desk (`_bars.FEE_DEFAULT`). The study code is called unchanged; only the bar array and the day range of `ideas` are swapped for this window (the day-range loop is copied with its two dates changed).
- Features, model columns, ridge lambda 1.0, IRLS, complete-case rule, 6 contiguous week-blocks with 1-week purge/embargo, terciles with cut points from the TRAINING fold (ROADMAP 2.1 amendment 3), day-block bootstrap 2000 draws seed 20261031, shuffled-label placebo 300 shuffles seed 20261031: all exactly as `PRE_REG.md` sections 2-3 and `analyze.py` (imported, not copied).
- Holm family: m = 2 kept (the parent family: Tom VP and Fabio C), conservative; with a single setup run here the Holm p equals min(1, 2 x placebo p). BH q reported beside. Descriptive single-feature splits at the Bonferroni 99.375 % level, no verdict. Gross, fee, net per tercile and n per bucket reported (under 30 = too few). The setup is named "Fabio Model C price-only stand-in (ours)" everywhere.
- Same-sign check periods (OURS, replaces the DEV 2022 vs 2023-24H1 split): 2020 vs 2021-01..2022-03 (cut 2021-01-01).
- A week-purged random K-fold is reported beside, no verdict (amendment 4).

## 3. Pass rule (inherited, unchanged)
PASSED = top-tercile fee-net mean > 0 AND its 95 % day-block CI lower bound > 0 AND real top-minus-bottom spread above the placebo 95th percentile. NOT ENOUGH DATA = fewer than 100 trades in the top tercile, or CI spans 0 with n_top below n_need = ceil(7.849 (sd/0.30)^2) (the 0.30 R lift bar, amendment 8). Otherwise FAILED. No VALIDATION read on any outcome (the parent forbade it unless DEV passed, and this window is pre-DEV: a PASS here would be a hypothesis for the card owner, not a gate; HOLDOUT never).

## 4. Power, computed before any read (FORMULAS-style, (1.96 + 0.8416)^2 = 7.849)
n_need = 7.849 (sd/0.30)^2. With the P0 sd 2.3817 R as the only prior: (2.3817/0.30)^2 = 63.03, n_need = 495 per tercile. The ROADMAP 2.2 update expected about 140 per third (27 DEV months gave 162; about 5 months of 2020 drop to the 21-week Cowen warm-up), under 495, so NOT ENOUGH DATA is the expected outcome and parks meta-labelling for Tom VP and Fabio C, as ROADMAP 2.2 says. Pooling with P0 (162) by simple addition is an arithmetic line only: no pooled model or verdict. Realised n and delta_min = sd sqrt(7.849/n_top) are recomputed in RESULT.md.
Features tried: 8 (10 columns), one model fit, no selection, no new features.

## 5. Tests and exports
- `test_dev_ext_window.py`: the loader never returns a bar at or after 2022-04-01 (and a loader one bar too wide is caught); the window constants; funding never beyond the window.
- Export: one sim-desk result `desk-meta_label_fabio_c_dev_ext` in the same three-part shape as P0 (table, verdict line, best/worst third examples).
