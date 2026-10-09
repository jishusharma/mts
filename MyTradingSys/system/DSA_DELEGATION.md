# DSA DELEGATION - hand work to DeepSeek (DSA) through AIBridge to save Claude cost

Operator order 2026-10-09: use DSA as much as possible; invent ways to use it. Claude (any surface) is the
expensive tier; DSA via AIBridge has full run reach in the project tree (AIBRIDGE_LANE.md) and costs no Claude budget.
Rule of thumb: if the job is "run it, read the numbers, write them down", it is DSA's. If it needs
judgment about code that trades, or a result DSA failed twice, it is Claude's.

## The mechanism (no new code: the desk board already exists)
- Claude (or the operator) posts a task: `python scripts/dev/desk.py post "<title>" --need "<exact commands/paths>" --done-when "<observable>" --target DSA`
- DSA at boot (prompt 5e) runs `python scripts/dev/desk.py list`, takes tasks with target DSA, works in `mts-dsa`,
  closes with `desk.py done <id> --result "<numbers + file>"` (or `--failed --result "<reason>"`), ships with `sync.py ship`.
- Claude reads results with `sync.py start` + `desk.py list --all`; it never redoes a closed task, it spot-checks ONE claim.
- Budget per DSA task: every step inside the 300 s bridge cap. A long job is posted as numbered steps (chunk by year or
  symbol), each writes its output to a file; the last step merges them.

## What goes to DSA (T0/T1 lane)
| Job | Why DSA can do it | Output |
|---|---|---|
| Run an existing backtest/probe with new parameters or on another year/symbol/timeframe | script exists, only args change | results file + RESULT.md table |
| Stratify an existing verdict by session or regime (B154) | re-slice an existing CSV | table per stratum, n per cell |
| Run the offline gate (`run_all_tests.py --quick`) and report failures verbatim | read-only | pass/fail list |
| Regenerate STATUS.md, session paste, news | single commands | line saying done |
| Inventories: transcripts extracted vs total, files per folder, NO-SOURCE parameters list, open-claims audit | grep and count | counts file |
| Source hunts: find the transcript quote + file:line for a NO-SOURCE parameter (B142-B145) | grep over transcripts | quote or "NOT FOUND in N files" |
| Archive/declutter (`declutter_backups.py --apply`), stale-claim sweep | script exists | counts moved |
| Control Room pickup: record inbox items verbatim, rebuild page | procedure in CONTROL_ROOM.md | OPERATOR_INBOX.md lines |
| Fetch public market data into F:\MTS\data (klines, funding) with the existing fetch scripts | scripts exist | file list + row counts |
| Draft first version of an item file, a RESULT.md or a doc from numbers it ran | writing | file; Claude reviews only if it touches rules |

## What stays with Claude
Live-path code (auto_trader, position manager, Java), safety checks, new strategy logic, formula tests,
anything touching the CLAUDE.md hard rules, and a DSA task that failed twice. Claude writes the test and the
spec; DSA may run them.

## Making DSA tasks cheap to succeed (rules for whoever posts)
1. Paste exact commands (copy-ready), the expected file name, and one observable done-when. No "figure out".
2. Name the worktree: `mts-dsa`. Data paths on F:\MTS\data are read-only for DSA.
3. State the stop condition: "if a command fails twice, close the task --failed with the error text."
4. Numbers claimed in the result must come from a file DSA printed in the chat (prompt 0.1 rule).
5. Block format (AIBridge parser): no source line may begin with a hash; build one from [char]35; keep lines under about 200 chars.

## Operator guide: where, when, how

| Situation | Where | What you do |
|---|---|---|
| Starting a DSA session | DeepSeek chat | Run `scripts\start-session.ps1`, paste `Dumps\SESSION_PASTE.txt`, say: "Check the desk tasks for DSA and do them." |
| You have a question or idea | MTS Control Room Inbox | Paste it word for word. A Claude or the cloud poller files it; if it is a run-and-report job it becomes a DSA desk task. |
| You want a backtest or inventory now | DeepSeek chat | Say what, in one line ("rerun T089 for 2024 only"). DSA runs it. No Claude needed. |
| You want a decision asked of you | Control Room decisions | Answer there. Claude never asks in chat. |
| Claude session is running low on budget | Claude | Say "post the rest to DSA". Claude posts desk tasks with `--target DSA` and ends the session. |
| Weekly reset hold / both Claude accounts empty | DeepSeek chat | DSA keeps the queue moving: it takes any open `--target DSA` task. |
| Something looks wrong (refusal, no result seen) | DeepSeek chat | Check the AIBridge extension is loaded and the tab is reloaded; DSA falls back to paste mode (prompt 0.7). |
| A DSA result looks suspicious | Claude (Sonnet) | Ask for a spot check of one number. Do not ask for a redo. |

Daily rhythm that costs the least: morning, one DSA session pulls `desk.py list`, runs the queue and ships;
Claude sessions start with `sync.py start`, read DSA results, post the next tasks, and stop at the short-session limit.

## Standing DSA queue (ideas to keep it busy; post as budget allows)
1. B154 stratified verdicts over every existing result CSV (session x regime), n per cell.
2. NO-SOURCE sweep: for each of B142 B143 B144 B145 search the transcripts for the parameter; report quote or NOT FOUND.
3. Transcript inventory: Tom videos extracted v2 vs total; other speakers extracted vs inventory.
4. T085 order-imbalance 4-12 h (operator choice in D08): run once the spec exists; Claude writes spec, DSA runs it.
5. Re-run every RESULT.md number from its script monthly; report drift (cheap regression check).
6. Daily: `run_all_tests.py --quick`, STATUS regenerate, `sync.py where`, stale-claim sweep, one line to the inbox.
7. Fetch refresh: klines/funding up to yesterday for the symbols in the registry.
