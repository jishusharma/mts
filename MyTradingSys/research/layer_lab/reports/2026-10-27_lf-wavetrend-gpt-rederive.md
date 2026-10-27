# lf-wavetrend-gpt-rederive — 2026-10-28

FIX-FIRST: 133 arithmetic/aggregate consistency checks MATCH, 0 MISMATCH; 106 raw outcome fields NOT_IN_DATA. These are not 133 independently validated backtest results.

Deliverable: `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/wavetrend.md`. It embeds the standalone standard-library recomputation script, exact PowerShell run command, full comparison tables, tracked evidence inventory and SHA-256 receipts. Re-extraction and a second execution produced byte-identical evidence output. Synthetic long/short/incomplete-horizon assertions validate the written return formula independently of producer modules.

Checked: layer_index.json:716-735 and its seven named source/result documents; EXPOSURE_LEDGER.csv:6-7; FORMULAS.md:133-142,345-351,468-479; counts/CELLS.csv:2-10 and matching context counts; RESULT.md:13-21,27-62,103-128; aggregate atlas JSON, run log, quality/strata tables and later input-manifest metadata. Paths shortened here refer to the WaveTrend study directory unless otherwise named. Exact claim file:line and input hashes are in the deliverable. Permitted evidence: tracked public DEV artifacts only; no untracked bars, sealed partitions, calculation-code imports, tuning, new outcome trials or Holm calculation.

| Severity | Evidence | Finding | Classification | Proposed next evidence |
|---|---|---|---|---|
| HIGH | Outcome table in deliverable; tracked CSV/JSON inventory | No event-level prices/timestamps or control draws in permitted evidence. N and mean cannot be independently reconstructed from summaries. | NOT_IN_DATA (106 fields) | Exact historical DEV event/price and control-draw ledger, bound to input hashes |
| MED | PRE_REG.md:80-84; ATLAS_STUDY_SPEC.md:24-25; FORMULAS.md:468-479 | Atlas outcomes are gross percent/bps, not risk-normalized R or executed trades; no risk denominator or execution/cost ledger exists in reviewed evidence. | MATCH for written gross contract; NOT_IN_DATA for mean R/net result | Defined strategy/risk/cost ledger if a separately authorized study needs R |
| LOW | counts/CELLS.csv:2-10; RESULT.md:13-21,27-62 | Side sums, duplicate count-table entries and printed aggregate conversions agree. W04 has 1155 frozen vs 1154 outcome-bearing episodes; difference 1 agrees, truncation cause unverified. | MATCH for aggregate arithmetic; NOT_IN_DATA for raw cause | Omitted event timestamp and horizon bars |

Historical C1 limitations in AUDIT_2026-10-18.md and later dispositions are preserved; no corrected detector result is inferred. DEV dates calculate to 912 calendar days; ledger metadata and saved zero-read flags agree, while actual historical I/O and timestamp membership remain NOT_IN_DATA. Later registry cost 0.14 is not evidence of fee-net atlas returns. No keep/drop verdict.

Follow-up cards created: none. Existing separate C1 and Holm work is outside this card. No new outcome run: no TRIALS entry required.
