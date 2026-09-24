# NEXT SESSION HANDOFF
# Rewritten 2026-09-24T13:50Z by MTS-2026-09-24-1100Z.

STATUS: Loop ALIVE. lock 2832, snapshot 13:43Z. Build PASS 13:44:24Z.
Bugs 114 rows. Index 12 open IDs.

## SESSION MTS-2026-09-24-1100Z - WHAT LANDED

- Folder flatten. MyTradingSys/mts/* -> MyTradingSys/*.
  data/ -> runtime_data/. MyTradingSys/data/ -> MyTradingSys/market_data/.
  Three extracts folders consolidated to extracts/. 197 files rewritten.
  Java StateCodeEmitter L446+L477 path-fixed. start-trading-day.ps1 L53
  $LogDir fixed. Five Python files path-fixed.
- PROJECT_VISION.md added to SESSION_MANIFEST.json boot_files at position 4.
  Full read every session. Closes the layer-provenance gap.
- USER.md rules added: close items on decision; label sub-item context.
- T045 CLOSED. Materiality is consumer-layer. Producer emits raw.
- T046 d1 d3 d4 d5 resolved. d2 open (T-number plain titles).
- post_funding_vp demoted to display-only. Removed from candidate zone
  list and target pool in SetupCandidatesBuilder.java and
  math_object_builder.py. Java 9137C219 -> 9B058AED. Python
  28659A91 -> BF2E7FE2. Test inverted. 130/130 pass.
- B067 filed: crypto-hack gating audit. Item doc created. Cryptoadaptations
  hacks (funding rate, funding reset times, liquidation clusters, OI delta,
  aggregated CVD, UTC 00:00 daily open, slippage buffer, correlation-adjusted
  risk) all UNVALIDATED and mostly gating. Only post_funding audited.
- Loop restarted, log writes to runtime_data/. STATE_UPDATE_WARN gone.

## CRITICAL NOTES

- 10.0 pf bin size is SCREENER, no citation. Prior B059 session picked it.
  Still untagged at call sites MarketDataSnapshot.java L144, L1066.
- pf_vah no longer appears as rank-1. B066 (rank-1 distance gate) premise
  was based on pf_vah. Re-assess B066 before working it.
- UTC 00:00 CVD anchor is crypto hack #5. Still gates verdict via
  state_code.json and mts_math.py session CVD. Next audit candidate.
- 0.75 slippage multiplier is crypto hack #9. Applied to every net_rr.
  Verdict-changing. Next audit candidate.
- claude review of B059 confirmed: "multiples of 10" verifies code path,
  not drift. Real drift proof is a stable zone across cycles.

## OPEN QUEUE (BUGS.md, open rows only)

- B059  fix landed 2026-09-24, live tape confirmed. 10.0 still untagged.
- B063  divergence. NEEDS OPERATOR: restore or deprecate.
- B066  rank-1 distance gate. Premise shifted (pf no longer rank-1).
- B067  crypto-hack gating audit. UTC 00:00 + 0.75 slippage top of queue.
- T034  positioning states. Output type (boolean / strength / both).
- T035  multi-venue CVD. T1 web pass pending.
- T037  8 untested files. Blocked on pom.
- T038  deferred to ~21000 labels.
- T040  tick-delta. Threshold source-tier decision pending.
- T042  1w/1d/4h structure, no consumer. A/B/C.
- T044  hybrid REST/WS divergence alert. Not started.
- T046  d2 only open (T-number plain titles).

## NEXT SESSION - FIRST ACTION

1. Read items/INDEX.md + BUGS.md open rows.
2. Tag 10.0 pf bin size as SCREENER at MarketDataSnapshot.java L144 + L1066.
   Comment with proof obligation.
3. Audit UTC 00:00 CVD anchor for gating (B067 top item).
4. Commit session 1100Z work.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Critical files: hash, edit, hash, diff.
- Read target line from disk same turn before composing anchor.
- Anchor count must be exactly 1. # END appears as substring in many files.
- Build-Check prints to host, not stdout. Do not capture into a variable.
- MarketDataSnapshot.java is CRLF. math_object_builder.py is CRLF.
  SetupCandidatesBuilder.java is LF. Match on write.
- PROJECT_VISION.md doctrine: modules never gate core. Enforce on every
  new field or rule.

# END
