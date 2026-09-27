# B071 - FAIL-OPEN: PROOF-DIRECTION CHECK DEFAULTS TO "ALIGNED" ON PYTHON ERROR

Opened: 2026-09-26 by session claude-sonnet-4-6-2026-09-26.
Severity: HIGH (silent bad signal; blocks mainnet gate).
Status: CLOSED (code fix applied 2026-09-27; live PowerShell execution not yet observed).

## DESCRIPTION

When the loop's Python call errors (any exception, timeout, or non-zero
exit from the Python rules layer), the proof-direction check silently
defaults to "aligned" — treating an unknown state as a confirmed trading
signal. This is fail-open behavior. The system should fail closed: any
error in the Python evaluation must be treated as NO SIGNAL, not as a
confirmed direction.

## OBSERVED CONSEQUENCE

2026-09-24 18:55 UTC: A SETUP_FORMING verdict was produced under
conditions where the Python call had errored. The proof-direction check
returned "aligned" by default, propagating a bad signal to downstream
consumers. The error was silent — no alert, no halt, no log entry
distinguishing a real "aligned" result from a defaulted one.

## ROOT CAUSE (as understood)

The PowerShell loop's Python invocation does not distinguish between:
  a) Python returned exit 0, result = "aligned"
  b) Python errored / returned non-zero / returned empty / timed out

In case (b), the condition evaluates as if (a) were true.

## REQUIRED FIX

The proof-direction check must:
1. Capture exit code and stdout/stderr separately.
2. On any non-zero exit, empty stdout, or exception: emit an explicit
   ERROR state (not "aligned", not "unaligned") and halt/alert.
3. The ERROR state must be logged with the raw exit code and stderr
   so the cause is diagnosable.
4. No downstream consumer may treat ERROR as a trading signal.

Fail-closed is the only acceptable behavior. The fix must be verified:
  - Force a Python error (bad script, nonexistent file, deliberate
    exception) and confirm the loop halts, does not emit a verdict,
    and logs the error with full detail.

## BLOCKS

- T050 Phase 5 (live trading). B071 must be fixed before any live order
  is placed. A bad signal reaching an executor is an unacceptable risk.
- Step 8 mainnet gate (explicit dependency per handoff).

## UPDATES

2026-09-26: Filed. Bad SETUP_FORMING on 2026-09-24 18:55 traced to this
bug. Operator confirmed: must fail closed before any automated executor.

2026-09-27: Fix applied to the live files (start-trading-day.ps1, build_mo_cli.py, verdict.py) - previously staged as .new, Opus-reviewed. Implementation: proof_dir defaults to "error" instead of "aligned"; compute_verdict caps any WATCH/SETUP_FORMING under an error proof_dir at WAIT_PROOF. Verified via fail_closed_spec.py (S1+S2 PASS, 0/9287 real snapshots leak WATCH/SETUP_FORMING under fail_closed) and verdict_golden.py (NO CHANGE vs baseline, 9160 compared). NOT verified: an actual live PowerShell run on a running candle loop - no PowerShell available to any session so far. Also note: the required-fix spec above asked for halt/alert on error; the shipped fix instead caps at WAIT_PROOF with a logged PD_ERROR line (no halt, no popup alert), matching the plan's D7 recommendation - which was still an open, unruled operator decision at the time this landed. If halt/alert behavior is actually required, this needs a follow-up change.
2026-09-27: D7 ratified by operator (see research/core_readiness_2026-09-27/D1_D7_DECISION_BRIEF.md).
The shipped WAIT_PROOF-cap-with-log-line behavior is the final, accepted
fix - no halt+alert being added on top. This closes the gap between the
original required-fix spec (halt+alert) and what shipped; operator chose
the shipped behavior deliberately, not by default.
