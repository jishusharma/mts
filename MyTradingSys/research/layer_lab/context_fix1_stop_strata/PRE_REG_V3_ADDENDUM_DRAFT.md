# PRE_REG_V3 addendum draft: stop comparability and stratified E

Status: draft for the supervisor to attach before any `study_v2.py` outcome run. This file does not authorize or perform that run.

## FIX-FIRST 1 — counts before outcome read

The V2 count-only pool is same-side `f1_at_level` rows with `f3_stop_tf != none`, excluding C and decision times within 24 hours (inclusive) of any same-side C event. C remains the V2 trigger. For each side and pool print the count, `f3_stop_tf` shares, and median/p90 `f3_stop_pct`. `f3_stop_pct` is the ladder stop width as known at decision time T; do not load/use entry or any price after T for these diagnostics.

Count-only DEV result from cached decision frames, 2022-04-01 through 2024-06-30:

| pool | side | n | D share | 12h share | 8h share | median stop_pct | p90 stop_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| C | long | 554 | 81.95% | 12.82% | 5.23% | 2.084% | 3.718% |
| V2 control pool | long | 6,664 | 86.97% | 8.88% | 4.14% | 1.616% | 3.785% |
| C | short | 456 | 82.89% | 14.04% | 3.07% | 2.161% | 4.509% |
| V2 control pool | short | 8,021 | 87.94% | 8.43% | 3.63% | 1.619% | 3.526% |

Relative median gap is `abs(control_median - C_median) / C_median`: long 22.45%; short 25.10%. The short side exceeds 25%, so mark `R units not comparable` for short. Under the V2 verdict, this precludes calling the result FAIL; preserve INCONCLUSIVE unless all other registered conditions support PASS and stop geometry is addressed. This flag is side-specific.

## Stratified E helper for the eventual read

The outcome run may call `stratified_e(C_rows, control_rows, kmin=10)` after the ordinary matching/read has produced net_R rows. It groups by side and `f3_stop_tf`; for each stratum E is the mean C net_R minus mean control net_R. A stratum with fewer than 10 control rows has E=null and is ineligible. Print these rows beside the ordinary pooled verdict, with event and control counts. This helper is post-outcome by definition and must not be used in the count-only phase.

PASS additionally requires stratified E > 0 in strata that together contain at least 80% of matched C events. Compute coverage as positive eligible strata's `n_events` divided by all matched C events; require coverage >= 0.80. Keep the ordinary matched event/control construction and all other V2 gates unchanged. Do not call FAIL when either side's C/control median stop gap exceeds 25%; report `R units not comparable` and use INCONCLUSIVE under this fix-first rule.

## Implementation and provenance

`context_fix1_stop_strata/stop_strata.py` provides count summaries, the relative-gap flag, and the stratified E helper. Input rows can use `f3_stop_pct` or its normalized `stop_pct` alias. No post-T prices are required for the count-only summary. Synthetic tests hand-check shares, median/p90, stratified E/kmin, and the >25% flag. The real DEV counts above used the cached frames named by `context_asof.CACHE`; no `study_v2.py` run or outcome read was performed.
