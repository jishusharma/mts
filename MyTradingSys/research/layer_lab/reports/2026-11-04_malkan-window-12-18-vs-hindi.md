# malkan-window-12-18-vs-hindi

Verdict: regular divergence 3-10 is supported by the English extracts as a conservative default; 12 STRONG / 13-18 OK / >18 WEAK is not supported by the sources checked. Hindi gives mixed under-15 / dilution wording and no 18-bar rule. Reverse PRD/NRD has a distinct source conflict.

## Checked

- Reconciled source quotes in [WINDOW_RECONCILE_1104.md](../../malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md), including English extracts, six Hindi transcript search results, and `GbXnw_tNMtw_raw.txt`.
- Compared against `malkan_divergence_default.json:4-8,12-17` and `OPERATOR_DECISIONS.md:1685-1686`.
- Regular proposed window: min 3 SOURCED, max 10 SOURCED. Reverse proposed window: min 5 SOURCED, max 14 OURS.

## Findings

| Severity | File:line | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686` | The regular 12/18/>18 rule is labelled SOURCED without matching primary evidence in the searched sources. | English `Wvq1TZh8aF0` says "between three and 10" (`extract_Wvq1TZh8aF0.md:133`); Hindi `TO3pLafk7Us` lists 12 among diluting counts; 18 is NOT_IN_DATA. | Relabel the 12/18 thresholds OURS or find a distinct primary source. Follow-up card owns edits to params/chart flags. |
| LOW | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4-8` | Regular 3-10 matches the explicit English range, but English `cQ-y1oULkBw` also describes 15-20 as "still fine". | `extract_Wvq1TZh8aF0.md:131-133`; `extract_cQ-y1oULkBw.md:200`. | Keep 3-10 as conservative default; preserve the source-context caveat. |
| MED | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:12-17` | Reverse window is separate; 5 is sourced, but the upper bound is unresolved by source. | `GbXnw_tNMtw_raw.txt:382` says less than 15; `:460-461` says five to fifty. | Treat 14 as OURS pending a source resolution. |

## Commands

- `python MyTradingSys/research/malkan_hindi_2026-11-04/check_window_reconcile.py` -> `OK`.
- `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md` -> `PASS: 0 problem(s)`.

Follow-up cards created: none. Existing follow-up card `rsi-divergence-chart-draws-used-pivots` remains the implementation owner.
