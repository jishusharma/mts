10 MATCH / 1 DIFF / 8 NOT_IN_DATA

# Re-derivation of meta_label_dev_ext_2026-10-31 RESULT.md headline numbers (Claude Sonnet worker, second check after Gemini blind-read 1102)

## Limit (read first)
- Folder `MyTradingSys/research/meta_label_dev_ext_2026-10-31/` holds NO trade-level csv (files: `ext_window.py`, `numbers.json`, `output.md`, `PRE_REG_EXT.md`, `RESULT.md`, `run_ext.py`, `test_dev_ext_window.py`). A repo-wide search for csv with `meta`/`fabio` in the path found no trade list of this study. Per-trade numbers (CIs, placebo, AUC, buckets) therefore cannot be recomputed: NOT_IN_DATA.
- What WAS done: recomputing derived numbers by hand-formula (Python arithmetic, no study script run) from the saved per-tercile figures in `numbers.json` (n, mean, sd, gross, fee, net per tercile). All numbers below are OURS (our own study, price-only stand-in); the only SOURCED constant is 7.849 (`RESULT.md:15`, a pre-registered multiplier, not re-checked here). `FORMULAS.md` has no formula for tercile/placebo/power; the formulas used are the ones quoted in `RESULT.md:15` and `RESULT.md:22`.
- `numbers.json` is the study's own output, so MATCH here means arithmetic-consistent, not independently observed.

## Rows
| # | Status | RESULT.md line quoted | Recomputed | Basis |
|---|---|---|---|---|
| 1 | MATCH | `RESULT.md:8` "509 / 418 / 91" | 509 - 418 = 91 | numbers.json n_filled/n_model/n_dropped_incomplete |
| 2 | MATCH | `RESULT.md:9` "139 / 137 / 142" | 139+137+142 = 418 = model n | numbers.json terciles n |
| 3 | MATCH | `RESULT.md:4` "random third (all model trades) -0.047 R" | n-weighted mean of the 3 tercile means = -0.046719 | numbers.json terciles mean |
| 4 | MATCH | `RESULT.md:12` "+0.645" top-minus-bottom spread | 0.429609 - (-0.215154) = 0.644763 | numbers.json terciles mean |
| 5 | MATCH | `RESULT.md:14` "+0.668 / 0.238 / +0.430 R (middle -0.105 / 0.251 / -0.355; bottom +0.030 / 0.245 / -0.215)" | gross - fee = net for all 3: 0.42961 / -0.35542 / -0.21515 | numbers.json bucket_money |
| 6 | MATCH | `RESULT.md:15` "delta_min at n_top 139 = 0.509 R (2.144 x sqrt(7.849/139)" | 2.1432 x sqrt(7.849/139) = 0.50929 | sd pooled from tercile n/mean/sd |
| 7 | DIFF | `RESULT.md:15` "sd (model sample) 2.144 R" | pooled sd of 418 model trades from tercile n/mean/sd = 2.1432 (rounds 2.143, not 2.144; diff 0.0008, rounding-level, no effect on 0.509) | sample sd, n-1 |
| 8 | MATCH | `RESULT.md:15` "n needed per tercile for a 0.30 R lift = 401" | 7.849 x (2.1432/0.30)^2 = 400.6 -> 401 (2.144 gives 400.9) | same formula |
| 9 | MATCH | `RESULT.md:22` "0.428 = sd x sqrt(2 ln 16)/sqrt(n)" | 2.1432 x sqrt(2 ln16) / sqrt(139) = 0.42807 | same sd |
| 10 | MATCH | `RESULT.md:13` "Holm (m = 2) 0.047" | 2 x placebo p 0.023256 = 0.046512 | numbers.json placebo_p (p itself not re-derivable) |
| 11 | MATCH | `RESULT.md:17` "Pooled n_top by simple addition 301" | 162 + 139 = 301 (162 is a P0 figure quoted in the same line, not in this folder) | arithmetic only |
| 12 | NOT_IN_DATA | `RESULT.md:10` "+0.430, +0.028..+0.869 (97.5 % level: -0.024..+0.937)" | top mean, day-block bootstrap CI need trades | no trade csv |
| 13 | NOT_IN_DATA | `RESULT.md:13` "p95 +0.521 < real 0.645; placebo p 0.023 (real at 98.0th percentile)" | needs 300 shuffles over trades | no trade csv |
| 14 | NOT_IN_DATA | `RESULT.md:13` "BH q 0.023" | BH needs the family p-values; the 2 p-values are not in the folder (m = 2 stated, only one p saved) | incomplete |
| 15 | NOT_IN_DATA | `RESULT.md:20` "out-of-fold AUC 0.527" | needs per-trade scores and outcomes | no trade csv |
| 16 | NOT_IN_DATA | `RESULT.md:21` "top +0.056 R, CI -0.296..+0.445, spread +0.239" | week-purged K-fold needs trades | no trade csv |
| 17 | NOT_IN_DATA | `RESULT.md:16` "+0.336 (n 46) / +0.476 (n 93) ... +0.340 / +0.833" | per-period top/bottom means need trades | no trade csv |
| 18 | NOT_IN_DATA | `RESULT.md:23` "relative volume low third -0.447 R (n 170)" | bucket mean needs trades; only counts check (3 volume buckets 169+170+170 = 509) | no trade csv |
| 19 | NOT_IN_DATA | `RESULT.md:25` "all 509 fills coincide with the desk touch time (0 differ)" | needs per-fill times | no trade csv |

## Disposition
Headline derived numbers are arithmetic-consistent (10 MATCH); one rounding-level DIFF (sd 2.144 vs 2.143); the trade-level headline (top +0.430 R and its CI, placebo, AUC, k-fold) remains unverified by any second vendor. To close it, a trade list csv (one row per filled trade: entry time, tercile, net R, gross, fee, score, fold) must be saved in the study folder; then rerun rows 12-19. No source or script was edited.
