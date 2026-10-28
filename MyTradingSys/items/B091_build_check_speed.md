# B091 - Build-Check cycle cost for fix-test loops

Status: CLOSED 2026-10-04. Severity: MED. Opened 2026-10-03.

## Defect

Every fix-test cycle costs the operator about 45 seconds of wall time
and dirties the working tree twice. During a multi-fix session this
compounds: dozens of waits, dozens of dirty-tree handling steps, and
the same two files rewritten on every run.

## Evidence

Timing, from the 2026-10-03T12:14:45Z run of scripts/Build-Check.ps1:
  Java compile:  PASS 3.2s
  Math tests:    PASS 219/219 38.5s
  Doc tests:     PASS 5/5 2.2s
  Wall: ~45s per invocation.

Tree side effects, from gitsnap output after the same run:
  warning: in the working copy of BUILD_REPORT.md, CRLF will be
  replaced by LF the next time Git touches it
  warning: in the working copy of session_log.json, CRLF will be
  replaced by LF the next time Git touches it
Both files are rewritten on every run.

Existing fast path: scripts/dev/run_all_tests.py --quick skips Maven
and backtest. Build-Check.ps1 has no equivalent fast tier.

## Fix (Claude decides)

(A) Build-Check --quick: compile + doc tests only. Math tests
    deferred to a full pass, which runs at release gate only.
(B) Build-Check --read-only: does not rewrite BUILD_REPORT.md or
    session_log.json, so the tree stays clean between runs.
(C) Skip-if-unchanged: hash the tracked set; if nothing changed
    since the last PASS, print the cached result and exit 0.
(D) Split into two scripts: fast pre-commit gate, full release
    gate, wired into cicd_run.py stage 2.2.

Chosen fix must include a test that fails on the pre-change
Build-Check.ps1 at least once.

## Receipt

B091 CLOSED 2026-10-04 (MTS-2026-10-04-0200Z-CLI-BLD-b091-buildcheck-speed): scripts/Build-Check.ps1 gains -Quick (math tests skipped, STATUS names QUICK) and -ReadOnly (BUILD_REPORT.md not rewritten; Build-Check never wrote session_log.json); cicd_run.py stage 2.3 build-check step now passes both. MyTradingSys/tests/test_b091_build_check_tiers.py: 3 FAIL on scripts/Build-Check.ps1.pre_b091, 3 PASS on new; quick tier 21s incl. compile vs ~45s full. Commit: the one tagged B091

# END
