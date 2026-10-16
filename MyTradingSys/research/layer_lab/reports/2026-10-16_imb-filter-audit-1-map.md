BLOCKED

Card: imb-filter-audit-1-map
Date: 2026-10-16 UTC. Stage 1 evidence map; no predecessor report is named in the card.

The headline arithmetic matches. Historical input isolation and a row-level reproduction of the touch-bar defect are NOT_IN_DATA in the six permitted source files. No market rerun, VALIDATION file, or HOLDOUT file was read. The card must remain unfinished and the next stage must not advance.

## Checked material and command

All source paths below are relative to `MyTradingSys/research/imbalance_qriptal_2026-10-16/filter/` unless written in full. Read PRE_REG.md:1-124, COUNTS.md:1-47 and trials.csv:1-31, then parsed every row of events_dev.csv:1-5977 and trades_dev.csv:1-5977 before reading RESULT.md:1-132. Both CSVs contain 5,976 records. The six SHA256 values printed by the command match the read-only context pack. This establishes the snapshot correspondence; no git command or historical commit verification was performed.

Reproduction (standard library only, reads the six scoped source files; no market loader):

```powershell
python MyTradingSys/research/layer_lab/imb_filter_audit_1_map.py.txt
```

The script also prints the full column schemas, five selected rows and source hashes. It exited 0. This is a table recount, not a new strategy trial or market outcome run.

## Criterion evidence

C1: PASS

MATCH: RESULT.md:10,18,21,28-29,59 versus COUNTS.md:5,13-14, trials.csv:2-3 and trades_dev.csv:2-5977. Filter `small == True` versus `small == False`, sum `net_1` and divide by the respective count; subtract the unrounded means.

| group | n | distinct days | sum net R | mean net R | three decimals |
|---|---:|---:|---:|---:|---:|
| IMB | 3271 | 708 | -1198.7559488776 | -0.36647995991366555 | -0.366 |
| NOIMB | 2705 | 692 | -1263.1844077572 | -0.4669812967679113 | -0.467 |
| difference | | | | +0.10050133685424573 | +0.101 |

The command above recomputes these directly. Counts total 5,976; shared event/trade fields match row for row, with no duplicate day/level key. Mean `gross_1 - cost_1` is -0.3664799597921125 / -0.46698129722883547, agreeing within CSV rounding. trials.csv:2-3 stores -0.366480 / -0.466981. The headline difference uses unrounded cells: subtracting displayed three-decimal numbers alone loses information. This criterion confirms table arithmetic, not raw-bar execution or the statistical significance claims.

C2: BLOCKED

MATCH for the observable DEV output dates and this audit's inputs; NOT_IN_DATA for the stronger historical assertion in RESULT.md:5 that no VALIDATION or HOLDOUT file was read during the original study. PRE_REG.md:12-16 prescribes the cutoff and excludes the lc event table; a prescription is not an execution access manifest.

Evidence: events_dev.csv:1 and trades_dev.csv:1 contain only event timestamps/day identifiers, flags and (for trades) summarized outcomes. Parsing rows 2-5977 gives identical UTC timestamp bounds 2022-04-01 01:27 through 2024-06-30 22:26, zero timestamps at/after 2024-07-01, and zero timestamp/day mismatches. This matches COUNTS.md:3 and RESULT.md:5 for decision dates. The reproduction command opens only the six scoped files; none is a VALIDATION or HOLDOUT data file.

Missing evidence: no historical opened-file manifest, source-candle timestamps, outcome exit timestamps, or loader source is among the six permitted files. DEV decision dates cannot exclude a future input candle or later outcome bar. Therefore original-run input isolation cannot be certified from these tables alone. PRE_REG.md:20-22 and RESULT.md:110 also explicitly acknowledge that the supplied KEEP-family choice came from a period in standard VALIDATION; this is inherited selection information, not proof that this run opened a VALIDATION file. Do not conflate those claims.

C3: BLOCKED

NOT_IN_DATA: RESULT.md:109 alleges a touch-close direction and touch-bar target-credit defect, citing LC2 source and LC1 HOLD rates. PRE_REG.md:27-28,38,43 declares the causal replacement (previous close; no touch-bar target credit). Neither the cited original implementation nor previous-close/touch-bar OHLC observations is in the six-file scope. Both CSV headers at :1 lack those columns. The command inspects these committed trades (matching event line numbers):

| CSV line | touch t (ms) | level | side | width | rr1 outcome | exit |
|---|---:|---:|---:|---:|---|---:|
| 2 | 1648776420000 | 45185 | +1 | 182.0236 | stop | 45002.976 |
| 3 | 1648824360000 | 45735 | -1 | 182.0236 | stop | 45917.024 |
| 4 | 1648781580000 | 44375 | +1 | 182.0236 | target | 44557.024 |
| 5 | 1648779900000 | 44655 | +1 | 182.0236 | stop | 44472.976 |
| 6 | 1648776420000 | 45142 | +1 | 182.0236 | stop | 44959.976 |

For every row, previous close, touch OHLC, target/stop ordering and exit time are absent. Side and summarized exit price cannot reconstruct whether the touch close would flip direction or whether a favourable touch-bar excursion preceded the fill. These rows expose the missing evidence; they do not reproduce the defect. Invented bars would be a synthetic illustration, not the required committed-row reproduction.

MATCH: the present table has 2,761 targets / 5,976 = 46.20147256%, 3,144 stops = 52.61044177%, 71 time exits = 1.18808568% (trades_dev.csv:2-5977; RESULT.md:39,89). RESULT.md:109 reports LC1 HOLD 54-69%; that range is not independently supported by any permitted original LC1 table. Mechanistically, choosing direction after observing the touch close and crediting favourable movement before a fill can bias HOLD upward. The size and even the net counterfactual rate change on these rows are NOT_IN_DATA. The 46.2% target rate and claimed 54-69% HOLD range differ in period and rules and are not an estimate of the defect's effect. Q79 needs matched causal/leaky outcomes on the same rows before quantifying it.

## Findings and claim map

| Severity | File:line | Classification and finding | Evidence / proposed fix |
|---|---|---|---|
| LOW | RESULT.md:10; COUNTS.md:13-14; trials.csv:2-3 | MATCH: headline cells and group sizes | Independent recount above; retain figures. |
| HIGH | RESULT.md:5; events_dev.csv:1; trades_dev.csv:1 | NOT_IN_DATA: output dates do not establish original-run file isolation | Provide a committed original-run input manifest and causal source/exit-time evidence limited to DEV; review loader separately with explicit scope. |
| HIGH | RESULT.md:109; PRE_REG.md:27-28,43 | NOT_IN_DATA: required observed-row defect reproduction is impossible from summarized rows | Supply a small committed DEV evidence fixture with preceding close, touch OHLC, availability/exit times, and original versus corrected direction/outcome, plus scoped source excerpts. No VALIDATION/LC event table is needed or allowed. |
| MED | RESULT.md:109 | NOT_IN_DATA: numerical HOLD inflation is not identified | Use matched rows/rules; do not subtract rates from different periods. |
| MED | PRE_REG.md:20-22; RESULT.md:110 | MATCH: KEEP selection inherited from standard VALIDATION period | Retain disclosure; DEV-only market-file access would not make family selection independent of VALIDATION. |
| LOW | PRE_REG.md:39,46-48,57-70; RESULT.md:80,100-105 | MATCH as disclosed assumptions, not independently validated inputs | Touch-limit fill, fee/slippage, numeric anomaly thresholds, missing wick confirmation and regime confounding remain assumptions. Preserve SOURCED/OURS labels; no causal attribution follows from a group contrast alone. |

Scope limits: no check of pre-registration commit chronology (PRE_REG.md:5; RESULT.md:127), original builder/loader behavior, source quotes, trial-history m=16, or raw-bar fills was possible from this scope. These are assertions/references, not independently verified facts. Statistical SE/p-values and all secondary cells were not required by C1 and are not certified here. No contradictory headline cell was found.

## Follow-up cards created

None. Missing evidence and suggested expanded DEV-only evidence scope are specified above; this flow stops BLOCKED rather than unlocking its next stage.
