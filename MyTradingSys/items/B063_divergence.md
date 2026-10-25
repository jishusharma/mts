# B063 - DIVERGENCE

Register row: MyTradingSys/research/BUGS.md B063.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (operator, session MTS-2026-09-22-1215Z)

Transcribed from the operator's paste. Leading tabs and trailing spaces preserved.
requirements - 
We need a worker for this audit + research task. 
	Audit -> Current MTS files and implementation and definition of divergence across all project files. Grasp the understanding and working code and verify the data correctness of Alerts thrown. 
	Research -> GOLAS -> Since we have different indicators, we need to do these in order:
		A. For each indicator, research how the divergence is calculated by professional traders verified institutions - attach proof
		B. Then in CRYPTO space, how each indicator is related to each other in terms of actual use and their setup types - every possible detail
		C. What are the consensus on internet about the fine tuning on these indicator values and trading methods that work most of the time for BTC specially!
		D. Research how we can back test these findings with historical and live data

## STATE

2026-09-22 OPEN. Wiring not started.
Prior work: DIVERGENCE_AUDIT_AND_RESEARCH.md (worker reply 2026-09-21). GOLAS_CD_WEB_2026-09-21.md (web reinforcement for GOLAS C and D). Both T3 or lower. Neither meets the T1/T2 bar the ask sets.
Detectors on disk: tape-watch.ps1 L59-60 (two-term price/CVD, one snapshot). divergence_monitor.py (10m window, thresholds 30pt/200/20). SetupScreener.java L54 (boolean, producer unknown). mtf_flow_alignment_design (inert).

## UPDATES (chronological, newest last)


### 2026-09-22T17:30Z - coordinator, session MTS-2026-09-22-1215Z

State on open: wiring not started. Prior worker outputs obsolete-marked; retained for history.

Next-session worker plan for B063:

- W1  Audit pass. Verify the divergence alerts actually fire and are correct against the current live detector. Disk only. Output to Dumps/workers/W1_divergence_audit/. Report correctness findings and any alert mismatches.
- W2  GOLAS-A. Institutional definitions per indicator. Tier-locked T1/T2 only. Reject anything that does not meet the pre-committed tier; do not lower the bar. Attach proof per source.
- W3  GOLAS-B. Cross-indicator relationships in crypto, setup-type mappings. T2/T3 with sources named.
- W4  GOLAS-C. BTC tuning consensus. T1/T2 for any claim presented as working most of the time; T3 must be labeled.
- W5  GOLAS-D. Backtest design. Data sources, replay method, thresholds, pass/fail criteria. No execution this cycle.

Each dispatch carries the R1-R5 protocol from MyTradingSys/methodology/live_session_protocol.md. Replies land in Dumps/workers/<id>/ and updates append below in this doc.

### 2026-09-23T15:30Z - coordinator, session MTS-2026-09-23-1445Z

Source fold. Added from T039 sweep source 2 (compiled_output_audit_20260915.md L104, cvd row of the schema/emitter gap table).

Verbatim action cell (L104):
> Restore divergence or deprecate in schema.

Context: schema declares value, slope, divergence, last_3_delta, confidence, source. Emitter emits value, slope, last_3_delta, cvd_recent, confidence, scope, session_start_utc. Gap columns: divergence, source. Two unresolved directions: restore divergence or deprecate in schema, and source-string mismatch.

This fold is documentation only. No schema change. Ties to the detector audit already recorded above.

### 2026-10-04T10:15Z - builder, session MTS-2026-10-04-1009Z-APP-BLD-t052-b063-t046

DECISION: DEPRECATE divergence in the snapshot schema. Do not restore.
Why:
- Provenance. market_data/data_schema_v1.2.0.md:148: "Tom does not define 'divergence' numerically. The boolean flag is a
  screener heuristic." (also L452, L138). The only numeric rule on disk (divergence_monitor.py 30pt / 200 / 20, 10m)
  has no Tom source = NO-SOURCE.
- Tom's only divergence words are a guard, not a detector: extracts/fresh/extract_rFPCtOcfUMI_fresh.md:71 (verbatim in raw
  rFPCtOcfUMI:13) "don't trade the delta divergence alone always use confirmation". No computation is given.
- The emitter never wrote the field (compiled_output_audit_20260915.md L104), the live alerts do not fire on it, and no
  condition file or verdict reads it. Restoring means inventing a threshold plus a verdict consumer.
- Fabio CC-2 absorption_cvd (ANALYST_LAYER_FRAMEWORK.md:144) is the candidate for a separate layer; it is not this field.
Files that change on the DEPRECATE path (nothing changed this session):
- MyTradingSys/market_data/data_schema_v1.2.0.md L138, L430, L452 (remove divergence from the cvd row; keep the Tom guard as a note)
- MyTradingSys/market_data/data_state_document.md L20, L151 (CVD field list; TC pullback row)
- MyTradingSys/market_data/sample_btc_snapshot.json L109 (divergence: false)
- MyTradingSys/research/MTS_DICTIONARY.md L200-213 (DIVERGENCE section: state deprecated, point to the Tom guard)
- MyTradingSys/research/_archive/loose_2026-10/compiled_output_audit_20260915.md L104 (close the "restore or deprecate" action)
- MyTradingSys/research/BUGS.md B063 row (close). Detectors tape-watch.ps1 and divergence_monitor.py are tooling, left as is.
Files that would change on the RESTORE path (blocked: needs a sourced Tom definition first):
- MarketDataSnapshot.java (cvd emitter), data_schema_v1.2.0.md, a conditions/*.md rule, math_object_builder.py,
  Compute-Verdict in start-trading-day.ps1 and backtest/verdict.py (critical files, four-step proof), plus tests.
Next step if the operator agrees: one small doc-only task for the six DEPRECATE files above.
