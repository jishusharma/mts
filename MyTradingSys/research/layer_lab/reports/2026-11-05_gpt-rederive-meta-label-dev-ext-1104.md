BLOCKED - 0 MATCH / 0 DIFF / 19 NOT_IN_DATA (19 headline rows cannot be independently re-derived without the required saved CSV).

## What was checked

- `MyTradingSys/research/meta_label_dev_ext_2026-10-31/RESULT.md:1-30` - requested headline source.
- `MyTradingSys/backtest/layers/FORMULAS.md` - formula reference supplied by the card; it defines generic statistical/backtest conventions but does not supply this study's row-level observations.
- `MyTradingSys/research/meta_label_dev_ext_2026-10-31/` - recursively inventoried saved files. The directory contains `numbers.json`, `output.md`, `PRE_REG_EXT.md`, `ext_window.py`, `run_ext.py`, and a test file; there is no saved CSV output.
- Command: `Get-ChildItem MyTradingSys/research/meta_label_dev_ext_2026-10-31 -Recurse -File | Select-Object FullName,Length`.

The task requires recomputation from saved CSV outputs, not from the script. `numbers.json` and `output.md` repeat the reported results, so using them as independent observations would not satisfy that check. No study script was run and no market data was read.

## Headline rows

`NOT_IN_DATA` below means no required CSV observation set was present from which to independently recompute the headline. The quoted source excerpt identifies each row against RESULT.md; it does not claim that the reported value was independently verified.

| Status | RESULT.md source | Headline number(s) | Reason |
|---|---|---|---|
| NOT_IN_DATA | `RESULT.md:4` ?Best third by filter: +0.430 R - vs random third - -0.047 R.? | +0.430 R; -0.047 R | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:8` ?509 / 418 / 91? | filled / model / dropped counts | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:9` ?139 / 137 / 142? | top / middle / bottom counts | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:10` ?+0.430, +0.028..+0.869 (97.5 % level: -0.024..+0.937)? | top mean and two CI ranges | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:11` ?-0.355 / -0.215? | middle / bottom means | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:12` ?+0.645, +0.114..+1.194? | top-bottom spread and CI | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:13` ?p95 +0.521 - placebo p 0.023 - 98.0th percentile - Holm - 0.047; BH q 0.023? | placebo p95, p, percentile, Holm, BH | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:14` ?+0.668 / 0.238 / +0.430 - middle - bottom ?? | gross / fee / net for all terciles | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:15` ?sd - 2.144 R; delta_min - 0.509 R - n needed - 401? | SD, minimum delta, needed n | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:16` ?+0.336 (n 46) / +0.476 (n 93) - +0.340 / +0.833? | period means, counts, spreads | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:17` ?top -0.003 R, n 162, placebo p 0.60 - n_top - 301 - under 401? | P0 comparison and pooled arithmetic count | Required CSV absent; P0 data also outside this study folder |
| NOT_IN_DATA | `RESULT.md:20` ?out-of-fold AUC 0.527? | OOF AUC | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:21` ?top +0.056 R, CI -0.296..+0.445, spread +0.239? | week-purged fold metrics | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:22` ?0.428 = sd x sqrt(2 ln 16)/sqrt(n)? | best-of-16 threshold | Required CSV absent for independent SD and n derivation |
| NOT_IN_DATA | `RESULT.md:23` ?relative volume low third -0.447 R (n 170)? | low-volume bucket mean and count | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:24` ?Gross - +0.668 R vs 0.238 fee? | gross and fee | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:25` ?2019-09..2019-12 - no perp 1m data - Fill check - 509 - (0 differ)? | missing-data statement and fill-match counts | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:26` ?n_top came in at 139? and ?PASSED? | top count and verdict rule outcome | Required CSV absent |
| NOT_IN_DATA | `RESULT.md:30` ?one DEV null (n 162, -0.003 R) - +0.430 R? | concluding P0 and pre-DEV summary figures | Required CSV absent |

## Disposition

No verdict on the numeric accuracy is possible from the required evidence. Provide the saved CSV output(s) for this study in its folder, then rerun the independent calculations. The card remains open; per the lab instruction for missing input, it is not marked done.
