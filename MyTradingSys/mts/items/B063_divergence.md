# B063 - DIVERGENCE

Register row: MyTradingSys/mts/research/BUGS.md B063.
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

