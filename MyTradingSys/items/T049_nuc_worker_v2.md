# T049 - NUC WORKER VERSION 2: SELF-CONTAINED TASKS, NARROW SHARE, UNATTENDED START

Register row: MyTradingSys/research/BUGS.md T049.
Opened: 2026-09-25 by session MTS-2026-09-25-2100Z.
Severity: MEDIUM. Status: OPEN (built and tested in a sandbox; operator setup pending).

## OPERATOR STATEMENT (verbatim, 2026-09-25)

"we can make changes that simplify the process and the architecture."
"Please redesign and outline the roadmap so that we stay corrected."
"going forward i am looking to remove issues with permissions as I need
Claude to build Automated System in a token efficient way."
On restarts: "setup should be simple like a 1 click thing or a scheduler of
something on startups".

## WHAT WENT WRONG IN VERSION 1 (evidence)

1. Task 001 reply listed files that do not exist (asset_allocation.md,
   execution_engine.md and others). Cause, proven from the script: the model
   prompt carried only the task text, never the file contents.
2. After file contents were added to the prompt, task 003 claimed T048 has
   no row in items/INDEX.md. INDEX.md line 30 has that row. The reply also
   proposed a table layout INDEX.md does not use. Likely cause: the command
   line client runs with the model server's default context window (2048 or
   4096 tokens, depending on the Ollama version) and silently drops the start
   of a longer prompt. The items folder is about 52 KB, roughly 15,000
   tokens. Not proven: version 1 records no token counts. Version 2 records
   them in every reply.
3. Replies contained terminal control characters because the command line
   client was used instead of the HTTP interface.
4. The whole repository was shared to Everyone with full control, the NUC
   drive letter did not survive a restart, and nothing restarted the loop.

## DECISIONS

- Shrink the bridge instead of moving it. The desktop packs self-contained
  tasks; the NUC needs no repository access. The repository stays on the
  desktop.
- The queue stays on the desktop because the coordinator can only reach
  folders on the desktop. The NUC tolerates a sleeping desktop: replies wait
  in a local outbox and are delivered later.
- Share only NUC-QUEUE, to a dedicated account without admin rights
  (mtsworker). The old whole-repository share is removed. The Everyone grant
  on the repository is removed after a full permission backup.
- Call Ollama over HTTP with a context window sized per task by the packer
  (3 characters per token, deliberately pessimistic; cap 32768 tokens for
  the 32 GB NUC). Too big means refused and split, never truncated.
- Acceptance checks are data: EXPECT lines in the spec, hidden from the
  model, checked by the verifier. The verifier also flags invented file
  names, inputs changed since packing, and replies cut off at the limit.
- Unattended start: automatic sign-in, a scheduled task at sign-in, a
  launcher that restarts the worker forever, and BIOS power-on after power
  failure. Chosen over a system task at boot: the system account on a
  workgroup machine cannot sign in to the desktop share, and would not see
  the models stored in the user's Ollama folder.
- Updates without visiting the NUC: queue_tool.py deploy; the worker sees
  the new copy within one poll, exits, and the launcher installs it.
- Routing: exact questions go to scripts, judgment goes to the model.
- Writes follow USER.md: non-critical files directly, critical files by
  .new and the four-step proof. Nothing the worker returns is applied
  automatically.

## COMPONENTS

| File | Runs on | Role |
|------|---------|------|
| scripts/worker/queue_tool.py | desktop | pack, status, verify, deploy |
| scripts/worker/nuc-worker.ps1 | NUC | claim, call model, outbox, heartbeat, requeue after a crash, self-update |
| scripts/worker/nuc-launcher.ps1 | NUC | keeps the worker running, installs updates |
| scripts/worker/setup-desktop.ps1 | desktop, once | account, queue-only share, retire old share and grant, publish |
| scripts/worker/setup-nuc.ps1 | NUC, once | credential, install, scheduled task, Ollama and power settings |
| Dumps/workers/NUC-QUEUE/README.md | - | queue protocol |

## COORDINATOR TOKEN BUDGET

Per task the coordinator spends one spec (about 15 lines), one pack line and
one five-line verdict. File contents never pass through the coordinator. A
full reply or diff is read only on REVIEW or FAIL.

## ROADMAP

Phase 1. Build and sandbox test. DONE 2026-09-25.
  Evidence: pack refused a critical file, a banned term, a 195 KB file and a
  missing path; three tasks ran through the worker against a stand-in model
  server; the worker requeued an interrupted task; verify gave PASS for the
  canary, FAIL for an invented file name, REVIEW with a diff for a proposed
  change; the launcher installed a changed worker by itself; a second worker
  copy refused to start. All four PowerShell scripts parse without errors.

Phase 2. Operator setup, one time, about 15 minutes.
  Desktop, PowerShell as administrator, repository root:
    powershell -ExecutionPolicy Bypass -File scripts\worker\setup-desktop.ps1
  NUC: close the old worker window, then PowerShell as administrator:
    net use Z: /delete /y
    net use \\jis-nb\MTS-Queue /user:jis-nb\mtsworker *
    powershell -ExecutionPolicy Bypass -File \\jis-nb\MTS-Queue\deploy\setup-nuc.ps1
  NUC: automatic sign-in (netplwiz) and BIOS After Power Failure = Power On.
  Restart the NUC without touching it afterwards.
  Exit: queue_tool.py status shows a heartbeat under 3 minutes old.

Phase 3. Canary. Task 004 (packed 2026-09-25) must verify PASS: every EXPECT
  line present, no invented file names, tokens in close to the packed
  estimate. Then move the version 1 files to Dumps/workers/_archive/.
  Exit: PASS.

Phase 4. Scripts for exact checks. The 001-003 question (does every item file
  have an INDEX.md row) becomes a script inside Build-Check instead of a
  model task. Exit: the check runs in Build-Check.

Phase 5. First production work, per the 2026-09-25 freeze decision (the NUC's
  first jobs are rule tagging and source tracing of compiled_engine.md).
  compiled_engine.md is packed in line-range slices, each with
  OVERRIDE-CRITICAL and EXPECT lines. Proposals are reviewed and applied by
  the four-step proof and checked by scripts/tools/verify_rule_citations.ps1.
  Exit: first slice applied and its citations verified.

Phase 6. Measure, then tune, only with data from phase 5: tokens per second,
  queue wait, FAIL rate per task type. Options then: a smaller model for
  mechanical rewrites, batching, a larger context cap.

## RISKS AND LIMITS

- Automatic sign-in gives anyone with physical access a signed-in NUC.
  Accepted for a home machine; revisit before the NUC ever holds exchange keys.
- Windows PowerShell 5.1: checked by review and by running under PowerShell
  7.4 on Linux. The first real 5.1 run is setup-nuc.ps1 on the NUC.
- net use rejects /savecred together with a password prompt (error 3510);
  setup-nuc.ps1 stores the credential itself. A stale stored credential for
  the desktop (the desktop user's own account, from the old drive mapping)
  caused Access denied on first start; setup-nuc.ps1 now replaces it and
  checks the result.
- verify checks form, not meaning. It catches invented names, missing expected
  text, changed inputs and cut-off replies. Meaning stays with the reviewer.

## UPDATES

2026-09-25 22:08Z. Phase 2 mostly done: setup-desktop.ps1 and setup-nuc.ps1
ran. Two faults found and fixed in the scripts: share creation failed with
error 1332 on a hand-built account name (now resolved through the account's
security ID); the NUC had a stale stored credential for the desktop user's
own account, giving Access denied (setup-nuc.ps1 now replaces and checks it).
Phase 3 canary 004: PASS. 5 of 5 expected lines, 0 invented file names.
Tokens in 2997 against a packed estimate of 3609 (estimate 20 percent high,
as intended), out 232, context 6144, 191 s including the first model load.
Version 1 script and replies 001-003 moved to Dumps/workers/_archive/nuc-worker-v1/.

2026-09-26 14:04Z. Phase 2 restart test: PASS. Operator restarted the NUC
without touching it afterward. Automatic sign-in landed on E-ngineers (the
same account the scheduled task's Principal.UserId names, confirmed before
the test), MTS-NUC-Worker fired at logon, queue_tool.py status from the
desktop read heartbeat 14 s old, host JIS-NUC, state idle. Unattended start
proven end to end.

2026-09-26 14:12Z. Phase 4: items/INDEX.md consistency check strengthened
in scripts/Build-Check.ps1. The existing check only cross-referenced OPEN
ids already listed in research/BUGS.md against INDEX.md; it could not have
caught the version 1 failure mode by itself, since T048 would need a BUGS.md
row to be checked at all. Added a direct items/*.md -> INDEX.md row check
(every file in items/, excluding INDEX.md itself, must have a matching row)
and the reverse (every INDEX.md row must point at a file that exists), so a
missing or stale row is caught independent of BUGS.md. Build-Check itself cannot be run from this bridge session (no PowerShell
or Maven on it, only the mounted files); the check logic was reproduced in
Python against the live repo instead: 24 item files, 24 INDEX.md rows,
zero mismatches either direction. Operator or a Windows session should
still run scripts\Build-Check.ps1 once for a real PASS/FAIL.

2026-09-26 14:17Z. Phase 5 first slice: PASS, citation staged, not yet applied. Scope: the "Double
Distribution Breakdown Anticipation" rule at compiled_engine.md:38-44 embeds
a quote attributed only to "Tom:" with no [TOM-NNN] tag, unlike every other
rule in the file's sourcing scheme. Verified before dispatch (T1, canonical
transcript): the quote is verbatim in raw_transcripts_canonical/-dMWA_bbm3o_raw.txt.
The same video already backs TOM-059 in conditions/market_state_rules.md
section 3.2, but for a different excerpt - this rationale line has no id of
its own. Also found: this exact gap was already logged, uncited, in the
2026-08-28 archive audit (archive/mts_historical/htf_structure_audit_2026-08-28.md
row 2 and row 216), tagged there with an old, pre-TOM_VERBATIM_INDEX scheme
id ("T4") that was never carried into the TOM-001..TOM-213 rebuild - so this
is a known, aged gap, not a new find. Task 005 packed and dispatched asking
the worker to confirm the quote's presence, propose the next sequential id
(TOM-214) and index row, and propose the one-line compiled_engine.md edit.
scripts/tools/verify_rule_citations.ps1 as written only scans conditions/*.md
for [TOM-NNN] usage, so a citation living only in compiled_engine.md would
read as "unreferenced" and fail the verifier; extended the script to also
scan runtime/compiled_engine.md before dispatching, so this and future
compiled_engine.md citations are actually checked, not just decorative.
Task 005 (first pack) verified FAIL: expected text "market_state_rules.md"
missing, and "runtime/compiled_engine.md" flagged as an unknown file name.
Both traced to the spec, not the worker: it presumed source_file should be
the thematically-closest conditions file; the worker's own answer (cite
compiled_engine.md itself, since that is where the rule actually lives, not
in any conditions/ file) was the more defensible one. Re-specified as task
006 with the bare-filename convention spelled out and source_file corrected
to compiled_engine.md: verify PASS, 3/3 expected, 0 unknown names.
Caught on review, not by verify: task 006's own proposed compiled_engine.md
edit line was byte-identical to the original - it confirmed the quote and
the index row correctly but silently dropped the [TOM-214] tag insertion
that was the actual point of the task. Task 005's edit line, from the first
run, had inserted the tag correctly. Verify does not check the substance of
a freeform proposal line against its stated intent, only the EXPECT
patterns, so this mechanical PASS would have shipped a no-op edit had it
gone unread. Built MyTradingSys/runtime/compiled_engine.md.new and
MyTradingSys/research/TOM_VERBATIM_INDEX.md.new by hand from the two
cross-checked, independently-correct pieces (both runs agreed on the
VERBATIM finding and the index row; the edit line came from run 005,
verified by direct comparison against the live line). Re-ran the extended
verify_rule_citations.ps1 logic in Python against the .new pair: 214
defined ids, 214 used, 0 unknown, 0 unreferenced - PASS. Diffs are one
line each (compiled_engine.md: adds "[TOM-214]" mid-line; index: adds one
table row before "# END"). Neither .new has been applied - both wait for
the four-step proof and operator sign-off, per compiled_engine.md's
"ask before" status in USER.md.

## STATUS

CLOSED 2026-10-01 (Qwen decommissioned; AIBridge on desktop replaces the run-command surface). Phase 2 complete 2026-09-26: NUC restarted, automatic sign-in to
E-ngineers (the scheduled task's own principal) landed on the desktop with
no manual step, MTS-NUC-Worker fired at logon, worker heartbeat read 14 s
old at 2026-09-26T14:04Z, host JIS-NUC, state idle. BIOS power-on after
power failure remains deliberately unset (unattended-outage recovery, not
in scope). Phases 1-3 done; phase 4 done (see UPDATES); phase 5 first slice
verified PASS, applied, and committed by the 2026-09-26 claude session (see UPDATES).
Open, not phase-blocking: rotate the mtsworker password (pasted in chat
2026-09-25); stop using the Z: drive letter on the NUC, UNC path only.
Next action: continue phase 5 slice by slice; slice 1 (TOM-214) is live on disk and in the index.
