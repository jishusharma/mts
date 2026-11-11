counts: MATCH=6 DIFF=0 NOT_IN_DATA=0 (sum 6)

# Gemini Blind Read: scripts/sched/dispatch_gate.py against its docstring

- Date: 2026-11-11
- Card: `gemini-blind-read-dispatch-gate-docstring-1111`
- Target: `scripts/sched/dispatch_gate.py`
- Test: `MyTradingSys/tests/test_dispatch_gate.py`

## Clauses and Audit Table

| Clause # | Docstring Clause Requirement | Implementation Status | Implementation Code (`scripts/sched/dispatch_gate.py`) | Test Verification (`MyTradingSys/tests/test_dispatch_gate.py`) |
|---|---|---|---|---|
| 1 | TICK NOOP launches nothing | MATCH | SOURCED `dispatch_gate.py:79-80` `if first.startswith("TICK NOOP"): return "NOOP", first`, `dispatch_gate.py:107-118` `if verdict == "NOOP": ... print("GATE NOOP", line); return 0` (no launch subprocess unless `refine=REFINE_NEEDED`) | SOURCED `test_dispatch_gate.py:43-51` `test_noop_launches_nothing_and_passes_hourly_off`: asserts `GATE NOOP` and `prompt.txt` does not exist |
| 2 | TICK KICK launches ONE headless relay session with the tick output on stdin | MATCH | SOURCED `dispatch_gate.py:77-78` `if first.startswith("TICK KICK"): return "KICK", first`, `dispatch_gate.py:123-134` `p = subprocess.run(launcher_argv(a.launcher), input=PREAMBLE + r.stdout, ...)` | SOURCED `test_dispatch_gate.py:64-70` `test_kick_launches_one_session_with_the_tick_text`: asserts prompt has tick text and preamble |
| 3 | REFINE_NEEDED launches a session | MATCH | SOURCED `dispatch_gate.py:109-116` `if "refine=REFINE_NEEDED" in hourly and not a.dry_run: p = subprocess.run(launcher_argv(a.launcher), input=REFINE_PREAMBLE + hourly, ...)` | SOURCED `test_dispatch_gate.py:57-62` `test_refine_needed_hour_launches_one_refiner_session`: asserts prompt has `Refiner run` and `Do NOT run relay.py tick` |
| 4 | exit 1 on an unparsable tick | MATCH | SOURCED `dispatch_gate.py:81` `return "ERROR", first or "no TICK line"`, `dispatch_gate.py:103-106` `if verdict == "ERROR": ... print("GATE ERROR", line); return 1` | SOURCED `test_dispatch_gate.py:84-87` `test_unparsable_tick_never_launches`: asserts exit code is 1 and no launch prompt created |
| 5 | exit 2 when the launcher binary is missing | MATCH | SOURCED `dispatch_gate.py:91-95` `if not (shutil.which(argv0) or Path(argv0).is_file()): ... return 2` | SOURCED `test_dispatch_gate.py:76-82` `test_missing_launcher_does_not_tick`: asserts exit code is 2 and tick args file not created |
| 6 | one log line per run in ~/.claude/mts-dispatch-gate.log | MATCH | SOURCED `dispatch_gate.py:37-47` `home().mkdir(parents=True, exist_ok=True); with open(home() / "mts-dispatch-gate.log", "a", ...) as f: f.write("%s %s\n" ...)`; logged exactly once per execution path: line 93 (NO_LAUNCHER), line 104 (ERROR), line 108 (NOOP), line 120 (DRY), line 126 (KICK) | SOURCED `test_dispatch_gate.py:37-38` sets `MTS_RELAY_HOME` to `self.d / "home"` where log is written |

## Verification Details

1. **Clause 1 (TICK NOOP launches nothing):**
   - Docstring: SOURCED `dispatch_gate.py:4` `"NOOP costs nothing"`
   - Code: SOURCED `scripts/sched/dispatch_gate.py:79-80`, `scripts/sched/dispatch_gate.py:107-118`.
   - Test: SOURCED `MyTradingSys/tests/test_dispatch_gate.py:43-51` (`test_noop_launches_nothing_and_passes_hourly_off`) and `MyTradingSys/tests/test_dispatch_gate.py:52-55` (`test_idle_hour_with_refine_ok_launches_nothing`).
   - Verdict: MATCH.

2. **Clause 2 (TICK KICK launches ONE headless relay session with the tick output on stdin):**
   - Docstring: SOURCED `dispatch_gate.py:4-5` `"KICK launches ONE headless relay session with the tick output (NEXT / UNLOCK commands and relay_session.md) as its prompt."`
   - Code: SOURCED `scripts/sched/dispatch_gate.py:77-78`, `scripts/sched/dispatch_gate.py:123-126`.
   - Test: SOURCED `MyTradingSys/tests/test_dispatch_gate.py:64-70` (`test_kick_launches_one_session_with_the_tick_text`).
   - Verdict: MATCH.

3. **Clause 3 (REFINE_NEEDED launches a session):**
   - Docstring: SOURCED `dispatch_gate.py:6` `"and launches a session only for REFINE_NEEDED."`
   - Code: SOURCED `scripts/sched/dispatch_gate.py:109-116`.
   - Test: SOURCED `MyTradingSys/tests/test_dispatch_gate.py:57-62` (`test_refine_needed_hour_launches_one_refiner_session`).
   - Verdict: MATCH.

4. **Clause 4 (exit 1 on an unparsable tick):**
   - Docstring: SOURCED `dispatch_gate.py:10` `"1 = unparsable tick"`
   - Code: SOURCED `scripts/sched/dispatch_gate.py:81`, `scripts/sched/dispatch_gate.py:103-106`.
   - Test: SOURCED `MyTradingSys/tests/test_dispatch_gate.py:84-87` (`test_unparsable_tick_never_launches`).
   - Verdict: MATCH.

5. **Clause 5 (exit 2 when the launcher binary is missing):**
   - Docstring: SOURCED `dispatch_gate.py:10` `"2 = no launcher binary (claude missing: the gate does nothing, so it never strands the lock)."`
   - Code: SOURCED `scripts/sched/dispatch_gate.py:91-95`.
   - Test: SOURCED `MyTradingSys/tests/test_dispatch_gate.py:76-82` (`test_missing_launcher_does_not_tick`).
   - Verdict: MATCH.

6. **Clause 6 (one log line per run in ~/.claude/mts-dispatch-gate.log):**
   - Docstring: SOURCED `dispatch_gate.py:10` `"Log: ~/.claude/mts-dispatch-gate.log (one line per run)."`
   - Code: SOURCED `scripts/sched/dispatch_gate.py:37-47`, `scripts/sched/dispatch_gate.py:93`, `scripts/sched/dispatch_gate.py:104`, `scripts/sched/dispatch_gate.py:108`, `scripts/sched/dispatch_gate.py:120`, `scripts/sched/dispatch_gate.py:126`.
   - Test: SOURCED `MyTradingSys/tests/test_dispatch_gate.py:37-38`.
   - Verdict: MATCH.
