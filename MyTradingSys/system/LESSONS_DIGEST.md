# LESSONS DIGEST - the rules only (boot read; stories stay in LESSONS_LEARNED.md)

Source: `MyTradingSys/system/LESSONS_LEARNED.md` (38 KB, append-only history). This file is the RULE line of every entry,
grouped by who needs it; `[A]`..`[G]` = lettered section there, `[10-03 title]` = dated entry. Read the full entry when a
rule touches your task. Adding a lesson: append the story to LESSONS_LEARNED.md AND one rule line here, same commit.
Synced with LESSONS_LEARNED.md at blob: c5767610 (STATUS.md flags this file STALE when that blob changes).
Hard rules and gates live only in CLAUDE.md and are not repeated here; prompt-composition rules for the chat surface live in DSA_SESSION_PROMPT.md and RELAY.md.

## 1. Accuracy (every session)
- The gate must EXECUTE every file a change touches; if no test does, add a static/AST check first. [A]
- Label expectations `EXPECT:` and results `RESULT (date, machine):`; never mix them. [A]
- Status comes from code/tests, never from a doc alone; spot-check one claim before acting. [A]
- Any reply that cites an external source / states what exists on the internet runs playbook PART I STEP 1 first. [A]
- Never truncate output you draw a conclusion from; count by parsing the real format, then state the number. [F]
- Read what a parameter does in code before reasoning from its name. [F]
- Edit by matching text, never by a line number from an earlier read. [G]
- No claim that a file exists / was written without a same-turn disk read; read cited paths and lines before quoting them. [10-02 prompt delivery; 10-02 DSA list]
- "Not on disk" checks all branches and refs; cross-branch diffs use three dots; "is it merged" uses `git cherry`. [10-01 lessons; 10-02 DSA list]
- A "shipped" claim (worker report, relay line, message to the operator) quotes an empty `git cherry origin/fast-track <sha>`. [10-15 observer]
- Recursive file searches scope to src/ explicitly; backup_session/ copies shadow real files. [10-02 DSA list]
- If an instruction references advice not found in repo or memory, ask in the first reply. [E]
- Check the observable result before re-asking the operator for a task. [F]

## 2. Research / backtests
- A hypothesis suggested by DEV results is tested once on VALIDATION as one pooled trial, never promoted on its DEV p-value. [E]
- Volume flags use a same-slot (hour or weekday) baseline; plain relative volume is a clock for BTC. [E]
- Placebo/permutation shifts are drawn without replacement and the lags are printed. [E]
- Collection-only families are marked as such in config + log, kept out of edge claims; pick a hold where fees do not decide. [G]
- Before flipping a verdict label, read the row's own evidence cell; verify then edit. [10-04 flipping a verdict]
- No layer backtest starts until the 12-item readiness template `MyTradingSys/backtest/PRE_REG_TEMPLATE.md` is answered with file:line evidence (encoding recall AND fire rate on a held-back check set, ledger with minute timestamps, home-market fit and cost per instrument). [10-12 backtests before encoding]
- Plan edge research as option arms plus branch rules before any run (PROBE_PLAN.md pattern); CME BTC trades 24/7, so gap rules are DAX-only. [operator 2026-10-11]
- Research briefs follow `methodology/playbook.md` Part I: tier every source T1-T3/REJECT and verify each citation. [operator]

## 3. Live path (execution/, layers/alerts/, anything a running process imports)
- Any P/L/risk metric gets a test with deposits/transfers/funding; use trade-type transaction logs. [F]
- On missing/reset state a live emitter starts at NOW; backfill is a separate explicit command. [F]
- Liveness/safety checks fail CLOSED; specs name the exact output path. [F]
- A halt/guard may block risk-ADDING orders, never the protective reduce-only stop; check the halt after the stop is live. [B]
- Before editing a live path ask: restart, reset, transfer, partial fill, API error? Test one. [F]
- Safety paths (kill switch, stops, loss guard) get an ordering/failure-mode review, not a diff skim. [F]
- Process exit is not position state: the exchange decides flat; network reads retry, then fail closed. [G]
- A new state location greps every reader of the old path in the same change and tests the real on-disk layout. [G]
- One owner per area at a time; the other session proposes only. [G]
- Anything outcome review needs is appended to the ledger at close. [G]
- Read routing from auto_trader_config.json, never from a brief. [G]
- Pauses and temperature limits are enforced in worker code, not only in instructions. [G]
- Never kill python by image name (`taskkill /IM python.exe` killed the whole live stack 2026-10-10). [NEXT_SESSION 13:30Z incident]
- SUPERVISOR_LOG "from:" names an actor that exists on disk (cicd_run lint L1). [10-03 SUPERVISOR_LOG]

## 4. Git and shared trees
- No `git stash` in a shared tree; fail-before proofs copy the old file aside or use `git show HEAD:<path>`. [10-08 stash]
- Stage exact file paths, never a directory or stage-all; list the staged set right before every commit and unstage what you did not write. [10-03 gitsnap; 10-03 directory-scoped; 10-09 commit swept]
- Read trailers with `--format=full` + grep, not the `trailers:key` format. [10-04 git trailers]
- A stale 0-byte `.git/index.lock` with no git process running is safe to remove. [D]

## 5. Workers, cost, tokens
- Spot-check one concrete claim per worker report; never merge a worker's change without reading its diff. [B]
- Two sessions report the same red gate test: the coordinator starts a Sonnet fixer within the hour. [10-15 observer]
- At most 2 `sync.py ship` / `run_all_tests.py` runs per machine at once; 3 at once collided on the AIBridge selftest. [10-15 observer]
- When a worker says "wait"/"blocked", ask whether a cheaper route exists (e.g. older history from data.binance.vision). [B]
- Expected values are hand-derived from the spec; a test fixed "to match the implementation" can turn tautological. [B]
- EXPECT lines name text that is NEW in the change; read verify's `+N -M` count. [B]
- Adversarial review stays at Sonnet/Opus plus repro scripts. [B]
- OUTPUT_TOKENS covers the whole reply (~bytes/4 + headroom); never lower it when splitting. [B]
- Summaries are checked against the request checklist item by item. [F]
- Wait with one background shell, never a polling agent; hand workers paths + line ranges; delegate broad reads to Haiku. [C]
- Every launch prompt names Ultracode on/off, total subagent cap, batch size, "commit and push between batches". [10-02 Ultracode]
- Never write a budget-refusal clause; save-work clause only. [10-02 budget gate]
- Cloud-readable files go under MyTradingSys/research/ or system/, never gitignored Dumps/. [10-02 DSA list]
- Cloud sessions that produce analysis name a DELIVERABLE file and commit it; read-only never means no file output. [10-01 cloud $11]

## 6. Windows / tooling
- Never name a unittest attribute `self.fail`. [D]
- YouTube: at most ~5 caption fetches per session; on a bot check STOP and ask for pasted transcripts. [D]
- Confirm a scheduled task with Get-ScheduledTask before relying on it; long NUC jobs go through the ssh gate `ps-bg` (DEVICES.md section 7). [F]
- PowerShell: `$pid` is reserved; build new paths with Join-Path (Resolve-Path throws on missing files); wrap gate+commit blocks in `& { }`. [10-01 lessons; 10-04 Resolve-Path; 10-03 gate guard]
- Never put prompt content in a PowerShell here-string; use a temp .py with a triple-quoted string. [10-02 DSA list]
- No diagnostic line that can throw between the first write and the commit. [10-04 diagnostic line]
