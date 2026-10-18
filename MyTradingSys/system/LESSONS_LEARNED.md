# LESSONS LEARNED (living log - append, never rewrite history)

Purpose: every session gets cheaper, faster and more accurate than the last. Each entry states
what went wrong, the rule that prevents it, and where that rule now lives. Add new entries at the
top of the relevant section. Keep each entry to 3 lines.

## A. Verification (accuracy)
- 2026-10-09: a question phrased as "what exists on the internet" was answered as a chat question and nine claims were presented with no URL, no DOI, no verified date and no tier; the playbook PART I gate was skipped.
  RULE: any reply that would cite an external source, name a web study, or state what exists on the internet runs playbook PART I STEP 1 before searching, regardless of phrasing.
  Where: MyTradingSys/methodology/playbook.md PART I; DSA_SESSION_PROMPT.md section 5 step 0.
- 2026-09-28: rsi TEST_PLAN C1 expected values were copied from Qwen's bt_rsi.py.new (off vs textbook
  Wilder, 70.0 vs 77.78), so tests would have blessed the bug. RULE: expected numbers come from the
  definition in backtest/layers/FORMULAS.md, computed independently; never from repo code. (CLAUDE.md gates)
- 2026-09-28 D1: a patch appended a comment in the middle of a dict line, which commented out 3 keys.
  The unit gate was green because nothing executed that file. RULE: the gate must EXECUTE every file
  a change touches; if no test does, add a static/AST check first (testnet/test_suite_static.py).
- 2026-09-28: expected results ("-> 6/6 PASS") were read by a later session as actual results.
  RULE: label expectations `EXPECT:` and results `RESULT (date, machine):`; never mix them.
- 2026-09-28: a doc audit (DEV_VELOCITY_AUDIT) reported findings as OPEN that the code had fixed.
  RULE: status comes from code/tests, never from a doc alone; spot-check one claim before acting.
- 2026-09-28: new tests must FAIL on the old code. Run them against the `.pre_*` backup once;
  a test that passes on both versions is a regression guard, not proof of the fix.

## B. Workers (cost + accuracy)
- 2026-09-28 FIX4: a worker put the mid-run HALT check BEFORE the protective stop, so a HALT after a fill
  skipped the stop and relied on the flatten alone. RULE: a halt/guard may block risk-ADDING orders, never
  the protective reduce-only stop; check the halt right after the stop is live. Safety diffs always get T4 review.
- Qwen (NUC) writes correct implementations but WRONG tests (019, 020, 021: 8 bad expectations).
  RULE: Qwen writes implementations/extractions only; tests are written by Haiku/Sonnet from the spec.
- Fixing a failing test "to match the implementation" can make it tautological (021 ladder:
  deadline test now expects all fills). RULE: expected values are hand-derived from the spec, and
  the test must still exercise the behaviour its name promises.
- Every worker report had at least one wrong claim: mvn "not found" (it is `mvn.cmd`), "needs Whisper"
  (it was HTTP 429), a video ID with its leading '-' stripped, a "compile gate" rewrite that
  regressed (it wrote __pycache__ into repo dirs). RULE: spot-check one concrete claim per report;
  never merge a worker's change without reading its diff.
- A worker concluded "monthly RSI must wait for next month's data" when downloading OLDER history
  fixes it (the archive goes back to 2020). RULE: when a worker says "wait" or "blocked", ask whether a
  cheaper route exists before accepting it; history comes from data.binance.vision (fetch_binance_archive --interval).
- Qwen 028 returned the file UNCHANGED yet passed both EXPECT lines (the phrases already existed).
  RULE: EXPECT lines must name text that is NEW in the change; always read verify's `+N -M` count.
- Qwen reviews confirm; they do not attack (022 restated the diff). RULE: adversarial review stays
  at Sonnet/Opus plus repro scripts.
- Packing snapshots the scoped files. RULE: never pack a Qwen task on a file that another in-flight
  task will change; sequence them.
- Queue banned terms were a substring match ("DIGIT" tripped "git"); fixed to word-start match.
  "commit" is still banned in task text; say "changeset".
- OUTPUT_TOKENS must cover the whole expected reply: a full-file rewrite needs about bytes/4 plus
  headroom. 031 (3500 for a ~4k-token runbook) and the 054 split (2500 each) were packed too small
  and would truncate. RULE: when splitting a truncated task, never lower OUTPUT_TOKENS; check it vs file size.

## C. Tokens + time
- Waiting: one background shell (`until [ -f reply ]; sleep`) per batch, never an agent that polls.
- Hand workers paths and line ranges, ask for tables of 25 lines or fewer, review diffs, not files.
- Batch all Qwen specs at once; the NUC is free but sequential (~4 tok/s, 5-25 min per task).
- Delegate broad reads to a Haiku Explore agent; the coordinator reads only what it will edit.

## D. Windows / tooling
- Python `open(p, 'w')` writes CRLF on Windows; always pass `newline='\n'` (a 142 KB diff was refused).
- Multi-line patches: write the patch as a .py file and run it; heredoc quoting in Git Bash breaks.
- unittest: never name an attribute `self.fail` (it shadows TestCase.fail).
- `Dumps/workers/` is gitignored (queue specs are not versioned).
- A stale `.git/index.lock` (0 bytes, hours old, no git process running) is safe to remove.
- YouTube (2026-09-28): after ~10 caption requests this IP got HTTP 429, and later a sign-in bot check.
  RULE: fetch at most ~5 videos per session with long gaps; on a bot check STOP (no cookie/IP workarounds)
  and ask the operator for pasted transcripts or a run from their own network.
- YouTube captions: `scripts/dev/fetch_captions.py` (captions only, 429 backoff); on HTTP 429, wait, don't transcribe.

## E. Domain framing
- 2026-10-09 volume study: a pattern chosen after looking at DEV (volume-confirmed breakouts beat unconfirmed in 6/6 daily and 5/6 4h pairs; pooled p = 0.008) fell to -13 bp, p = 0.60 on VALIDATION. RULE: a hypothesis
  suggested by DEV results is tested once on VALIDATION as a single pooled trial, never promoted on its DEV p-value. (volume_2026-10-09 V4)
- 2026-10-09: plain relative volume (this bar / mean of the last N bars) is a clock for BTC: 36% of 12-16 UTC 4h bars vs 6% of 04-08 UTC bars qualify as 2x spikes; weekends run at 0.62-0.72x. RULE: any volume flag uses a
  same-slot (hour or weekday) baseline; P06 (T073) still uses a 4-hour baseline. (volume_2026-10-09 V0)
- 2026-10-09: a first placebo draw sampled lags with replacement from 9 values, so 4 of 20 runs were near-duplicates. RULE: placebo/permutation shifts are drawn without replacement and the lags are printed in the result.
- 2026-09-30: Tom's stop floor 0.1%/0.2% fallback, 2-3.5R target window, 25% friction haircut and the TWOPEAK label were
  engineering choices with no Tom source; they cut his real trades (tight stops, 8R winners). RULE: parameters come only from
  the trader's own words (CLAUDE.md Provenance); unsourced ones are flagged NO-SOURCE, never tuned. (Replaced 2026-10-13 by the CLAUDE.md Numbers rule: SOURCED or OURS labels.)
- Non-Tom systems (MalkanView RSI, CryptoCred, FlowHorse, probability, session frame) are separate
  layers per PROJECT_VISION, extracted and backtested on their own, never as filters on Tom.
  RULE: read PROJECT_VISION "INTEGRATIONS TRACKED" before framing any indicator work.
- If an instruction references advice that cannot be found in the repo or memory, ask in the first
  reply; don't carry an unresolved reference through the session.

## F. Live system + supervision (maintainer run 2026-09-29; mistake -> root cause -> RULE)
- Sonnet builder edited live journal.py/executor.py in place -> next auto-trade would have crashed; AUTO_PAUSE
  needed. Cause: brief said "fix X" without naming the live-file rule. RULE: every builder brief touching
  MyTradingSys/execution/ says "stage <file>.new only; never edit a file a running process imports".
- Testnet daily-loss used equity delta -> subaccount transfer = -3.35M "loss" -> false HALT + kill-switch
  flatten of a healthy trade (fixed 1542151). Cause: P/L proxy not tested against non-trade balance moves.
  RULE: any P/L/risk metric gets a test with deposits/transfers/funding; use trade-type transaction logs.
- Live alert runner re-emitted a 99-bar backlog after state reset -> 43 stale rejections, 0 trades for hours
  (fixed 6ad9fd0). Cause: "last seen" state doubled as "start from". RULE: on missing/reset state a live
  emitter starts at NOW (fresh closed bar only); backfill is an explicit, separate command.
- Supervisor kept asking the operator for a task already done (NUC gate). RULE: check the observable
  result before re-asking (memory: operator-tasks-verify-yourself).
- Gate verified with `cut -c1-120` -> truncated output -> wrong conclusion; "53 findings ignored" claimed
  without reading the format (49 were "NO FINDINGS"). RULE: never truncate output you draw a conclusion
  from; count by parsing the real format (grep -c on the verdict token), then state the number.
- Windows OpenSSH kills children on disconnect -> background model pull died; an MTS-Ollama task was
  assumed but did not exist then (it does now, 2026-09-29). RULE: long NUC work goes through `ps-bg`;
  confirm a scheduled task with Get-ScheduledTask before relying on it.
- Qwen wrote `<file>.new.new`; verifier BLOCKED; Qwen pid_alive check was fail-open (fixed in review).
  RULE: liveness/safety checks fail CLOSED; specs name the exact output path; verifier rejects double suffix.
- Bake-offs: gpt-oss and qwen3.6 THINK=false returned empty / reasoning-only replies. RULE: qwen3.6 only
  with THINK=true; treat an empty `response` as a failed run, never as "no findings".
- Haiku summary dropped a requested item; kill-switch cancel-before-close was missed by every review
  until an Opus audit. RULE: summaries are checked against the request checklist item by item; safety
  paths (kill switch, stop handling, loss guard) get an ordering/failure-mode review, not a diff skim.
- Recurring pattern (commit history: 86 commits say fix/revert; 14 say false halt/stale/fail-open/closed):
  most incidents were state or accounting assumptions in live code, not strategy. RULE: before editing a
  live path ask "what happens on restart, reset, transfer, partial fill, API error?" and test one of them.
- `--hours` in new_plan is an entry window, not a time exit: one wide bracket held the single slot 7 h and
  6 signals were skipped_busy. RULE: read what a parameter does in code before reasoning from its name.

## G. Live system + supervision (maintainer run 2026-09-30)
- Watchdog CLI read the old heartbeat dir -> false orphan HALT on the first jishu_2 trade (fixed a9629e8).
  RULE: a change that adds a state location (per-account heartbeats) greps every reader of the old path in
  the same change and tests the real on-disk layout.
- Position manager died on a transient auth URLError; auto_trader read "manager exited" as "trade closed" and
  freed the slot while short 10 was open (fixed 863bae6 retry + rc 3 + settle only when exchange-flat;
  9d28118 adopt on restart). RULE: process exit is not position state - the exchange decides flat; network
  reads retry, then fail closed (slot stays busy + OPERATOR_ALERTS line).
- Checklist ticked by a stale line number (3a4d4d2). RULE: edit by matching text, never by a line number
  from an earlier read.
- Two supervisor sessions edited execution/ at the same time. RULE: one owner per area at a time, claimed in
  SUPERVISOR_LOG/INBOX before editing; the other session proposes only.
- Builder died (API 401) after editing auto_trader.py in place and left AUTO_PAUSE on 00:01-01:50 IST ->
  3 signals skipped (tom#70, fabio 1h, malkan 1h). RULE: builders stage .new too; whoever sets AUTO_PAUSE
  writes owner + expected end, and each wake clears or escalates a pause past its end.
- execution/journal/ vanished (cause unknown) and exit reasons were lost. RULE: anything outcome review
  needs is appended to the ledger at close; wakes check the journal dir holds the open plans' files.
- NUC hit 98 C under continuous Qwen load; an hourly check ran a backfill after the thermal pause was
  written into the skill text. RULE: pauses and temperature limits are enforced in the worker code (read
  before each task), not only in instructions.
- Adding the 5m timeframe crashed alert_rate_check (TF map lacked 5m; fixed 2026-09-30). RULE: adding a
  timeframe or family greps every TF/family map (rate check, account routing, audits) in the same change.
- turn_of_candle got a side and went live 3.5 h after C3 found no edge; 8/8 trades lost about the round-trip
  fee (1m, 8-min time exit, 10 USD). RULE: mark collection-only families as such in config + log, keep them
  out of edge claims, and pick a hold where fees do not decide the result.
- Maintainer brief carried stale routing (fabio -> jishu_1; config now has turn_of_candle there). RULE: read
  routing from auto_trader_config.json, never from a brief.

## 2026-10-01 session MTS-2026-09-30-1733Z - lessons

- Cross-branch diff: use three dots (main...cloud/work), not two. Two-dot compares tips and shows main's newer commits as if the other branch removed them. Caught by cloud, not by this session.
- "Not on disk" claims must check all branches and refs, not just local main. Auto-mode rule was on cloud/work at 125a64d while my note said "not on disk anywhere".
- PowerShell $pid is a read-only reserved variable. Never use it as a loop variable. Use $procId.
- Relayed operator directives through another AI note are not trusted by the cloud guard. Only direct operator typing in the cloud chat or a committed file lands.
- For any write with an anchor: read the exact target line from disk in the same turn. My two-dot diff error earlier came from composing an anchor from memory.
## 2026-10-01 - Cloud session wasted $11, wrote nothing

What happened: MTS-2026-10-01-~1630Z-CLD-ANA-chart-read ran a two-pass
Tom/Fabio chart read on two images. The prompt said "No writes". The
session complied and its full analysis stayed in the chat. $11 of cloud
credits spent. Nothing on disk. The next session cannot see any of it.

Rule that prevents it: every cloud session that produces analysis gets
a DELIVERABLE section naming the exact file path, and a closing clause
"commit to your branch". Read-only means no writes to main, no Maven,
no Dumps/. It does NOT mean no file output. A cloud branch is the
session's own workspace and its output belongs on it.

Where the rule lives: this file plus DSA_SESSION_PROMPT.md section 9
(pending edit).

Cost of the mistake: $11.

## 2026-10-02 - Prompts delivered without conformance check

What happened: DSA handed the operator a cloud prompt for the two-cores
work. On review the prompt named live_runner_cli.py at a path that does
not exist (real path MyTradingSys/backtest/layers/alerts/live_runner_cli.py),
spawned Sonnet subagents at an assumed 85 percent tier (SURFACE_POLICY
section 3 forbids Sonnet builders at 85 percent or above), omitted the
CLAUDE.md 'new tests must fail on pre-change code' gate, omitted the
ownership claim for execution/ and layers/alerts/ staging, omitted the
03_FILE_INDEX row requirement, and named the verify block without
naming its four lines.

Rule that prevents it: before delivering any prompt for a Claude cloud
or code session, DSA prints the conformance table in
MyTradingSys/system/PROMPT_CONFORMANCE_CHECKLIST.md with evidence per
row, and does not deliver until every row is PASS.

Where the rule lives: MyTradingSys/system/PROMPT_CONFORMANCE_CHECKLIST.md
plus DSA_SESSION_PROMPT.md section 12 (pending operator approval).

Cost of the mistake: one rewrite of the prompt (one DSA turn).

## 2026-10-02 - Budget gate refused work it should have done

What happened: the two-cores CC prompt carried a budget gate that told
the session to skip the fix pass and stop at 85 percent usage. The
session complied, delivered the tables and scaffold, and stalled
waiting for operator input. The refusal was written by DSA, not chosen
by the cloud session.

Operator correction 2026-10-02: never refuse a task for budget. Work to
completion. If usage is at 95 percent or above, commit and push
immediately, then continue with a commit after each step. At 1 percent
remaining, still work.

Where the rule lives: SURFACE_POLICY.md section 3, CLAUDE_MANAGER_SPEC.md,
CLOUD_PROMPT_TWO_CORES_2026-10-01.md, CLOUD_PROMPT_W3_KAPPA_2026-10-02.md,
PROMPT_CONFORMANCE_CHECKLIST.md row 3.

## 2026-10-02 - Ultracode burned  and lost two waves

What happened: the two-cores integration prompt said 'One Sonnet
subagent' inside each of four waves. The operator launched in Ultracode
mode. Ultracode spawned all four subagents in parallel. 85 percent of
the session cost went to subagents. Session cost .97 out of a 
cloud pool, in 9 minutes of active work. Waves 3 and 4 landed on the
branch; Waves 1 and 2 (readiness top-5 fix pass, Fabio v3 core compile)
died uncommitted when the container was reclaimed.

Rule that prevents it: every launch prompt names the mode explicitly
(Ultracode on or off), the total subagent cap, the batch size, and the
rule 'commit and push between batches'. Default is Ultracode off.
Full table: MyTradingSys/research/CLAUDE_MANAGER_SPEC.md section
MODE SELECTION.

Cost of the mistake: .97 plus the two lost waves.

## 2026-10-02 - DSA prompt-construction mistakes (one list)

This session wrote ~12 Claude prompts in 6 hours. Recurring defects,
all operator-corrected.

Prompt construction:
- Cited paths that do not exist (MyTradingSys/layers/live_runner_cli.py;
  MyTradingSys/runtime/alert_rate_check.py). Wrong line number
  (auto_trader.py:47 vs real :48).
- Wrote a PowerShell here-string containing a backslash-escaped quote,
  which broke parsing and produced a 1-byte file. Rewrite needed the
  temp-Python pattern with a triple-quoted string.
- Put a cloud-readable prompt under Dumps/operator/, which is
  gitignored and invisible to CC.
- Wrote budget-refusal clauses. Operator corrected: never refuse work
  for budget.
- Named 'One Sonnet subagent' per wave but did not also say 'Ultracode
  off', 'cap 3 total', 'batch 1'. Ultracode spawned 4 parallel
  subagents; $17.97 in minutes.
- Asked for one commit at the end of multi-wave work. Container
  reclaim lost 75 lines on 2026-10-01 (1800Z chart-read).

Git operations:
- Cherry-picked commits already on main because `git cherry main
  <branch>` was skipped.
- Used three-dot diff to answer 'is this branch merged'. Correct tool
  is `git cherry`.
- Ran a stage-all inside a rename commit and silently deleted 7
  tracked .new files. Plain working-tree check first, always.

Evidence discipline:
- Twice claimed a prompt file was on disk when the composing block had
  never been executed. The write must be read back in the same turn.
- Ran a recursive file search that hit backup_session/ before src/ for
  two Java files, then cited line numbers from the backup copies.

Process:
- Wrote prompt files into MyTradingSys/research/ that the operator
  wanted in chat. Waste of tokens and commits.
- Wrote the same lesson twice because the first append failed on a
  PowerShell -replace arity error and the write was not verified.

Rules that now apply:
1. Every prompt: Test-Path every cited path, grep every cited line,
   print the prompt in chat, do not write it to disk unless asked.
2. Never use PowerShell here-strings for prompt content. Use the
   temp-Python pattern with a triple-quoted string.
3. Cloud-readable files go under MyTradingSys/research/ or
   MyTradingSys/system/. Never Dumps/.
4. Every CC prompt names: Ultracode on/off, cap N total, batch M,
   'commit and push between batches'.
5. Never include a budget-refusal clause. Save-work clause only.
6. Cherry-report the branch before a cherry-pick. Plain working-tree
   check before any stage-all.
7. Never claim a file was written unless a head/tail read-back is in
   the same turn's paste.
8. Recursive file searches: scope to src/ explicitly to avoid
   backup_session/ shadowing.

Cost of these mistakes: ~$18 cloud burn (Ultracode); 2 lost waves
(Waves 1+2 of the two-cores session); several DSA turns rewriting
prompts; one 1-byte file; one unintended deletion of 7 tracked files.


## 2026-10-03 - surface choice was CLI-by-default, not task-first

What happened: DSA composed a Tom-and-Fabio fix prompt with surface
'Claude local CLI on the desktop' as the default. Operator correction
same day: CLI is fallback, not default. The order is App first
(Code / Cowork / Chat / Cloud), CLI only when the App cannot reach
local Maven, local testnet, the live loop, PowerShell-only files,
repo-importing scripts, or a gitignored path.

Rule: choose the surface by what the task needs, not by what the
policy lists first. App if it can read, write, run tests, and commit.
Otherwise CLI, and state the fallback reason in the session record.

Where the rule lives: MyTradingSys/system/SURFACE_POLICY.md section 1b.
# END

## 2026-10-02 - prompt delivery failures

Four defects in one day, all on the DSA chat surface, all from
composing CC/CL/Opus prompts from earlier pastes instead of disk reads.

1. Claimed 13 Fabio v3 files. Disk had 14.
   Rule: no prompt claim without a same-turn read. Now in USER.md and
   PROMPT_CONFORMANCE_CHECKLIST.md STEP -1.

2. Invented a 500K/100K session token cap.
   Rule: any numeric cap is OPERATOR-SET or omitted. Now in
   PROMPT_CONFORMANCE_CHECKLIST.md STEP -1 tags.

3. Invented four "do not read" restrictions on the Opus session.
   Rule: every restriction needs the operator's own words. Now in
   USER.md and PROMPT_CONFORMANCE_CHECKLIST.md STEP 0.

4. Delivered a prompt labelled verified, composed from prior pastes.
   Rule: verification means same-turn disk read with a pasted receipt.
   Now in PROMPT_CONFORMANCE_CHECKLIST.md STEP -1 and DELIVERY FORMAT.

Cost: one wasted Opus session on 2026-10-02.

Prevented by: SESSION_MANIFEST now loads the checklist and this file
at boot; DSA_SESSION_PROMPT.md section 3 step 10 requires the checklist
run before any prompt leaves the surface.

Structural fix still pending: scripts/dev/prompt_check.ps1, a real gate
that greps a composed prompt against disk and refuses launch on FAIL.
Filed for later.

## 2026-10-03 - DSA pacing: batch reads at boot, one block per phase

Cost: roughly ten turns burned in MTS-2026-10-03-1444Z-DSA-COO-tf4-compose
on context gathering that fits in two.

What happened.
1. Reads split across five turns (git state, queue state, execution
   inventory, three audits, five extracts, OPERATOR_RULINGS, CLAUDE.md,
   BUILD_PIPELINE) when one batch would have returned all of it.
2. Two reads used wrong path prefixes (.\runtime\queue, .\execution).
   The files live under MyTradingSys\runtime\queue and
   MyTradingSys\execution. Both returned empty; two turns lost.
3. The writer-check (index.lock, reflog tail, session-record mtime)
   ran after the operator asked, not inside the compose step.
4. A process-list grep matched Claude Desktop Electron helpers and
   long-lived Code sessions. I reported "two Opus sessions running"
   when the count was three and the idle state was unverified.

Rules that now prevent it.
- At boot, issue ONE command block that returns: the last three commits and
  the working-tree state; .git\index.lock; queue pick_state + pick_log tail;
  session-record mtimes; execution/ file list; the day's audit inputs.
  No follow-up read unless the paste shows a missing path.
- Every path is MyTradingSys\... . Never .\runtime\... or .\execution\...
  from the repo root.
- The writer-check is part of compose, not a response to a challenge.
  Run it inside the same block as the boot batch, before any prompt prints.
- Process check filters to Name='claude.exe' AND CommandLine matches
  'claude-code'. Electron helper PIDs (renderer, gpu, crashpad, network)
  are not writers.

Where the rule lives: this entry is the record until
DSA_SESSION_PROMPT.md section 5 TASK LOOP step 1 and section 3 boot
procedure carry the batch-read rule. Section 3 step 11 (prompt archive)
and section 8 (paths, test both prefixes) already cover parts of it.

Receipt: cost measured against MTS-2026-10-03-1444Z-DSA-COO-tf4-compose;
commit c9319e9.

## 2026-10-03 - Gate guard failed; commit landed on FAIL

What happened: the guarded gate block ran, printed ABORT: build FAIL,
and gitsnap still ran. Commit bb9d73c landed on a failing doc test.

Cause: in an interactive paste, return at top level does not abort the
remaining statements. Same rule already in live_session_protocol.md
PROCESS SPEED RULES #2, dated 2026-09-19.

Fix: every gate+commit block is wrapped in & { ... }. return inside
& { } aborts the block. Confirmed 2026-10-03.

Cost: one FAIL commit on fast-track, one fix commit to follow.

## 2026-10-03 - CLI prompts must open with mts go

What happened: the TF5 promote prompt (session MTS-2026-10-03-1700Z-CLI-SUP-tf5-promote) was printed as bare text with no mts go launch block. DSA dropped the launch and handed the operator a naked prompt.

Rule that now prevents it: every CLI prompt DSA prints opens with the mts go launch block. The prompt text follows the launch. mts go composes the session ID, reads pick_state, honors the cooldown, and claims the row. A bare CLI prompt skips all four.

Where the rule lives: USER.md LIKES (prompt-fence bullet) and DSA_SESSION_PROMPT.md section 9 HARD RULES.

Receipt: operator 2026-10-03.

## 2026-10-03 - Row order is not dependency order; read the blocker cell

What happened: DSA told the operator TF6 could not run until TF5's promote landed. TF6's blocker cell reads only 1.6 (TF4). TF4 was LANDED. TF6 was pickable the whole time. The picker proved it: mts go launched MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena on the next tick.

Cause: DSA read the row number (1.8 follows 1.7) instead of the blocker cell (1.8 blocker = 1.6). Pipeline row order is not dependency order.

Rule that now prevents it: before saying a pipeline row is blocked, name its blocker cell and the blocker's current status, read from BUILD_PIPELINE.md in the same turn. The picker reads the blocker cell; DSA reads the same cell.

Where the rule lives: DSA_SESSION_PROMPT.md section 5 TASK LOOP step 1 VALIDATE.

Receipt: operator 2026-10-03.

## 2026-10-03 - gitsnap stages the whole tree and swept another writer's file

What happened: two DSA commits swept a live session's in-flight file into DSA's commit. 9d43d03 captured TF4's EXEC_PROVENANCE_AUDIT.md mid-work. 91c2d0a captured TF6's test_tom_golden.py mid-work. Both sessions reported the sweep in their own T5 MISSED.

Cause: gitsnap stages the entire working tree. With a second writer active, the stage captures whatever is on disk, including another session's stage.

Rule: when a second writer is active, stage exact paths and commit by hand. Confirm the stage list equals the files DSA wrote before commit.

Where the rule lives: DSA_SESSION_PROMPT.md section 6 WRITING.

Receipt: two incidents, both self-reported by the swept session.

## 2026-10-03 - Stop conditions must name the harm and the mechanism

What happened: the TF5 promote prompt (MTS-2026-10-03-1700Z-CLI-SUP-tf5-promote) carried a T0 rule reading "if a trade is open, STOP and report". The session read three position_manager processes as "trade open", stopped at T0, and touched nothing. The promote is still pending.

Cause: the rule was written without naming the harm it prevents or the mechanism by which the promote would cause that harm. The promote touches auto_trader.py, auto_trader_config.json, and test_auto_trader.py. position_manager.py is a separate process; it loads its own plan file at start and does not reload the auto_trader config. Promoting auto_trader does not affect a running position manager.

Rule: every STOP or BLOCKED condition in a composed prompt names two things in one line - the harm it prevents, and the mechanism by which the target change would cause that harm. A condition that fires on an unrelated process or file is over-broad. The check is a dependency check, not a process check: name the file or field the target change touches and the code that reads it.

Where the rule lives: DSA_SESSION_PROMPT.md section 5 TASK LOOP step 1.

Receipt: operator 2026-10-03. One promote session blocked at T0, no files touched, no commit, staged files unchanged.

## 2026-10-03 - mts go feeds the prompt into whatever CLI window is foregrounded

What happened: after TF7 landed, DSA said "run mts go". The operator ran it while the TF7 claude window was still the foreground shell. The picker wrote the TF8 prompt to next_task.txt and echoed it. The TF7 window consumed the echo as its next user message. TF8 T0 started under the TF7 session ID. Caught before any TF8 file was written.

Rule: before telling the operator to run mts go, check the shell state. If a claude window is foregrounded in the same shell, mts go feeds the prompt there. The picker composes the ID from the clock and echoes the text; it does not open a new window.

Shape: Ctrl+C twice in the CLI window to exit claude. Then run claude fresh. Then paste the prompt from next_task.txt.

Where the rule lives: DSA_SESSION_PROMPT.md section 9 HARD RULES.

Receipt: operator 2026-10-03.

## 2026-10-03 - A directory-scoped stage verb is not exact paths

What happened: to commit three .new deletions, DSA used a directory-scoped stage with the update flag on MyTradingSys/execution/. That directory also held three pm_heartbeat JSON files the loop writes every cycle. All six were staged; the commit added the current content of the three heartbeats.

Rule: "exact paths" means the explicit file list, never a directory. Every add is a named file. If a directory is used, the staged list is reviewed and any path DSA did not write is unstaged before commit.

Where the rule lives: DSA_SESSION_PROMPT.md section 6 WRITING.

Receipt: commit 7a1749c.

## 2026-10-03 - Quoted the 30-line cap, then broke it in the same session

What happened: DSA composed a TF4 prompt at roughly 60 lines. CLAUDE.md says "Prompt <= 30 lines." DSA had quoted that line two turns earlier, then composed over it. Caught during the operator challenge pass, corrected to 28 lines before the prompt shipped.

Rule: the 30-line cap is read from RELAY.md "Task list standard" at compose time, not from memory. Count the prompt lines before printing. If a prompt carries inherited hard rules or restated state, that is a defect: CLAUDE.md and STATUS.md already have them.

Where the rule lives: RELAY.md "Task list standard" (block <= 30 lines, enforced by `relay.py lint`). (CLAUDE.md "What a CL prompt carries" was folded into these on 2026-10-15.)

Receipt: operator 2026-10-03.

## 2026-10-03 - SUPERVISOR_LOG entry attributed a promote to a session that did not exist

What happened: DSA wrote a SUPERVISOR_LOG entry for the TF5 promote with "from: MTS-2026-10-03-1725Z-CLI-SUP-tf5-promote". That session ID was invented. The promote was performed by a PowerShell block from DSA chat, not by a CLI session. The CLI promote session that was launched stopped at T0 and wrote nothing.

Rule: the "from:" field in a SUPERVISOR_LOG entry names an actor from disk, not an actor DSA thinks should exist. If a promote is done by a PowerShell block, the field reads the operator block description, not a session ID. If a session ID is named, the session record must exist on disk before the entry is written.

Where the rule lives: DSA_SESSION_PROMPT.md section 6 WRITING.

Receipt: commit b31b7bf corrected the entry.

## 2026-10-04 - Group rows by file set, not wave order

What happened: DSA printed a 30-step sequential plan for pipeline rows. Operator asked why 30. Re-laid as 23 groups. Operator then asked if the groups were sequential; DSA admitted most were parallelizable. Two operator corrections, two re-lays.

Rule: group rows by file set (one-writer-per-file-set, B086). Walk each row, name its files, merge rows whose file sets overlap. Two rows with disjoint paths run concurrently. Wave order is a priority hint, not a schedule.

Where the rule lives: DSA_SESSION_PROMPT.md section 6b BATCHING.

Receipt: operator 2026-10-04.

## 2026-10-04 - Stop hedging when the pair is parallel-safe

What happened: after composing B104 (prompt-hygiene check) and B100 (audit verdict labels) with zero shared paths, DSA wrote "Recommendation: run B104 first, then B100." Operator: "why u gave me both if they were not both supposed to be sent togther?"

Rule: after naming the file sets, state the collision check and stop. Disjoint: run together. Overlap at a named path: order X then Y. One line. No recommendation.

Where the rule lives: DSA_SESSION_PROMPT.md section 6b BATCHING.

Receipt: operator 2026-10-04.

## 2026-10-04 - Resolve-Path throws on a file that does not exist yet

What happened: twice, [IO.File]::WriteAllText with Resolve-Path on the target path, for a file that did not exist yet. Resolve-Path threw, the batch stopped. Cost: two retries.

Rule: build the path with Join-Path using $root = (Get-Location).Path. Resolve-Path is only for files that already exist.

Where the rule lives: DSA_SESSION_PROMPT.md section 6 WRITING.

Receipt: B129 item doc write, B129 session record write.

## 2026-10-04 - A diagnostic line that throws aborts a commit batch mid-flight

What happened: in the E2-T revert batch, a probe called .Substring(0,60) on a shorter string. The probe threw before any write to the audit. The push earlier in the same block had already landed. Half-completed batch, one retry.

Rule: no diagnostic line that can throw between the first write and the commit. Probes go in their own block after commit, or wrap with a length guard: if the string is long enough to slice, slice; otherwise print the whole string.

Where the rule lives: DSA_SESSION_PROMPT.md section 6 WRITING.

Receipt: E2-T revert batch; the audit write landed in 94310a3.

## 2026-10-04 - git trailers custom format hides a trailer behind a blank line

What happened: DSA read push trailers using the trailers:key custom format in the log command. It returned blank for f088b52 and 18ed141. DSA reported "missing trailer, file a row." Both commits carry the trailer; a blank line before Co-Authored-By hides it from that format. One wrong claim, one correction.

Rule: read trailers with the log command's --format=full followed by a body grep. Do not use the trailers:key format when another trailer paragraph may follow.

Where the rule lives: DSA_SESSION_PROMPT.md section 9 HARD RULES.

Receipt: f088b52, 18ed141.

## 2026-10-04 - Flipping a verdict label without reading the row

What happened: B100 prompt (audit verdict-label mismatch) told the session to flip E1b and E2 from NO-SOURCE to CONCEPT-ONLY. E1b-T was correct. E2-T's own row text lists 0 hold-time rules in 58 transcripts and calls its nearest quotes Opposed. The session followed the instruction and flagged the concern in its reply. E2-T needed a revert (94310a3) plus an audit count resync (a20f602).

Rule: before composing a "flip verdict X to Y" prompt, read the target row's own evidence cell. If the row contradicts the flip, the prompt says: read row R. If the row's own text supports CONCEPT-ONLY, flip. If not, state why and leave NO-SOURCE. Verify-then-edit, not edit-then-verify.

Where the rule lives: DSA_SESSION_PROMPT.md section 5 TASK LOOP step 1 VALIDATE.

Receipt: B100, 94310a3, a20f602.

## 2026-10-04 - Angle brackets in a composed prompt now fail prompt_check

What happened: DSA prompts carry the commit-trailer instruction with angle brackets around the ID placeholder. B104 (prompt-hygiene check) landed check 8 the same day, which fails any angle-bracket token in a composed prompt. Going forward, DSA prompts fail their own gate.

Rule: the trailer instruction reads: Commit trailer: MTS-Session: followed by the ID you composed per SURFACE_POLICY section 4. No angle brackets in composed prompt text. A placeholder-shaped instruction is a placeholder.

Where the rule lives: DSA_SESSION_PROMPT.md section 9 HARD RULES, near the mts go launch-block line.

Receipt: B104 (60f3250).


## 2026-10-04 - Applied a CLI-only rule to App prompts

What happened: USER.md LIKES and DSA_SESSION_PROMPT.md section 9 both scope
the mts go launch block to CLI prompts. This session printed three App prompts
(B093, T037, B133) each opening with the block. Operator: "from where do you
read mts go? why it is here?" Same defect twice this session, and once earlier
in the week (B104 break #6).

Rule: the mts go launch block belongs to CLI prompts only. App prompts open
with Session ID, Mode line, repo root, then the task brief. Before printing
any prompt, read the surface line and pick the opening that matches.

Where the rule lives: DSA_SESSION_PROMPT.md section 9 (line to add);
prompt_check.ps1 check 12 (code gate); B133 item doc.

Receipt: B133 filed df5059e.

## 2026-10-08 - `git stash push -- <pathspec>` emptied the index while renames were staged

What happened: during the wiring cleanup, a fail-before proof used `git stash push -- <paths>` while `git mv` renames were
staged. The index came back empty (status showed everything as deleted/untracked); working-tree files were intact.
Recovery: `git read-tree HEAD` rebuilt the index without touching files, then the changes were re-staged by explicit path.
Nothing lost, but a parallel session's staged work in the same tree would have been wiped.

Rule: no `git stash` in a shared tree (CLAUDE.md already bans it). Fail-before proofs copy the old file aside
(or run the test against `git show HEAD:<path>` written to a scratch dir), they do not stash.

## 2026-10-09 - commit swept another session's staged files
What happened: commit 02e7598 (DSA slim boot) also contained four files another session had staged: backtest/layers/alerts/live_runner_cli.py, alerts/test_live_runner_wiring.py, consensus/hook.py, consensus/test_hook.py. I added exact paths but never listed the staged set before committing.
Rule that prevents it: run the staged-file list (names only) right before every commit; if it holds a path you did not write, unstage it first (CLAUDE.md hard rule: no reset, so unstage only that path).
Where the rule lives: DSA_SESSION_PROMPT.md section 6 (after any write, review the staged list).
Cost: the other session's edits are in my commit; working tree unchanged, nothing pushed. The owning session should know 02e7598 holds its four files.

## 2026-10-12 - layer backtests ran before the encoding, ground truth and market fit were checked
What happened: Tom/Fabio backtests on BTC were run and tuned while the encoding did not fire on the trader's own ledger trades, levels were not checked against drawn levels, and the source's home market/timeframe was not the tested one (BACKTEST_FAILURES_RESEARCH.md classes C1, C2, C8).
Rule that prevents it: no layer backtest starts until the 12-item readiness template (encoding fidelity: recall AND fire rate on a held-back check set; extraction from frames: ledger with minute timestamps; market/timeframe transfer: home-fit and cost per instrument) is answered with file:line evidence.
Where the rule lives: MyTradingSys/backtest/PRE_REG_TEMPLATE.md; test_pre_reg_template.py; PROJECT_VISION DIRECTION UPDATE.

## 2026-10-15 observer: red gate without an owner, colliding gate runs, an unshipped "shipped"
- The card aibridge-live-selftest-flaky was filed 2026-10-14 (d140cbaa). For about 13 h no session owned it, while live-read, gpt-cards and malkan-extract each lost 11-minute ship runs to it.
- At 13:47Z three `run_all_tests.py --quick` runs from different sessions ran at once on JIS-NB. The failing selftest reads a shared task directory, and a different sub-check failed each time.
- live-read reported afaf3dae "on fast-track". The coordinator relayed that to the operator. In fact `git cherry origin/fast-track afaf3dae` printed "+".
RULE: two sessions report the same red gate test, so the coordinator starts a Sonnet fixer within the hour. At most 2 `sync.py ship` / `run_all_tests.py` runs per machine at once. A "shipped" claim quotes an empty `git cherry origin/fast-track <sha>`.
