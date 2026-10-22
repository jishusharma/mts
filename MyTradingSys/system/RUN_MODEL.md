# RUN_MODEL: talk in the app, work in the CLI (operator 2026-10-22, design v1)

Operator ask (2026-10-22): "use the UI ... to discuss something with the admin guy, the artifact guy, the thinker ... if some task comes out of
it, it will be sent to the CLI directly ... that need not be interrupted ... right models and the right compactions at the right time ...
optimally using all our data plans ... reduce [script time] by half." Status: DESIGN. Phases below say what is built.

## 1. Two surfaces, one queue
| Surface | Who drives | What runs there | Ends |
|---|---|---|---|
| Desktop app (Code tab) | the operator | conversations only: Thinker, Admin_Guy, Artifacts_Guy | on his word; he compacts when he wants |
| CLI (`claude -p`, headless) | `scripts/dev/mts_run.py` (a Python loop, 0 tokens) | every unattended task: build, pipeline, lab check, doctor, research | one card per process, then it exits |

- The queue is the existing card board (`tasks.py`, claims branch). A conversation turns a decision into a card (`tasks.py new`) and is done; no
  click, no child session. `mts_run.py` picks it up on any device whose login has budget.
- The supervisor is the script, not an LLM session: picking, claiming, launching, timing out, logging and pacing are code. An LLM is called only
  for judgement (refine a raw card, review a diff), and then as one short CLI run.
- Roles to remember: three (the conversation roles above). Builder, Pipeliner, Lab_Guy, MTS_Doctor, Eagle_Eyes and Session_Planner become worker
  kinds that `mts_run.py` sets from the card's `worker` field; their role files stay as the worker's brief.

## 2. A worker run
```
claude -p "<card brief>" --model <haiku|sonnet|opus> --permission-mode auto --permission-prompts none
       --tools Bash,Read,Edit,Write,Grep,Glob --strict-mcp-config --max-turns <est_turns x 1.5> --output-format json
```
- Runs in its own worktree (`sync.py start`), with the project hooks (safety_guard, model_guard, turn_meter). Never `--bare` (it skips hooks).
- `--tools` and `--strict-mcp-config` drop the app's connector and browser tools: the fixed cost per step falls from about 75k tokens to the
  core tools only (to be measured in phase 1).
- No compaction for workers: a card is sized to fit (est_turns); a run that hits `--max-turns` writes its hand-over to the card and is requeued
  as a fresh run. Starting fresh is cheaper than summarising a worker's history.
- The JSON result (turns, tokens, cost estimate, result text) goes to the ledger `runtime_data/mts_run/ledger.jsonl` (gitignored). The card is
  UNVERIFIED until a checker run (a different model, Lab_Guy classes) or a test gate passes.
- Tested 2026-10-22: Sonnet, docs-only card, 6 turns, 33 s, $0.094 estimate, 0 permission denials, hooks ran.

## 3. Models
Haiku for mechanical cards, Sonnet by default, Opus only for cards marked crucial with `approved_by` or named by the operator (WORKERS.md rule 6).
Use-it-or-lose-it: in the last 24 h before a login's weekly reset, if that login is under its pace line, eligible cards are run one tier up.

## 4. Pacing the weekly allowance (per login)
- Ledger sums each login's usage this week. Calibration: the operator (or Admin_Guy) records the app's usage reading
  (`mts_run.py calibrate --login A --used 37`), which converts ledger units to "share of the week".
- Pace line = share of the week elapsed. Under the line: run up to `max_parallel` workers. Over the line: one worker, Haiku/Sonnet cards only.
  Over 90%: stop starting work on that login; another device's login takes the queue.
- Each device publishes its login's share to the signal branch, so every device and the conversations see all three logins (awareness ask).

## 5. Compaction rules (all surfaces)
- Conversation in the app: the operator's call. Rule of thumb: compact at a natural break when the context is over ~150k and more than ~5 steps
  are expected; never in the middle of an edit. The old transcript stays searchable.
- Workers: never; one card, then exit.
- Nothing else is long-running: the loop is a script.

## 6. Speed budget (scripts)
| Path | Budget | Measured 2026-10-22 (before, session) | hook_bench before (origin/fast-track) | hook_bench after (this branch) |
|---|---|---|---|---|
| hooks per tool call (wall) | <= 0.5 s | ~1.2 s (2 blocking pre + 2 blocking post) | 0.90 s | 0.40 s (post-tool hooks async) |
| hooks per prompt (wall) | <= 0.8 s | ~1.4 s | 0.99 s | 0.70 s (shot 0.99 -> 0.60; ci_watch, mts_signal async) |
| hooks at stop | <= 1.0 s | ~2.2 s | 2.10 s | 0.82 s (clean tree: no sync.py import, git calls in parallel) |
| `sync.py ship` | stage timings logged; target set from the first 20 measured ships | not measured (no timing code) | - | - |
hook_bench = median of 5 runs per hook on the laptop, state dirs in a temp folder, Stop measured on a clean tree (the common stop); wall of an
event = slowest synchronous hook. The remaining floor is python start-up (0.26-0.55 s per hook); the async hooks add no wall time.
Means: post-tool hooks run in the background (`async`), lazy imports, no git or network in per-step hooks. `scripts/dev/hook_bench.py`
measures every configured hook; `mts_doctor.py` reports it against this table.

## 7. Interview Prep feed
Learning notes live in `MyTradingSys/learning/` with front matter `interview: yes`. `scripts/dev/interview_feed.py export --to <dir>` copies only
those notes (size cap, no paths, no runtime or account data) into the Interview Prep project's inbox; `list` shows what would go. When the
operator asks a "teach me" question in any MTS session, the answer is also saved there as a note.

## Phases
1. Hook speed to budget, away-flag fix, hook_bench, interview feed, this design. (branch hook-speed)
2. `mts_run.py`: once, loop --hours N, ledger, calibrate, pace; one worker at a time; measured fixed cost per step with `--tools`.
3. Parallel workers per device, cross-device usage on the signal branch, checker runs, use-it-or-lose-it upgrade.
4. Retire the app super session and child-session workers; ROLES.md lists the three conversation roles and the worker kinds.
