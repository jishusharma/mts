# LESSONS LEARNED (living log - append, never rewrite history)

Purpose: every session gets cheaper, faster and more accurate than the last. Each entry states
what went wrong, the rule that prevents it, and where that rule now lives. Add new entries at the
top of the relevant section. Keep each entry to 3 lines.

## A. Verification (accuracy)
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
- 2026-09-30: Tom's stop floor 0.1%/0.2% fallback, 2-3.5R target window, 25% friction haircut and the TWOPEAK label were
  engineering choices with no Tom source; they cut his real trades (tight stops, 8R winners). RULE: parameters come only from
  the trader's own words (CLAUDE.md Provenance); unsourced ones are flagged NO-SOURCE, never tuned. (CLAUDE.md hard rules)
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
# END
