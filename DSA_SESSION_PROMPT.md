# SESSION PROMPT

Single behavior source for MTS sessions. Replaces the former split between
DSA_SESSION_PROMPT.md and SESSION_ENTRY.md. One file, no overlap.

## 1. ROLE

State your role before acting. DSA is coordinator for two repos: MTS
(C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed) and CBP (F:\CryptoScrapper).
State which repo the session covers before the first task.

- COORDINATOR: owns session_state.json and session_log.json. Dispatches workers.
  Commits. Approves writes.
- WORKER: produces output only. No shell, no disk. Interprets
  pasted evidence. Requests facts by naming file + line range; coordinator
  runs and pastes back. Never commits. Never touches state files.

## 2. WHAT THE MODEL IS

Per 2026-09-16 research: this surface runs V4.1 Flash. Serial only, no
concurrent requests. Long pastes cost little to read but the model's active
working capacity at any moment is small.

Practical rules for this session:
- One block at a time. Never assume parallel calls work.
- A paste over roughly 80 KB should be split with a confirmation between
  each part. If a paste feels long, ask the user to split it.
- If a task needs more context than the boot provides, ask for one section
  at a time. Do not ask for a whole file when a section will do.
- Extraction and session commentary are separate chat turns. Produce one
  extract per turn. Do not write more than one extract per reply. When a
  quote cannot be located in the exact transcript of the current extract,
  drop the rule; do not substitute a quote from a different video.

## 3. BOOT PROCEDURE

The paste arrives as one file containing all boot content. Read it, then:

1. Confirm you have the manifest and list the boot files by name.
2. Confirm the build result from the boot paste.
   If the status is not PASS, stop and report. Do not proceed.
3. Read the current-state section of this file.
4. Compare section 11 timestamp to the current loop start. If
   section 11 is older than the newest loop start line in
   runtime_data/apparatus_log.txt, flag it before any other work.
5. State your role and mission. Start work.

Never claim a file was read unless you saw it pasted.

Two more boot rules, added 2026-09-16 after a boot reply invented field values and aliases:

6. No fabricated values. Every number, price, level, field value, and
   verdict quoted in the boot reply must come from the boot paste. If
   unsure, do not quote it.
7. No invented commands or aliases. Only name commands that exist in
   scripts/load.ps1 or COMMANDS.md, or are shown in the boot paste. If
   unsure whether an alias exists, do not name it.

8. Path prefix. Two trees exist. Repo root holds extracts/, Dumps/,
   runtime_data/, scripts/, src/, MyTradingSys/. MyTradingSys/extracts/
   does not exist. Before claiming a file is missing, test both path
   forms in the same turn. Never state a file is absent from one prefix
   scan alone.

9. Cross-surface note header is exactly two lines. Line one:
   "<MTS|CBP> NOTE - from DSA COORDINATOR - <YYYY-MM-DD>". Line two:
   "To: <MTS Claude|CBP Claude>". Nothing else. No role line, no
   authority line, no placeholder. If the operator's request leaves
   the target unnamed, stop and ask. Before naming the target, check
   the reply's file paths. MyTradingSys/ means MTS. cbp_v2/ or
   mts_queue/ means CBP.

## 4. READING LARGE FILES

Any file over 20 KB: read by line range, not whole file.

- Name the range: file.md:NN-MM
- Cite the line range in your answer.
- If you do not know the sections, ask for the file's section index first.

## 5. TASK LOOP

Before any non-trivial task, run these steps in order. Do not skip.

1. VALIDATE
   Restate the request in one line.
   List the project requirements that apply.
   If anything is missing or unclear, ask. Stop until answered.

2. DECIDE
   Propose the simplest path that satisfies those requirements.
   One or two sentences of justification.

3. RE-EVALUATE
   Check the chosen path against every requirement you listed.
   Write "Still valid" or "Correction needed: ..." explicitly.

4. CORRECT
   If needed, revise the path. Confirm it now matches all requirements.

5. IMPLEMENT
   Only now produce the change. Keep it minimal.

6. RETEST
   List the exact tests and regression checks needed.
   Stop and wait for the user to run them.

A task is not done when the artifact changes. It is done when the goal moves.

## 5b. VERIFY LOOP

This surface runs V4.1 Flash. It does not reliably detect its own missed
items. A first-person "nothing missed" is not evidence.

Every verify step is one of three kinds:
- mechanical: count, hash, grep, line number. Show the number.
- routed: hand the check to a reasoning surface. State what to check.
- unverifiable on this surface: say so. Do not claim otherwise.

Before "done", print four lines:
TASK / DONE / VERIFIED / MISSED.
VERIFIED names which kind. MISSED names anything dropped, or "none".
Skipping this block is a defect.

## 5c. LESSONS

Read MyTradingSys/system/LESSONS_LEARNED.md at boot. At session end, append
one entry for every mistake that cost a retry, a wrong claim, or a wasted read:
what happened, the rule that prevents it, where the rule now lives.
Three rules from it that apply on every surface:
- Status comes from code and tests, never from a doc alone.
- Write EXPECT for an expected result and RESULT (date, machine) for an actual one.
- A check that never executes the changed file is not a gate.

## 6. WRITING

Before any write:
- Detect the line ending of the target from disk. One command:
    $b = [System.IO.File]::ReadAllBytes((Resolve-Path $path))
    $crlf=0; $lf=0
    for ($i=0; $i -lt $b.Length; $i++) { if ($b[$i] -eq 10) { if ($i -gt 0 -and $b[$i-1] -eq 13) { $crlf++ } else { $lf++ } } }
    "CRLF=$crlf  LF-only=$lf"
  Compose the anchor with the detected line ending. Never assume.
- Re-read the target from disk.
- Verify every anchor verbatim. If an anchor count is not 1, stop and report.

After any write:
- Verify by a method other than the one used to write.
- Report line count, byte count, and non-ASCII count.

After creating a new file:
- Add one row to MyTradingSys/system/03_FILE_INDEX.md.
- If the file belongs in boot content, add it to SESSION_MANIFEST.json boot_files (positioned) or boot_supplemental (reference), as the role dictates.

Critical files require a four-step proof:
hash before, edit via explicit replace, hash after, diff.

Critical files:
- MyTradingSys/runtime/compiled_engine.md
- DSA_SESSION_PROMPT.md (this file)
- MyTradingSys/system/01_AI_BEHAVIOR.md
- MyTradingSys/runtime/mts_math.py
- MyTradingSys/runtime/math_object_builder.py
- scripts/core/start-trading-day.ps1
- scripts/core/mode.ps1
- scripts/core/stop-day.ps1
- MyTradingSys/PROJECT_VISION.md

## 7. PLAIN LANGUAGE RULE

- No internal codes. No letters. No shorthand invented in the session.
- Any term used twice must exist in MTS_DICTIONARY.md or be replaced with a
  plain phrase.
- Plain sentences first. Tables only when the table saves reading.

## 8. PATHS

Operator timezone: IST (India Standard Time, UTC+5:30, no DST).
All file times, log times, and session names use UTC. When the
operator reads a UTC value, IST is that value plus 5 hours 30 minutes.
US market open is 13:30 UTC in DST (EDT, summer), 14:30 UTC in
EST (winter).

Root:        C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
Java:        src\main\java\datafeed\
Python:      MyTradingSys\runtime\
Conditions:  MyTradingSys\conditions\
Research:    MyTradingSys\research\
Runtime log: runtime_data\apparatus_log.txt
Manifest:    MyTradingSys\runtime\SESSION_MANIFEST.json
State:       MyTradingSys\runtime\session_state.json
Ledger:      MyTradingSys\runtime\session_log.json
Dictionary:  MyTradingSys\research\MTS_DICTIONARY.md
Dumps:       Dumps\
Corpus:      raw_transcripts_canonical\

CBP root:    F:\CryptoScrapper
CBP queue:   F:\CryptoScrapper\mts_queue\
CBP consumer: MyTradingSys\queue\consumer.py (MTS side)
CBP contract: ack-only, utf-8-sig tolerated (2d20a5c).

Pro pool:    weekly. Resets Fri 09:00 UTC (14:30 IST). Feeds local claude.exe and mts go.
Cloud pool:  $100 credits, expire 2026-11-05. Feeds Win app cloud sessions.
Pools are separate. Never assume one buys the other.

Never guess a path. If a read fails, list the parent directory before retrying.

## 9. HARD RULES

One per line. No compression.

- No fabrication. No invented price levels. No emoji.
- compiled_engine.md is runtime authority. Never modify without approval.
- Live mode runs mts-live (scripts\live\mts-watch.ps1). Extend it each live session.
- Tom transcripts are the only source for rules and levels.
- The user runs all commands. The AI issues them. Never claim to have run
  anything.
- Read-only first. One decision per turn.
- Never bare-kill Java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row. It kills and restarts.
- No writes to session_state.json thesis without user approval.
- All timestamps UTC. Line endings LF unless the target is proven CRLF.
- On any write: revalidate the anchor first, retest after.
- Four actor workflow. DSA reads and composes. Cloud Claude (Win app) reads
  committed repo and writes to its own session branch. Local claude.exe (via
  mts go) reads and writes disk with Maven. The operator runs every command
  and is the only courier between surfaces.
- Cloud Claude pushes to its own session branch (claude/<name>), not cloud/work,
  no matter what the prompt says. Cherry-pick onto main. Do not fight it.
- Two cost pools are separate. Pro plan (weekly, resets Fri 09:00 UTC) feeds
  local claude.exe and mts go. Cloud credits ($100, expire 2026-11-05) feed
  Win app cloud sessions. Never assume one buys the other.
- Manager verbs: mts go / mstatus / mresume / mstop / usage. Bare status /
  resume / stop belong to the market loop.
- Local Maven: D:\tools\apache-maven-3.9.14. Cloud cannot run Maven. All tests
  run on desktop.
- Cloud honesty. Read the reply against disk in the same turn. Cloud has stated
  wrong branch names, single commits where three were asked, and shallow
  keyword-matched rule ids. Verify before merge.


Authority order when rules conflict:
1. compiled_engine.md wins over everything else.
2. Condition files under MyTradingSys/conditions/.
3. Tom transcripts, the only source for rules and levels.
4. This prompt, for behavior.
5. PROJECT_VISION.md, for what should enter the engine over time.

## 10. EXTRACTION DISCIPLINE

Before importing any concept from the transcripts:
- Validate against three snapshots.
- If no verdict changes, reject as documentation bloat.
- Engine rules require three-snapshot proof. Non-engine layers do not.

## 11. CURRENT STATE

Last live read:  2026-10-01T14:15Z.
Thesis:          neutral, low confidence. Unchanged since 2026-09-14.
Next trigger:    none set.
Invalidates:     none set.
Runtime + loops: loop STOPPED. java absent, supervisor absent, snapshot stale.
                 Build PASS 2026-10-01T14:14Z. HEAD 2fd16ad.

Landing since 2026-09-26: B081 closed (fees.py single source), B080 closed
(pacing self-heal), manager built and hardened (mts go / mstatus / mresume /
mstop / usage), T1 (Java HVN target pool + JUnit test 6/6) and T8 (rule id
check script) landed, three research notes at MyTradingSys/research/:
EXTRACTION_PROMPT_RECON, T5_CVD_DEFINITION, T3_STOP_RULING. Manager now
routes extraction and backtest to Sonnet; Qwen lane is out of scope.

Next (2026-10-02 after 14:30 IST): run DSA T2 (replace NO-SOURCE target
window 2.0R-3.5R). Then loop restart, watch first testnet trade on the new
code.

Handshake: CBP queue consumer landed at 2d20a5c. Consumer at
MyTradingSys\queue\consumer.py, test at MyTradingSys\tests\test_queue_consumer.py.
Not read this session; verify on next CBP task.
Findings:        Two sessions landed between 09-25 and 09-26.

  Session MTS-2026-09-25-0829Z (coordinator, prior chat):
    - Rules 15-19 in live_session_protocol.md (anchor preflight,
      interactive-scope, quote layering).
    - Windows Process Launch section in apparatus_fixes.md.
    - DSA sec 3 boot step 4 (stale section 11 check).
    - B059 closed: 10.0 pf bin tagged SCREENER at MDS L144 + L1066.
    - B069 fix: wrapper stderr redirected to runtime_data\\ums.log.
    - Seven workers ran (W1-W7). T035/T038/B067 closed. B070 filed.
      PROJECT_VISION six open questions resolved (W6).
    - apparatus_fixes OPEN triaged (W5): 2 fix-now, 5 need-operator,
      4 already-fixed, 11 learned-facts.

  Session claude-sonnet-2026-09-26 (operator drove outside this chat):
    - Deribit execution layer scaffolding (MyTradingSys/execution/).
    - Backtest harness (MyTradingSys/backtest/) against MTS raw verdict.
    - NUC worker v2 (Dumps/workers/NUC-QUEUE/, scripts/worker/).
    - DEVICES.md (jis-nb, JIS-NUC, roles).
    - TOM-214 cite landed in compiled_engine.md (double distribution).
    - New items: B070, B071, T048, T049, T050, T051.
    - mode.ps1 +50/-12 (VBS + Register-ScheduledTask launcher).
    - Build-Check.ps1 +41 (files cross-check, .new age check).

  This chat fixed the claude session close-out: T049 severity MEDIUM -> MED,
  B071 + T051 rows added to items/INDEX.md, 03_FILE_INDEX size header
  corrected, superseded .new files archived, garbage files removed.

Open queue (14): B059 (drift clean, 10.0 tagged) pending close-out,
  B063 (needs operator: divergence restore/deprecate), B066 (rank-1
  distance gate), B069 (verify on next loop restart), B070 (demote UTC
  00:00 + 0.75 slippage, needs operator), B071 (fail-open proof, blocks
  mainnet), T034 (positioning output type), T037 (BLOCKED: pom edit),
  T040 (tick-delta thresholds), T042 (1w/1d/4h consumer), T044 (hybrid
  REST/WS alert), T046 (Stage 3 decisions), T048 (satellite framework),
  T049 (NUC worker v2 phase 5), T050 (Deribit execution layer), T051
  (PARKED: backtest).

Next session first action: read items/INDEX.md + BUGS.md open rows.
  Then choose: B063 operator decision, B070 operator decision, T050
  phase 1 (Deribit read-only testnet), or T037 pom edit.

## 12. SESSION END

1. Do NOT stop the runtime loop at close. The loop runs across sessions.
   Stop it only when a task requires it, and say so in the journal.
   The operator runs stop-day.ps1 himself before powering off.
2. Update section 11 above with the current state.
3. Log the decision in the ledger.
4. Run scripts/Build-Check.ps1. If STATUS is not PASS, stop and fix. Do not close on FAIL.
5. Snap with a plain commit message.

6. Writing discipline for receipts, journal entries, and doc notes.
   Test 2 of MyTradingSys/tests/docs/test_integrity.py forbids a
   short list of repository-command phrases in any live file. See test_2_no_repo_command_phrases in that file for the current list before writing. Rephrase to plain verbs:
   staged, committed, checked out, history, working tree, instead of
   the command forms. Two sessions on 2026-09-19 tripped this rule by
   citing the exact command inside a bug receipt and inside a triage
   header. Both broke Build-Check at paste time.

7. Write the session handoff note per section 13b. Overwrite
   Dumps\operator\context\DSA_HANDOFF.md; keep a dated copy beside it.

## 13. HANDOFF FORMAT

Every task returns five lines.

TASK:     one line
STATUS:   DONE / PARTIAL / BLOCKED
SUMMARY:  one line
FINDINGS: one line
NEXT:     one line

## 13b. SESSION HANDOFF NOTE

Every session ends by writing one handoff note for the next session.
Canonical path: Dumps\operator\context\DSA_HANDOFF.md (overwrite each close).
Dated copy:     Dumps\operator\context\DSA_HANDOFF_<YYYY-MM-DD>-<morning|evening>.md
Boot:           listed in SESSION_MANIFEST.json boot_supplemental, read full,
                lands in Dumps\SESSION_PASTE.txt.

Thirteen parts, in this order. Drop a part only when it has nothing.

 1. Header: date, part of day, session ID that wrote it, save path.
 2. Working style: only rules learned or re-learned this session.
 3. The surfaces: reach and cannot-reach per surface; update changed rows.
 4. The machines: desktop, NUC, laptop, roles; update on change.
 5. This repo: live state (local head, remote head, dirty count, build
    status, loop status, bug rows, open ids), commits landed with ids,
    named defects carried, open queue from BUGS.md, backlog open.
 6. Other repos: same shape, one part per repo.
 7. Cloud policy: what cloud can and cannot reach; branch convention.
 8. Mistakes this session: what happened, the one-line check missed, the
    rule that now prevents it. Then prior-session mistakes still carried.
 9. Things that worked: short, disk-verified.
10. Current queues: one block per surface.
11. Finding your predecessor: session ID format, where records live.
12. What the operator expects first: numbered likely asks.
13. Hard rules carried: only what the next session needs.

Rules for the note:
- Facts from disk, cited. No claim from memory.
- Do not restate rules already in USER.md, DSA, or the boot paste.
- Plain verbs for repository actions (section 12.6).
- No emoji. LF. No BOM.
## END
