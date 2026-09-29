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
- Recurring pattern (git log: 86 commits say fix/revert; 14 say false halt/stale/fail-open/closed):
  most incidents were state or accounting assumptions in live code, not strategy. RULE: before editing a
  live path ask "what happens on restart, reset, transfer, partial fill, API error?" and test one of them.
- `--hours` in new_plan is an entry window, not a time exit: one wide bracket held the single slot 7 h and
  6 signals were skipped_busy. RULE: read what a parameter does in code before reasoning from its name.
