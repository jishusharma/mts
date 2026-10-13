# RV08 [MED] Relay host= tag in lint and kick (d9306fe) and dispatcher model pin (c789011)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV08. Report: `MyTradingSys/research/revalidation/RV08_<UTC date>.md`.

Scope in: scripts/sched/relay.py, scripts/sched/handoff_lint.py, MyTradingSys/tests/test_relay.py, MyTradingSys/system/RELAY.md,
MyTradingSys/system/NEXT_SESSION.md, MyTradingSys/research/DISPATCHER_MODEL_CHECK_2026-10-12.md, MyTradingSys/system/relay_runs.jsonl.
Scope out: edits, firing kick/handoff for real, scheduled tasks.
Why: a wrong IDLE leaves a host without work; a wrong KICK launches a paid session with nothing to do.
Checks: write the missing cases as tests in the scratchpad and run them: lowercase / mixed-case `host=jis-nuc`; `host=any`;
two tags on one line; tag on a continuation line; a task that depends on a task of the other host; `hostname` with domain suffix;
a handoff with only DONE rows. Compare relay_runs.jsonl rows with the model claimed in DISPATCHER_MODEL_CHECK (6 of 20 Opus).
Already known: 30 tests pass on 2026-10-12.
