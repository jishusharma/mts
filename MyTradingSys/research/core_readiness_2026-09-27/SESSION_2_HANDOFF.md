# CORE READINESS - SESSION 2 HANDOFF (Sonnet 5, 2026-09-27, continuing Opus 5.5's plan)
# Reads with CORE_READINESS_PLAN.md in the same folder. Does not replace it.

## WHAT THIS SESSION DID

Revalidated Opus 5.5's plan against the live repo (all numbers reproduce; the
plan is current, not stale), then executed Phase A guardrails and B1 (B071
fix) end to end. Nothing in the live tree was changed - critical files are
staged as .new per USER.md; non-critical additions (new harness script, new
pytest file, docs, this file) were written directly, also per USER.md.

## REVALIDATION (exact reproduction of plan section 5)

Ran core_invariants.py, verdict_golden.py, module_isolation.py (A+B),
proof_direction_cases.py, fail_closed_spec.py directly via python3 against
the live runtime_data corpus (9,175 -> 9,195-9,223 snapshots; corpus grew
during the session, as expected). All five reproduce the plan's claimed
numbers within the growth delta. fail_closed_spec.py: S2 1,930 vs plan's
1,917 (13 new snapshots since). Confirms the plan's findings are accurate.

## PHASE A - DONE

- A1: MyTradingSys/tests/test_proof_direction.py added (copied from
  harness/proof_direction_cases.py, per spec). Full suite: 131 passed
  (was 130; the plan's "125+1=126" assumed a stale baseline).
  UNIT_TEST_PLAN.md rewritten v5.0.0: correct per-file counts (79/38/8/5/1),
  mojibake fixed (was CP1252-mangled em-dashes), notes the L1 Java gap.
- A5: harness/snapshot_contract.py written (did not exist before). L0
  contract: required keys, enum sets (discovered empirically from the
  corpus, not guessed - the plan's guessed session_timing values were wrong
  twice before I queried the actual data), VAL<=POC<=VAH, 25pct price-range
  sanity, numeric types. PASS on full corpus (9,219 snapshots) and on
  --since 2026-09-16T12:26:18Z (the "session" block's introduction date,
  discovered this session - not previously documented anywhere I found).
- A2: scripts/tools/core_check.ps1 written, chains all 7 checks into one
  STATUS line. NOT verified under real pwsh - none available in this
  bridge sandbox (see BLOCKED below). Run it once on the desktop.
- A3: BLOCKED, see below. Files unchanged (reviewed, no defects found).
- A4: NOT ATTEMPTED (needs A3's replay working first, per plan's own
  sequencing; also needs live Binance network access this session doesn't
  have reason to assume works from the bridge sandbox - untested).

## PHASE B - B1 (B071 fix) - DONE, STAGED, NOT APPLIED

Three .new files, byte-for-byte matching the plan's reference patch:
  MyTradingSys/runtime/build_mo_cli.py.new
  MyTradingSys/backtest/verdict.py.new
  scripts/core/start-trading-day.ps1.new

Proof (on an isolated /tmp scratch copy, NOT the live tree - live tree is
untouched):
  fail_closed_spec.py -> S1 PASS ("error", not "aligned"), S2 PASS (0 of
  9,222 snapshots reach WATCH/SETUP_FORMING with pd="error", was 1,930)
  verdict_golden.py -> NO CHANGE vs baseline (9,160 rows, 60 new/uncompared)
Not proven: the live-cycle proof (rename build_mo_cli.py for one real
cycle, confirm log shows PD_ERROR and no SETUP_FORMING) - needs the actual
running loop, which only exists on the desktop.

Apply via your normal four-step proof: diff each .new against its live
file (the diff is small - one new block per file, everything else is
byte-identical), then replace.

## BLOCKED (environment limits of this bridge session, not the plan)

- A3 (Java L1 replay): no javac reachable. This Cowork bridge sandbox has
  no root/sudo (apt-get blocked), the network allowlist is pip/npm/GitHub
  only (Maven Central 403s through the proxy), and the one pip-installable
  "JDK" (jdk4py) ships a jlink runtime with `java.compiler` but not
  `jdk.compiler` - java runs, javac does not exist anywhere reachable.
  I did find and use your .m2 cache (jackson 2.16.0 jars are there and
  fine) once granted folder access, so compilation is the only piece
  missing. core_check.ps1 (A2) has the same limit for a different reason:
  no pwsh in this sandbox at all.
- Computer-use was considered as a fallback (drive a real PowerShell
  window on the desktop) - not viable either: Terminal/IDE apps are
  granted at "click" tier under computer-use's safety rules, which blocks
  typing. I could click a Run button but not type a command.
- Net effect: A3 and A2's real PASS/FAIL need to run once on the desktop
  itself (pwsh + your .m2 are both there). Exact commands are in
  CORE_READINESS_PLAN.md task A2/A3 and in core_check.ps1's own header.

## NOT STARTED (by design, needs your decision first)

Phase C (D1-D6 into code), Phase D (historical mode), Phase E (execution
layer fixes), Phase G (governance/cleanup). These touch critical files or
change live verdict behavior - see D1-D7 below. I did not implement any of
these without your sign-off, per the plan's own "OPERATOR DECISIONS
PENDING" framing and USER.md (critical files need .new + explicit approval,
not a default-adopt).

## D1-D7 - YOUR CALL (plan's recommendation in [], all still pending)

D1 R:R suspension - [recommend: revert, hard stop always applies].
    Effect: 158 SETUP_FORMING, 807 WATCH, 1195 WAIT_PROOF, 893 WAIT_TRIGGER
    all move to WAIT_RR. No Tom citation for the current suspend behavior.
D2 Zone-math authority - [recommend: Java is canonical, Python legacy]. No
    verdict effect (off live path).
D3 Extra/FVG candidates - [recommend: move to module_candidates, out of
    setup_candidates]. No actionable-verdict effect measured.
D4 Directional proof count - [recommend: adopt directional-only counting,
    drop speed]. Combined with D1: of 260 SETUP_FORMING, 158->WAIT_RR,
    79->WATCH, 23 remain.
D5 Unhealthy trend/transition (B063) - [recommend: document the gap in
    compiled_engine sec 1 until a Tom-cited definition exists; no code yet].
D6 Proof thresholds 3/5, SETUP_CONFIRMED - [recommend: document as
    [SYSTEM] in sec 8; SETUP_CONFIRMED is unreachable and must not be keyed
    on by any executor until defined].
D7 B071 floor - [recommend: accept as written - this is B1 above].

Nothing in Phase C should land until you rule on D1-D6 (D7 is done, staged).

## NUC BUILDER

Idle throughout this session (heartbeat fresh, no task queued). Its last
completed work (TOM-214 citation, tasks 005/006) is still staged as .new,
still awaiting your four-step proof - unrelated to this session's work,
just flagging it is not stale-forgotten.

## SUGGESTED NEXT SESSION

1. You run core_check.ps1 and run_replay.ps1 once on the desktop for real
   PASS/FAIL (5 min).
2. Rule on D1-D6 (or tell me to proceed with the plan's recommendations -
   they are all safety-tightening, no loosening).
3. Apply B1's three .new files via four-step proof.
4. Then Phase C lands with exact transition-matrix proof, one decision at
   a time, same pattern as B1 above.
# END
