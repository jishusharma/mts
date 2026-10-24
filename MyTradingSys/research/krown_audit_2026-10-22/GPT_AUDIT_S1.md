# GPT independent audit: Confluence S1

Audit date: 2026-10-24 UTC. Card: `confluence-s1-gpt-audit`. No git, sync, task closure, code/test/card edits, or outcome-column reads were performed.

**Overall: conditional arithmetic MATCH; leak test MATCH/PASS; full source-independent verification INCOMPLETE.** One HIGH specification discrepancy was found. These results do not certify S1 as a fully verified base.

Reproduce from the repository root:

`python -B MyTradingSys/research/gpt_burn_2026-10-24/gx2-confluence-s1/audit.py`

The command exits 0 when its audit assertions pass; inspect the complete JSON for findings and missing sources. Exit 0 is not an S1 approval.

## Independence and coverage

The three counts are interpreted as the three pooled S cells explicitly named in `MyTradingSys/research/krown_audit_2026-10-22/PRE_REG_S1_COUNTS.md:11`: S=+3, S>=+2, S<=-2. Supplemental pooled n, weeks and MDE are also re-derived below.

The script independently reconstructs all 5,472 four-hour closes from 21,888 raw one-hour bars before 2024-07-01, computes BBWP from FORMULAS.md 21.5 (population SD, strict prior-only percentile), its previous-six minimum and both direction definitions. It uses 87,552 raw 15-minute closes for D3. The raw NPZ arrays are loaded before masking, as in the producer; no post-cut bar value enters a calculation. No outcome file or column is opened.

It parses every row of context_dev.csv and joined_events.csv: 7,115 context rows (1,643 daily and 5,472 four-hour), 23,213 event-key rows, 22,862 usable layer-events. It ignores stored usable flags, dimension scores, S, and join keys while computing its own results, then compares every stored value. There are zero mismatches for usable, D1, D2, D3, S, or selected context rows under the documented six-bar implementation. All four-hour fields match the raw-bar re-derivation.

**Limitation:** event timestamps, sides, membership, and row order come from the producer-generated joined_events.csv; daily trend, zones, ATR and range fields come from producer-generated context_dev.csv. The original sealed event tables and daily OHLCV source are absent. Therefore this is a separate implementation over partially shared snapshots, not the card-required independent regeneration from original sources. No unconditional count MATCH is claimed. Duplicates/status filtering and daily detector parity cannot be verified independently here. This limitation cannot be removed by recounting stored S values.

Pooled deduplication retains the first usable row per (decision_ts, side), reproducing the published pool convention and layer order. Alternative event-type ownership of simultaneous events was not tuned.

## Three counts: per-number verdict

COUNTS.md references below use `MyTradingSys/research/krown_audit_2026-10-22/run/COUNTS.md`.

| Cell | COUNTS.md count / share | Separate six-bar computation | Verdict on snapshots | REVIEW_OPUS F6 direction computation | Verdict against F6 |
|---|---|---|---|---|---|
| S=+3 | 12 / 0.07% (:80, :82) | 12 / 0.06576424% | MATCH, conditional | 12 / 0.06576424% | MATCH, conditional |
| S>=+2 | 353 / 1.9% (:80, :82) | 353 / 1.93456459% | MATCH, conditional | 351 / 1.92360388% | MISMATCH, conditional |
| S<=-2 | 1,849 / 10.1% (:80, :82) | 1,849 / 10.13317258% | MATCH, conditional | 1,849 / 10.13317258% | MATCH, conditional |

The S>=+2 F6 mismatch is two events; rounded 1.9% conceals it. F6 changes other histogram cells even where the tail count remains equal.

| S | -3 | -2 | -1 | 0 | +1 | +2 | +3 |
|---|---|---|---|---|---|---|---|
| COUNTS.md :80 / separate six-bar computation | 260 | 1589 | 5628 | 7230 | 3187 | 341 | 12 |
| Separate F6 direction computation | 256 | 1593 | 5600 | 7242 | 3205 | 339 | 12 |

| Supplemental number | COUNTS.md :56 | Separate computation | Verdict |
|---|---|---|---|
| Unique pooled n | 18,247 | 18,247 | MATCH, conditional |
| Distinct ISO weeks | 128 | 128 | MATCH, conditional |
| Distinct days | 895 | 895 | MATCH, conditional |
| Population sd(S) | 0.971 | 0.971289616 | MATCH after rounding, conditional |
| Week-clustered slope MDE, R/S | 0.170 | 0.169742911 | MATCH after rounding, conditional |
| Day-clustered MDE footnote | 0.075 | 0.074746322 | MATCH after rounding, conditional |

MDE uses the published design assumptions in COUNTS.md:54 (OURS m=17, rho=0.1, sd_R=1.5, power z=0.84), with a separately calculated inverse normal quantile and population sd(S). These assumptions are not independently estimated outcomes. The 0.10 R/S gate remains DESCRIPTIVE.

## Leak test: per-check verdict

COUNTS.md:16 asserts strict availability; it does not publish a numerical leak-test result. Expected behavior comes from `MyTradingSys/research/krown_audit_2026-10-22/PRE_REG_S1_COUNTS.md:14-24`: available_at = close + 60,000 ms, use only available_at < decision_ts; reject deliberate leaks and preserve truncated-history rows.

| Check | Required / published behavior | This audit | Verdict |
|---|---|---|---|
| Context timestamp metadata | close + 1 minute | 0 violations / 7,115 rows | MATCH/PASS |
| Actual stored joins | context available strictly before decision | 0 timing violations / 22,862 usable layer-events, both TFs checked | MATCH/PASS |
| Independent daily boundary oracle | no real-join violations, equality excluded | 0 / 4,929 decisions (available_at-1, available_at, available_at+1) | MATCH/PASS |
| Join keyed on bar open | planted variant rejected | 4,928 / 4,929 violations independently counted | MATCH/PASS |
| One-bar-forward row join | planted variant rejected | 4,928 / 4,929 violations independently counted | MATCH/PASS |
| New synthetic daily prefix recomputation | full and truncated rows equal | 6 / 6 equal, including weekly fields and confirmed pivots | MATCH/PASS |
| Forward-reading synthetic builder | planted dependency rejected | 5 / 5 non-terminal prefixes detect copied next close | MATCH/PASS |
| Shipped test_krown_context suite | passes, including four-hour truncation | 20 run, 0 failures, 0 errors | MATCH/PASS |
| In-memory planted-error red run | shifted-join test must fail if checker accepts leaks | disabled checker: 1 run, 1 assertion failure, 0 errors | MATCH/PASS |

The red run replaces only the in-memory check_point_in_time function with a checker that always returns no violations, runs test_shifted_join_leaks, and restores the function. No disk file is changed. This establishes sensitivity to an undetected planted leak; it is not a claim to have run the historical pre-change tree. Historical pre-change failure was not verified because git was prohibited.

Formula hand checks are independently calculated from `MyTradingSys/backtest/layers/FORMULAS.md` sections 1, 21.5 and 21.7: closes [10,10,12,11,15,15,14], basis 2, lookback 3 give BBWP [100,0,100/3] at indices 4..6; closes [10,11,10,12], period 2 give seeded gain/loss 0.5/0.5 then 1.25/0.25, hence RSI [50,100-100/6] at indices 2..3. Production matches within 1e-9. No expected value is taken from a production function.

## Findings

1. **HIGH — expansion-direction definition differs from the referenced review.** `MyTradingSys/backtest/layers/krown/krown_context.py:171` explicitly specifies six-bar price direction, implemented at :181 as close[i] minus close[i-6]. `MyTradingSys/research/krown_audit_2026-10-22/REVIEW_OPUS.md:24` F6 instead defines the sign since BBWP_4h was last <=50; design s9.2 adopts the review amendments. A constant six-bar horizon can point in the opposite direction and change whether a trade fades the expansion. Independent raw-bar calculations find 3,139 four-hour direction differences and 366 changed usable layer-event scores. Keeping the population, frozen bands, exhaustion/freshness rules and pool order fixed, S>=+2 becomes 351 rather than the published 353 (COUNTS.md:80). This is a specification mismatch, not a detected future-data leak. If six bars is intended, it needs an explicit approved definition/amendment before downstream use; this audit does not change either definition.

   Reproduce with the command above; inspect direction_row_differences, score_changes, example and review_direction_conditional. Concrete event: bb_top_reversal, decision_ts=1643122800000, h4_open_ms=1643097600000, six-bar direction +1 versus F6 direction -1; (D1,D2,D3,S) changes from (0,+1,0,+1) to (0,0,0,0). The F6 comparison resets its reference at every BBWP<=50 observation, including the current bar when applicable. It isolates only this direction-definition difference.

2. **LOW — absent inputs prevent the requested independent source-data audit.** `MyTradingSys/research/krown_audit_2026-10-22/run/COUNTS.md:12` identifies regenerated run/sealed event tables as its source; `MyTradingSys/backtest/layers/krown/run_counts.py:27` names F:/MTS/data/krown_daily/BTCUSDT_1d.csv. Both paths are absent in this audit environment. Thus the count matches above cannot certify source membership, filtering, timestamp semantics, or daily indicators; reusing event keys and daily fields is explicitly disclosed. This is an audit reproducibility limitation, not evidence that the original run had incorrect counts. Reproduce with the command above: missing_sources has exactly two entries. A fully independent rerun requires those DEV inputs (projected timestamp/side/status/event fields only; keep outcomes sealed).

No production fix was attempted. DEV_EXT event counts and missing layers remain outside the available source reconstruction; their incompleteness is already disclosed in COUNTS.md:14 and its final section.

## Delivery and task status

Requested GPT_AUDIT_S1.md and dated layer-lab report were written at the card-specified paths, as expressly allowed by the user output exception; audit scripts and report.md are under the task directory. No commit, push, sync.py, or tasks.py done was run. The harvester must not interpret report-file existence as completion of the independent-source requirement: that step remains incomplete for the missing-input reason above.

Result: 3/3 snapshot counts match conditionally; leak checks pass; HIGH F6 direction mismatch changes S>=+2 from 353 to 351; full independent source rebuild remains incomplete.
