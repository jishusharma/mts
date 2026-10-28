# Rules moved out of CLAUDE.md (size cap B18); the one-line forms stay in CLAUDE.md
Moved 2026-10-25 by the Lead to make room for the operator principles. Text is verbatim.

- Layers (operator 2026-10-13, replaces "Tom is core"): no fixed core. Tom, Fabio and every other system are layers (combine, filter or switch off); fee-net out-of-sample results decide what trades, never doctrine (PROJECT_VISION).

- Numbers (operator 2026-10-13): label each parameter SOURCED (trader's words, quote + file:line) or OURS (judgement or tuned). OURS is allowed: chosen on DEV, checked once on VALIDATION, holdout read once, variants in the trial ledger. Never call OURS the trader's.

## Longer originals of lines shortened in CLAUDE.md (same date, verbatim)

5b. After `get_usage`, once: `python scripts/dev/mts_signal.py budget --login <A|B|C> --five <%> --week <%> --reset <UTC>` (jishusharma1985=C).

5c. Then `python scripts/dev/exhaust.py plan --login <X> --week <%> --five <%> --reset <UTC>`; phase plan/exhaust: follow `MyTradingSys/system/EXHAUST_PHASE.md` (not subagents).

- Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety checks fail closed. New timeframe or layer family: grep every TF/family map. Whoever sets AUTO_PAUSE logs owner + expected end in SUPERVISOR_LOG; each wake clears or escalates an overdue pause.

- The live tree (`.mts_live`) runs the testnet system and changes only by a manual or coordinator-run deploy (DEPLOY_RUNBOOK.md). Builders never deploy, stop/restart processes, touch HALT files or open trades. No scheduled tasks or routines on any device.

5. SHORT SESSIONS (unattended workers; an operator-driven session ends on his word, q-v1-turn-caps): one session = one task; hand over when it is done, after 10 operator turns or the tool-turn cap (WORKERS.md rule 5), whichever first (commit, then steps 3-4, one line, stop). Live market threads: after 5 screenshot reads.

4. Hand-over: no schedulers or routines run anywhere (SCHEDULING_POLICY.md); nothing starts the next session by itself. Overwrite NEXT_SESSION.md, `sync.py ship`; coordinator (SUPER_SESSION.md) starts the next. The block must run with zero operator input (defaults for open questions).

- Interactive sessions and subagents: Sonnet (implementations, spec-derived tests), Opus only when the operator names it; Haiku for mechanical work; worker type + model: WORKERS.md (card fields `worker`, `est_turns`). Wait on a queue with one background shell; spot-check one worker claim.
