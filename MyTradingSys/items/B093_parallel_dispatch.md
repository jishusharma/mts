# B093 - parallel dispatch instead of single-slot hold

Status: CLOSED 2026-10-04. Severity: HIGH. Opened 2026-10-03.

## Defect

pick_state.json holds one picked row for 24 hours. During the hold
no other row is offered, even rows that touch disjoint file sets.
On a machine that is not always on, this serializes work that could
run in parallel.

The hold also cannot distinguish "picked and being worked" from
"picked and ignored." TF1 was picked at 10:59:12Z but never run;
the operator launched the B088/B089 fix as a direct prompt instead.
The whole queue still blocked for 24 hours behind a prompt nobody
used.

The goal from the operator: work in parallel (||) in a cost-
effective way. Cost-effective means: no turns burned on collision
repair. So the mechanism must still guarantee one writer per file
set (B086). Parallelism across disjoint file sets, not within one
file set.

## Evidence (2026-10-03)

- pick_state.json: {"TF1": {"count": 1, "picked_utc":
  "2026-10-03T10:59:12Z"}}
- pick_log.jsonl: R4-T2, B070 x4, TF1. TF1 the only hold.
- Every tick report tail since 10:59Z: "HOLD TF1 ... next_task.*
  unchanged".
- B088 part 2 set the cooldown to 24h, sourced from
  SCHEDULER_PLAN_2026-10-02.md:147 (session stale after 24h).
- B084, B085, B091, B092 wait at wave 9 behind waves 1-8 AND the
  hold.

## Fix (Claude decides)

(A) Multi-slot queue. pick_state.json holds N picks (default 3),
    each with its own next_task_<slot>.txt. Operator launches any
    slot with mts go <slot>.
(B) Parallel by file-set. Parse each row file set from the item
    doc or the row Next cell. Allow concurrent picks only when
    file sets are disjoint. Refuse a second pick that overlaps a
    held pick file set.
(C) Two-track queue. Fast track (small single-file fixes) parallel
    to slow track (large multi-file work), each with its own
    pick_state and its own next_task file.
(D) Keep single-pick. Shorten hold to ~1h. Rely on operator to
    notice and re-run.
(E) Explicit reservation. mts go <id> reserves the row for a TTL
    (e.g. 1h). Any row not reserved within the TTL releases
    immediately. Unpicked rows never block.

Chosen fix must ship with tests that fail on the pre-change
pick_task.py at least once, and must not weaken B086.

## Receipt

Chosen: (B) parallel by file set. Why: the defect is a hold that blocks rows touching other files; B removes exactly
that and keeps B086 (one writer per file set) as the admission test, with no new operator step (A needs slot
selection, C needs a size classifier, D and E leave two writers possible or rely on the operator).
Rule: file set = file names in the row Next cell and item doc, minus register files (BUGS, BUILD_PIPELINE, INDEX,
STATUS, LESSONS, 03_FILE_INDEX, SUPERVISOR_LOG). Disjoint -> picked together, up to 3 (MTS_PICK_SLOTS). Empty set
fails closed. Held rows still release on land / cooldown (24h); a conflicting row is skipped, not waited on.
Files: queue/slots/<id>.txt|json per active row; next_task.* mirrors the first (go.py unchanged); retired slots
move to slots/released/. Tests 23-30 in test_pick_task.py; 8 fail on the pre-change script.
Gate: run_all_tests.py --quick PASS.

# END

## 2026-10-04T18:30Z - REOPENED: launcher side not delivered

Pick-side landed at 1c81d81 (shape B by file set, up to 3 active slots in
queue/slots/<id>.txt|json). test_pick_task.py tests 23-30 added; 8 fail on
pre-change pick_task.py; 30 pass post-change; run_all_tests --quick PASS.

T5 self-report: go.py reads only queue/next_task.json, which mirrors the
first active slot. Slots 2 and 3 exist on disk with no launcher. So the
fix delivers "queue offers multiple rows", not "multiple rows run".

Residual fix shape (for Claude):
  go.py --id <rid> reads queue/slots/<rid>.json, composes the session ID
  from its session name, launches. Default (no flag) reads next_task.json.
  mts.ps1 go verb passes --id through. Tests: test_go.py new case fails on
  pre-change go.py; --dry on the operator terminal stays live for a single
  slot launch.

Not folded into B094. B094 is "launch without the operator"; this is
"launch a specific slot", a prerequisite for it. Same file set (go.py,
mts.ps1), so ordering is: B093 launcher side, then B094.

## Fix landed (launcher side, 2026-10-05)

go.py --id <rid> reads runtime/queue/slots/<rid>.txt|json, uses the stored session_id, rewrites the prompt Session ID line, same dry gate. Exit 3 on missing slot, 2 on bad id. mts.ps1 go -Id forwards it. Tests test_go.py 10-13; 10, 11, 12 fail on pre-change go.py. Gate: test_go 13 passed, run_all_tests --quick PASS.
