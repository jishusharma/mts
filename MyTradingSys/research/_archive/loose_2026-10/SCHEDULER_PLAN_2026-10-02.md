# SCHEDULER PLAN - 2026-10-02

Session MTS-2026-10-02-1900Z-CLI-ANA-scheduler-plan. Design only; no code, no schedule installed.
Input: `MyTradingSys/research/_archive/loose_2026-10/SCHEDULER_DESIGN_2026-10-02.md` (the note). Rate card = note section 2.
Billing facts (Agent SDK credit $20 Pro, 5-minute cache TTL, flag names) inherit the note's UNVERIFIED-WEB tag.
Every number tagged ASSUMED is an input to revisit after 30 days of the ledger (section 6), not a measurement.

Note on the brief: the note's section 8 has seven bullets. The first bullet holds two questions (which checks
stay Tier-1, which trigger Haiku), so they are answered separately below to give eight.

## 1. Answers to the eight design questions

### Q1. Which checks stay Tier-1 scripts (no Claude)
All eight detectors are Tier-1 forever. Claude never detects, only interprets a failure. Four never fire a
worker on their own: session-record scan, bug-row health, paste size and .new aging. They are written to a
digest file the daily Haiku reads (Q2). Reason: none is
time-critical, and one batched run replaces up to four runs. The cadence of every detector is 15 minutes,
driven by Windows Task Scheduler, cost $0 in SDK credit.

### Q2. Which checks trigger Haiku
Event-fired Haiku (one run per distinct failure, debounced): Build-Check FAIL, run_all_tests --quick FAIL,
canary RED, snapshot stale. These four can mean the live testnet system is unhealthy or the tree is broken, so
the operator should not wait up to 24 h. Digest-fired Haiku (one run per day, 06:00 local): the four slow
checks above, plus a one-paragraph roll-up of the last 24 h of ledger entries.

### Q3. How many Haiku tiers, what cadence, what trigger
One Haiku tier, one worker, two modes: `event` (trigger = Tier-1 exit code != 0, plus a state hash not seen
in the last 24 h) and `digest` (trigger = daily clock). No higher-frequency Haiku "heartbeat": a heartbeat
is a Tier-1 script. A second Haiku tier would add a second cached prefix for no gain.

### Q4. Where Sonnet and Opus sit, and what fires them
Sonnet fires only from a Haiku report whose `verdict` field is `ESCALATE` with a reason from a closed set:
`multi_file_cause`, `fails_in_2plus_modules`, `needs_patch`, `haiku_unsure`. Haiku never edits code.
Opus fires only when a Sonnet result proposes a change touching `MyTradingSys/execution/`, `layers/alerts/`,
HALT files or orders (the SURFACE_POLICY 3b "safety diff" route), and then it reviews; it does not apply.
Opus is never fired by a detector and never on mechanical failures. No worker edits a file the live testnet
processes import, restarts them, touches HALT or opens trades (CLAUDE.md hard rules); outputs are reports
and `.new` staging only, promoted by a session.

### Q5. Cost model
Section 4.

### Q6. Concurrency
Section 6 (T6): atomic per-job lock plus a tree-write lock plus a process-tree reaper.

### Q7. Cache discipline
Section 7 (T7).

### Q8. One Haiku worker for N checks, or one per check
One worker, check name as argument. The prefix (charter + check catalog) is identical for every check, so
every run shares one cacheable prefix; per-check workers would each need their own prefix and gain nothing.
The check name, evidence path and exit code go after the prefix. Exception: none now. Split a check into its
own worker only if its evidence needs different tools or its prefix grows past 2x the shared one.

## 2. Tier stack (T3)

Per-run cost uses the arithmetic in section 4. Cadence for Claude tiers is "on trigger", bounded by caps.

| Tier | Name | What it does | Model | Trigger | Cadence | Per run |
|---|---|---|---|---|---|---|
| 0 | Clock | Task Scheduler entry runs `tick.py`; holds the lock logic and ledger | none | clock | every 15 min (96/day) | $0 |
| 1 | Detectors | 8 deterministic checks (section 5); write `OK/WARN/RED`, evidence file, state hash | none | tick | every 15 min | $0 |
| 2a | Haiku event worker | Read evidence; classify cause; write 10-line report; verdict `RESOLVED_BY_OPERATOR / ESCALATE / NOISE` | Haiku 4.5 | detector exit != 0 and hash not seen in 24 h | on event | about $0.025 |
| 2b | Haiku digest worker | Read digest file; one summary; same prefix as 2a | Haiku 4.5 | clock | daily 06:00 | about $0.025 |
| 3 | Sonnet analyst | Diagnose across files; draft patch as `.new` staging or report; no commit | Sonnet 5.5 | Haiku verdict ESCALATE, closed reason set | on event, max 2/day | about $0.16 |
| 4 | Opus reviewer | Review a Sonnet safety diff; findings only | Opus 5.5 | Sonnet diff touches execution/, alerts, HALT, orders | on event, max 1/day | about $0.30 (cap $1.00) |

Wrapper limits per run: `--max-turns` Haiku 8, Sonnet 25, Opus 15; `--max-budget-usd` Haiku 0.10, Sonnet 0.60,
Opus 1.00 (flags per note section 7; confirm exact spelling with `claude --help` before building).

## 3. Cost model (T4)

### Per-run arithmetic (ASSUMED token profiles)
Rates per million tokens from the note. A run pays one cache write (runs are hours apart, longer than the 5-minute
TTL, so the prefix is re-written each run), then cache reads on later turns inside the run.

Haiku run: prefix 6k tokens, 4 turns, 8k fresh input, 1.5k output.
- write 6,000 x $1.25/M = $0.0075
- reads 3 turns x 6,000 x $0.10/M = $0.0018
- fresh 8,000 x $1.00/M = $0.0080
- output 1,500 x $5/M = $0.0075
- total $0.0248, use $0.025.

Sonnet run: prefix 10k, 5 turns, 30k fresh input, 6k output.
- write 10,000 x $2.50/M = $0.025
- reads 5 x 10,000 x $0.20/M = $0.010 (five read turns after the write turn)
- fresh 30,000 x $2.00/M = $0.060
- output 6,000 x $10/M = $0.060
- total $0.155, use $0.16.

Opus run: same tokens as Sonnet.
- write 10,000 x $5.00/M = $0.050
- reads $0.010 (same $0.20 read rate)
- fresh 30,000 x $4.00/M = $0.120
- output 6,000 x $20/M = $0.120
- total $0.300.

### Runs per month (ASSUMED event rates; 30-day month)
| Item | Runs/month | Basis |
|---|---|---|
| Tier-1 ticks | 2,880 | 96/day x 30; no SDK credit |
| Haiku event: build FAIL | 4 | assumed |
| Haiku event: test FAIL | 6 | assumed |
| Haiku event: canary RED | 10 | assumed (live testnet incidents) |
| Haiku event: snapshot stale | 8 | assumed |
| Haiku digest | 30 | daily |
| **Haiku total** | **58** | 28 event + 30 digest |
| Sonnet | 10 | 30% of 28 event runs (8.4, rounded to 8) + 2 from digest |
| Opus | 2 | safety-diff reviews |

### Spend per month
- Haiku: 58 x $0.025 = $1.45
- Sonnet: 10 x $0.16 = $1.60
- Opus: 2 x $0.30 = $0.60
- **Expected total = $3.65/month**, 18% of the $20 Pro credit.

### Where the $20 credit is exhausted
- At expected volume: it is not. Headroom = $20 / $3.65 = 5.5x the assumed event volume.
- Break-even volumes if one tier ate the whole credit: 800 Haiku runs, 125 Sonnet runs, 66 Opus runs.
- Runaway case with no debounce (the failure the lock and hash exist to prevent): a flapping detector firing
  every 15-minute tick = 96 runs/day. Haiku: 96 x $0.025 = $2.40/day, credit gone in 8.3 days. Sonnet:
  96 x $0.16 = $15.36/day, credit gone in 1.3 days. Opus: 96 x $0.30 = $28.80/day, credit gone in 0.7 day.
- Hard ledger caps (section 6): at $10 spent, Opus and Sonnet disabled; at $15, Haiku limited to digest only;
  at $18, all Claude runs stop and a RED line is written to the digest file. The $2 margin covers one in-flight
  run (the per-run `--max-budget-usd` caps are $1.00 or less). Overflow billing is never reached on purpose.
- Open question for the operator: the credit pool may be shared with other `claude -p` use (for example
  `scripts/manager/mts-manager.ps1` runs). If so the scheduler's ceiling is $20 minus that use; the ledger must
  read the shared figure, which this plan cannot verify.

## 4. Note on paste size

`Dumps/SESSION_PASTE.txt` is 150,554 bytes today, above the 150 KB threshold, so its check is RED on the first
tick. Handle by the same state-hash debounce (section 5): it enters the digest once, and again only when the
size band changes (150 KB steps).

## 5. Trigger taxonomy (T5)

Every check is a Tier-1 script. State hash = SHA-256 of (check name + condition-relevant evidence). A tier fires
only when the hash is new in the last 24 h (digest checks: new since last digest).

| # | Check (script) | Condition | Fires |
|---|---|---|---|
| 1 | Build health (`scripts/Build-Check.ps1`) | overall FAIL (script sets `$overallFail`; exit code mapping to confirm) | Haiku event |
| 2 | Test health (`python scripts/dev/run_all_tests.py --quick`) | exit != 0 | Haiku event |
| 3 | Canary (`python scripts/dev/testnet_canary.py`) | exit 2 (RED); exit 1 WARN goes to digest | Haiku event |
| 4 | Snapshot freshness (NEW: `scripts/sched/check_snapshot_age.py`) | newest market snapshot older than threshold (threshold to be sourced from the existing snapshot cadence, not invented here) | Haiku event |
| 5 | Session records (NEW: `scripts/sched/check_sessions.py`) | a `MyTradingSys/system/sessions/*.md` with `status: open` older than 24 h, or missing required header fields | digest |
| 6 | Bug rows (NEW: `scripts/sched/check_bug_age.py`) | row IN-FIX for more than 14 days in `MyTradingSys/research/BUGS.md` | digest |
| 7 | Paste size (NEW: `scripts/sched/check_paste_size.py`) | `Dumps/SESSION_PASTE.txt` over 150 KB | digest |
| 8 | .new aging (NEW: `scripts/sched/check_new_aging.py`) | in-flight `.new` older than 24 h (STATUS.md lists 11 of 13 already over) | digest |

Escalation edges: Haiku report `ESCALATE` fires Sonnet (closed reason set, Q4). Sonnet diff touching the
safety set fires Opus. No other edge exists; there is no Tier-1 to Sonnet or Opus shortcut.

## 6. Concurrency (T6)

Mechanism: an atomic lock directory per job, created with `os.mkdir` (atomic on NTFS, fails if it exists).
- Path: `MyTradingSys/runtime/sched/locks/<job>.lock/` (NEW; directory `MyTradingSys/runtime/` exists).
  Inside: `owner.json` with PID, process creation time, start UTC, TTL.
- Job key = tier + check name, so Haiku `build` and Haiku `canary` may run together; two `build` runs may not.
- Acquire: `mkdir`. If it fails, read `owner.json`; the lock is stale only if the PID is not running with that
  creation time, or TTL expired (Haiku 10 min, Sonnet 20 min, Opus 15 min). A stale lock is removed, then
  acquired once. A live lock means this tick exits with code 0 and logs `SKIPPED_LOCKED`.
- Second layer: the Task Scheduler entry uses `MultipleInstancesPolicy = IgnoreNew`, so overlapping ticks
  of `tick.py` never queue.
- Tree-write lock (`tree.lock`, same mechanism) is required by any Sonnet or Opus run before it writes. Workers
  write only under `MyTradingSys/research/sched_reports/` (NEW directory) and `.new` staging. They never run
  `git add -A`, `git commit`, `git reset` or any index command; only a session commits, with a pathspec
  (the commit 803e705 index-sweep cause).
- Orphan prevention: the wrapper starts the `claude` child inside a Windows Job Object with
  kill-on-close, applies the TTL as a wall-clock timeout, and on timeout kills the whole process tree. On the
  next tick, a sweep kills any `claude.exe` whose parent is a dead wrapper PID and is not in `owner.json`.
  The ledger records PIDs spawned and PIDs confirmed gone; a mismatch raises RED.

Spend ledger: `MyTradingSys/runtime/sched/ledger.jsonl` (NEW), appended before the run (reserved max budget)
and after it (actual from the SDK result). The caps in section 3 read this file under `tree.lock`.

## 7. Cache discipline (T7)

- Prefix file `MyTradingSys/system/sched/worker_prefix.md` (NEW) holds, in this order: worker charter, the hard
  rules that apply to workers (copied from CLAUDE.md), verdict schema, check catalog sorted alphabetically.
  Nothing else comes before the variable part.
- Byte-stability rules: no dates, times, hostnames, session IDs, counters or randomness in the prefix; LF line
  endings; no trailing whitespace; tool list and allowed-tools order fixed; the wrapper reads the file as bytes
  and sends it unchanged.
- Variable data goes after the prefix, in one fixed order: mode, check name, exit code, evidence path, evidence
  excerpt, current UTC.
- Stability proof: the wrapper logs SHA-256 of the prefix bytes per run to the ledger; a Tier-1 self-check
  fails RED if two consecutive runs of one model show different hashes without a recorded prefix version bump.
  A test (new test, must fail on a prefix containing a timestamp) asserts the hash is the same across two
  wrapper invocations.
- Edits to the prefix are a versioned change; each edit costs one cache write per model.
- Honest limits: the note's 5-minute cache TTL means runs hours apart pay a cache write each time; reads help
  only inside a run's turns and bursts of events. Caches are per model, so Haiku, Sonnet and Opus each pay for
  their own prefix. The prefix must also reach the model's minimum cacheable length (UNVERIFIED; check the
  figure in the API docs) with real content, not filler. The cost model above already assumes writes, not hits.

## 8. Failure modes (T8)

| Note section 9 failure | Preventing design element |
|---|---|
| /loop for hours, unbounded context | No `/loop` anywhere. Every run is a fresh `claude -p` process from Task Scheduler with `--max-turns` and `--max-budget-usd`; context is bounded by one run. Cost per run is flat. Tier 0 is a script, not a model loop. |
| Orphan processes, server-side billing continues | Job Object kill-on-close, wall-clock TTL kill of process tree, orphan sweep each tick, PID reconciliation in the ledger (section 6). Spend is counted from the reserved budget until a run is confirmed ended. |
| Concurrent workers on one tree, index-sweep | Per-job atomic lock plus `tree.lock`; workers write only to report/staging paths and never touch the git index; commits are session-owned, with pathspec (section 6). |
| Opus on mechanical work | Opus has exactly one edge: Sonnet diff touching the safety set. No detector, Haiku or digest path reaches Opus. Cap 1/day, budget $1. Closed escalation reasons keep Haiku from sending mechanical failures up. |
| Silent overflow beyond the credit | Ledger caps at $10 / $15 / $18 (section 3); per-run budget caps; ledger reads the shared credit figure if other `claude -p` users exist. Overflow billing is never expected, and a spend RED goes in the digest. If usage credits turn out to be enabled on the account, the $18 stop still applies. |

## 9. Path verification (T9)

`Test-Path` run in this session (2026-10-02, repo root). Planned paths marked NEW did not exist and are not
treated as existing; the brief asked that none be invented.

| Path | Test-Path | Role |
|---|---|---|
| `scripts/Build-Check.ps1` | True | check 1 |
| `scripts/dev/run_all_tests.py` | True | check 2 |
| `scripts/dev/testnet_canary.py` | True | check 3 (exit 0/1/2 confirmed in its docstring) |
| `scripts/dev/alert_rate_check.py` | True | reference only (TF/family map; none added by this plan) |
| `MyTradingSys/research/BUGS.md` | True | check 6 input |
| `MyTradingSys/runtime/BUILD_REPORT.md` | True | .new in-flight list source for check 8 |
| `MyTradingSys/research/STATUS.md` | True | .new list and digest context |
| `Dumps/SESSION_PASTE.txt` | True (150,554 bytes) | check 7 input |
| `MyTradingSys/system/sessions` | True | check 5 input |
| `MyTradingSys/system/SURFACE_POLICY.md` | True | routing rules, section 3b |
| `scripts/manager/mts-manager.ps1` | True | possible shared credit consumer |
| `MyTradingSys/runtime` | True | parent of lock/ledger directories |
| `C:\Users\E-ngineers\.local\bin\claude.exe` | True | CLI the wrapper spawns |
| `scripts/sched/` | False | NEW directory |
| `scripts/sched/tick.py` | not tested (parent absent) | NEW, Tier 0 |
| `scripts/sched/check_snapshot_age.py` | False | NEW, check 4 |
| `scripts/sched/check_sessions.py` | not tested (parent absent) | NEW, check 5 |
| `scripts/sched/check_bug_age.py` | not tested (parent absent) | NEW, check 6 |
| `scripts/sched/check_paste_size.py` | not tested (parent absent) | NEW, check 7 |
| `scripts/sched/check_new_aging.py` | not tested (parent absent) | NEW, check 8 |
| `MyTradingSys/system/sched/worker_prefix.md` | False (dir absent) | NEW |
| `MyTradingSys/runtime/sched/` (locks, ledger.jsonl) | False | NEW |
| `MyTradingSys/research/sched_reports/` | False | NEW |
| `MyTradingSys/research/_archive/loose_2026-10/SCHEDULER_PLAN_2026-10-02.md` | False before this file was written | this deliverable |

New items for the queue (none is built here): the six `scripts/sched/` scripts, the worker wrapper with Job
Object and lock logic, `worker_prefix.md`, ledger and cap reader, the prefix-hash test, one Task Scheduler
entry. Before any build, verify the run_all_tests runtime (the 15-minute cadence assumes `--quick` is cheap
enough to run 96 times a day beside the live system) and the Build-Check exit-code mapping.

# END
