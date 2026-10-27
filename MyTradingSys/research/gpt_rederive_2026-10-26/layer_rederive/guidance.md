# Guidance headline recount — 2026-10-28, OpenAI/Codex, JIS-NUC

**FIX-FIRST: published aggregate arithmetic reproduces; the 240-minute narrative mixes horizons and mislabels a filter.** This is an independent audit of the published cell ledger, not a new market-data run, raw-return reconstruction, trust certification or keep/drop decision.

## Inputs and boundaries

`system/layer_index.json`, family `guidance`, lists `research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md` as its result and no event/trade ledger. That folder contains `MATRIX_CELLS.csv` (336 aggregate rows), `MATRIX_SUMMARY.json`, `PRE_REG_Q33.md`, and the source/spec files. Paths below are relative to `MyTradingSys/` unless prefixed with `scripts/`.

CSV SHA256: `63a3eed04c362506f7924ecbe23cf28f90882d8a425b3404c7d4d2f8a865d573`. Recount code is embedded below and executes using only Python's standard library. Expected arithmetic follows the frozen pre-registration: classify n, sum disjoint unfiltered sides, independently compute BH adjusted p-values as reverse cumulative minima of m*p/rank, and apply the primary survivor rule. The producer runner was inspected only after the independent recount to resolve the horizon metadata.

The original study explicitly used 2022-01-01 through 2026-10-11 with **no holdout** (`PRE_REG_Q33.md:8,15`). This is not a current DEV-only/OOS result. No raw bars, sealed partition files, event-level returns, orders or account data were opened or rerun. Published aggregates cannot independently prove their underlying prices, fills, split membership or trial completeness. Those are NOT_IN_DATA for this audit.

## Headline comparisons

Source `research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md`:

| Claim / line | Independent result from CSV | Disposition |
|---|---|---|
| 336 cells / 8 | 336 unique trigger/side/filter keys; zero duplicates | MATCH |
| 186 tested / 8 | 186, exactly all n >= 300 rows | MATCH |
| 89 underpowered / 9 | 89; remaining 61 have n < 20 | MATCH |
| 0 primary survivors / 10 | 0 under freshly computed BH q plus net-positive and positive-half requirements | MATCH at aggregate level |
| Minimum q 0.62 / 10 | 0.62; largest difference from stored six-decimal q is 0.0000005 | MATCH within published rounding |
| Seven trigger event totals / 14-20 | 8689, 8689, 1491, 1275, 19282, 8427, 1870 from unfiltered long+short counts | MATCH; not deduplicated trade counts across triggers |
| Fourteen long/short means / 14-20 | All round to the quoted three-decimal percentages; values printed below | MATCH as unit conversions of stored means |
| Median gross +0.0003% / 22 | +0.00028525% after adding the stated 0.10% fee to stored mean_H4 values | MATCH conditional on stated constant fee; not raw P/L verification |
| 0 positive primary means / 23 | 0/186 | MATCH |
| 3 positive 240-minute means / 23 | 3/186 | MATCH |
| Best 240-minute +0.039% / 23 | +0.0388292%, CSV row 275 | MATCH |
| Best cell labelled F1=UP / 24 | Exact cell is `F1=1&F3=0`; F3 neutral is also required | MISMATCH: omitted filter condition |
| p=.038, q=.62 and negative halves support 240-minute instability / 24 | Those fields describe PRIMARY H4=60 minutes, not H16=240 minutes | MISMATCH of horizon attribution; 240-minute p/q/half results NOT_IN_DATA |
| Underlying trade count, mean R, fee legs, split membership | Aggregate n counts events; no stop/R scale, event returns or timestamped ledger available | NOT_IN_DATA; no invented trade count or R statistic |
| Data interval and no holdout / 4; PRE_REG:8,15 | Documents explicitly disclose full-period in-sample study | MATCH as documented provenance only; never relabel as OOS |

## Findings

1. **MED — horizon attribution:** `matrix_q33.py:297-301` derives h1_mean/h2_mean from `R[PRIMARY]` and placebo p from PRIMARY; the pre-registration fixes PRIMARY=4. `MATRIX_REPORT.md:23-24` places these values beside the best H16 result and concludes instability. This does not establish H16 instability. Correct the narrative or identify existing H16 evidence; do not rerun sealed data to fill the gap.
2. **LOW — incomplete cell key:** `MATRIX_CELLS.csv:275` requires `F1=1&F3=0`, whereas the narrative names only F1. Quote the complete key. Follow-up for both findings: `q33-report-horizon-and-filter-label`.
3. **LIMITATION — raw evidence:** a cell-mean ledger is sufficient to recount cells and redo BH from published p-values, but cannot rederive event returns, p-values from the placebo samples, or actual fee legs. No VERIFIED tag is issued. The frozen historical no-holdout design is disclosed rather than treated as new permission to access sealed data.

No producer report or calculation code was changed. Proof run: the embedded script printed 336/186/89/61, zero duplicate/status errors, zero primary survivors, and q max difference below 5.1e-7 (OURS allowance for six-decimal serialization). Assertions check the recount's internal contracts; no implementation-mirroring test was added.

## Reproduction script

Run from the repository root after saving this Python block to an untracked scratch file. It reads only the named aggregate CSV. The numerical output below is from the script, not copied from MATRIX_SUMMARY.json.
