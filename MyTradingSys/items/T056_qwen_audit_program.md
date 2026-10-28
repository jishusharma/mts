# T056 - QWEN REGULAR AUDITING PROGRAM

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: T057 (simplify/declutter, feeds it the T0 clutter inventory), MyTradingSys/archive/worker_roadmap_2026-10-15/WORKER_ROADMAP.md (work routing
tiers), research/fast_track_2026-09-27/QWEN_AUDIT_PROGRAM.md (binding design doc).

## VERBATIM ASK (operator, 2026-09-28)
We also need a regular auditing tasks for Qwens. Like assignit for finsing gaps in MTS and any other
thing that it can do to save cost and give Claude a heads up to work with! It can also research as per
MTS protocols. So Claude can plan ahead and assign scheduled tasks for Qwen.

## STATE
WONTFIX 2026-10-08: Qwen NUC lane decommissioned 2026-10-01 (263b13f); premise gone. History below kept.

2026-09-28 filed (supervisor). Design already written by a prior session at
research/fast_track_2026-09-27/QWEN_AUDIT_PROGRAM.md: idle-only backfill (packs only when the NUC queue
has 0 waiting so audits never delay priority work), 7 fixed audit templates (A1 formula conformance, A2
test gap, A3 spec pre-check, A4 corpus question, A5 layer independence, A6 doc-vs-code drift, A7 safety
invariants), a fixed reply format (FINDING/QUOTE/WHY/FIX blocks or the single line NO FINDINGS), and a
T0-before-T1 rule: anything a script can find mechanically is never a Qwen task.

This session (2026-09-28) delivered the pieces the design doc called for:
- `scripts/worker/audit_targets.json` -- seed registry, 15 real targets across all 7 templates (3x A1,
  2x each A2-A7), real repo paths verified to exist. Two targets (A1-bt-stats-sharpe, A7-risk-guard)
  are pre-marked `last_audited` so `--backfill` does not immediately re-pick what this session already
  hand-audited (specs 097/098 below).
- `scripts/worker/audit_rotation.py` -- spec 094 (packed, queued): registry I/O, `--backfill` (packs the
  least-recently-audited targets, idle-only), `--t0` (delegates to a sibling module, see next).
- `scripts/worker/audit_t0_checks.py` -- spec 095 (packed, queued): the T057 clutter inventory as
  read-only script checks (stale `.pre_*` backups, leftover rejected/raw names under
  Dumps/workers/NUC-QUEUE, directories over 200 MB, markdown docs referenced nowhere else) -> writes
  `research/audits/T0_CHECKS.md`. Never moves, renames or deletes anything -- an operator reviews the
  list before archiving (T057's own rule).
- `scripts/worker/audit_digest.py` -- spec 096 (packed, queued): reads verified (`verdict != FAIL`)
  audit replies from `done/`, keeps a finding only if its QUOTE is found verbatim within 3 lines of the
  claimed `path:line`, dedupes by a stable `sha1(path|quote)[:10]` id, skips ids a human has closed in
  `research/audits/AUDIT_DIGEST_CLOSED.json` (read-only sidecar, written by a human/supervisor, never by
  this script), writes `research/audits/AUDIT_DIGEST.md` capped at 40 open-finding lines, newest first.
- Two hand-made audit tasks so audits start before the scripts exist (queued behind 092/093 like
  everything above): spec 097 (A1: do `bt_stats.py:sharpe` and `ref_pbo.py:sharpe` match FORMULAS.md
  section 10's population-stdev Sharpe?) and spec 098 (A7: safety-invariant read of
  `execution/risk_guard.py`'s account-notional cap). Neither has an EXPECT line -- a correct reply can
  be either FINDING blocks or the single line NO FINDINGS, and EXPECT can only require text present in
  every valid outcome, so it was left off both (queue_tool.py's own mechanical verify still runs; it
  will not fail a clean NO FINDINGS reply just for having no EXPECT).
- Tests written from the design docs (not from code, since none of the three modules exist promoted yet):
  `scripts/worker/test_audit_rotation.py`, `test_audit_t0_checks.py`, `test_audit_digest.py`. All three
  currently fail at import with `ModuleNotFoundError` (verified) -- expected until each `.new` reply is
  reviewed and promoted.

Design changes made this session, and why:
- `audit_rotation.py`'s `--t0` flag does NOT contain the T057 checks itself; it imports a sibling module
  `audit_t0_checks.py` (built independently by spec 095) and calls its one entry function. The original
  design implied one file with both flags fully built in one task; splitting into two independently
  CREATE-able files means both Qwen tasks can be packed today without one waiting on the other's `.new`
  output first (the alternative -- one task appending to the other's file, like 082/083 did for
  `formula_audit.py` -- needs the first file's real output on disk before the second spec can be
  written, which was not available in this session).
- The T0 clutter inventory implements 4 of T057's 6 listed checks (stale `.pre_*` backups, leftover
  rejected/raw names, big directories, orphan docs) within the ~2.5k-output-token budget; "duplicate
  docs" and "code outside its area" were left for a later append-only extension (same registry-style
  pattern as `CHECK_BUILDERS` in `formula_audit.py`) rather than risking a cutoff like 076/082 did.
- Audit-generated spec IDs use a reserved `900+` range (`900-audit-<slug>.md`) so `audit_rotation.py`'s
  auto-generated specs never collide with the human-assigned sequential IDs (currently in the low 100s).

Next: once 094/095/096 clear the queue, review each `.new` reply, run the pytest files above against
the promoted code, `queue_tool.py verify`, promote (back up `.pre_<tag>`, rename, re-gate), then let a
real `--backfill` + `--t0` cycle run and read `research/audits/AUDIT_DIGEST.md` at the next session start
(after STATUS.md, per QWEN_AUDIT_PROGRAM.md's "Claude side" section). Desktop Task Scheduler wiring for
the 3-hourly cron (zero Claude tokens) still needs operator approval per the design doc -- not done here.
