# BLOCKED — CSV inputs absent

Counts reported in RESULT.md (not CSV-recomputed): 509 filled / 418 model complete-case / 91 dropped.

## What was checked

- Read `MyTradingSys/research/meta_label_dev_ext_2026-10-31/RESULT.md:1-31` and `MyTradingSys/backtest/layers/FORMULAS.md:1-6`.
- Searched all files recursively under `MyTradingSys/research/meta_label_dev_ext_2026-10-31/` for `*.csv`; result: no files. The directory contains `numbers.json`, `output.md`, `RESULT.md`, and other non-CSV files. The RESULT itself names `numbers.json` and `output.md` as number sources (`RESULT.md:3`), not CSVs.
- The required independent recomputation from saved CSV outputs is therefore impossible. No headline is labeled MATCH or DIFF from CSV evidence; values below are NOT_IN_DATA for the required input format. This is an input block, not evidence that the published numbers are wrong.

## Headline rows

| Headline | RESULT value | Status | Source line matched / evidence |
|---|---:|---|---|
| Filled / complete-case model / dropped | 509 / 418 / 91 | NOT_IN_DATA | `RESULT.md:10`; no CSV available to recompute |
| Tercile counts (top / middle / bottom) | 139 / 137 / 142 | NOT_IN_DATA | `RESULT.md:11`; no CSV available to recompute |
| Top mean net R and 95% CI | +0.430; +0.028..+0.869 | NOT_IN_DATA | `RESULT.md:12`; no CSV available to recompute |
| Top 97.5% CI | -0.024..+0.937 | NOT_IN_DATA | `RESULT.md:12`; no CSV available to recompute |
| Middle / bottom mean net R | -0.355 / -0.215 | NOT_IN_DATA | `RESULT.md:13`; no CSV available to recompute |
| Top-minus-bottom spread and CI | +0.645; +0.114..+1.194 | NOT_IN_DATA | `RESULT.md:14`; no CSV available to recompute |
| Placebo p95 / p / percentile | +0.521 / 0.023 / 98.0th | NOT_IN_DATA | `RESULT.md:15`; no CSV available to recompute |
| Holm / BH | 0.047 / 0.023 | NOT_IN_DATA | `RESULT.md:15`; no CSV available to recompute |
| Top gross / fee / net | +0.668 / 0.238 / +0.430 R | NOT_IN_DATA | `RESULT.md:16`; no CSV available to recompute |
| Model SD / delta-min / required n | 2.144 / 0.509 / 401 | NOT_IN_DATA | `RESULT.md:17`; no CSV available to recompute |
| Same-sign period top means | +0.336 (n=46) / +0.476 (n=93) | NOT_IN_DATA | `RESULT.md:18`; no CSV available to recompute |
| Same-sign period spreads | +0.340 / +0.833 | NOT_IN_DATA | `RESULT.md:18`; no CSV available to recompute |

## Follow-up

No follow-up card created. Per the card's blocked-data rule, the card was not marked done. Supply the saved CSV outputs in the result folder and rerun this audit.
