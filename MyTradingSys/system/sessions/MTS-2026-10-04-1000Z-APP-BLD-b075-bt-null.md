# MTS-2026-10-04-1000Z-APP-BLD-b075-bt-null
surface: APP (Code tab); Maven 3.9.14 and pytest were reachable from it, no CLI fallback needed
host: JIS-NB
model: Sonnet 5.5
role: BLD
branch: fast-track
predecessor: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup
status: closed
Task: BUILD_PIPELINE 1.2 (B075 residual, B084, B085 diagnosis).

## Origin of the BT 0.0 (B075 residual)
MarketDataSnapshot.java:1191 (fetchHistoricalSnapshot) wrote order_book_depth.bid_ask_ratio = 0.0; SetupCandidatesBuilder
detectProofs read it with asDouble() and toJson rounded it into proof.book_imbalance. 86313de only nulled conditions.book_imbalance.
## Changes
- MarketDataSnapshot: historical bid_ask_ratio -> putNull; added to data_quality.unavailable_fields.
- SetupCandidatesBuilder: bookImbalance is Double (null = no data); proof emits JSON null; countSignals null-safe;
  net_delta_1m read null-safe (null -> cvdAligned false, same outcome as the old asDouble 0.0 but explicit). Live numeric path unchanged.
  Call-site lines in the brief (552/635/822) had drifted; actual sites were :633 (emit), :820 (net_delta_1m), :833 (bid_ask_ratio).
- math_object_builder.py (critical file; staged .new, promoted, backup .pre_b075bt): result["proof_book_imbalance"] = number, or
  "UNAVAILABLE" for null / absent / 0.0 / non-numeric. Contradiction logic untouched (details strings unchanged).
## Tests (both failed before the change)
- HistoricalBookImbalanceNullTest (Java, 3 tests; 2 failed pre-change: proof 0.0, source 0.0).
- test_b075_bt_book_null_unavailable.py (5 tests; 5 failed pre-change).
## Verification
Java: mvn test on a scratch copy (live target/ untouched; MyTradingSys/system/*.json copied in for NetRrFloor/RunnerMinDistance): 50/50.
Python: pytest MyTradingSys/tests: 265 passed, 3 skipped. File stats re-read with Python, not the tool that wrote them.
## B084 note
BT-path 0.0 now cannot arise from the builder; Python additionally treats a 0.0 as UNAVAILABLE. No separate gate added (out of scope).
## B085 diagnosis (no change)
Rule at math_object_builder.py:463-464 is a mirror of :454-455 (pos,pos,pos vs SHORT / neg,neg,neg vs LONG); pinned symmetric by test_proof_direction.py:55.
The asymmetry is upstream: MarketDataSnapshot.java:696 labels a bar `(2*buy-vol)>0 ? "positive" : "negative"`, so a zero-delta bar
becomes "negative". That biases last_3_delta toward neg,neg,neg and suppresses longs only. No Java test pins the zero-delta label
(only CvdAnchorDisplayOnlyTest mentions last_3_delta). Hypothesis, not yet measured against allshorts.diag.jsonl (215:105 skew).
