# SUPER SESSION - the one coordinator MTS runs (design agreed 2026-10-24)

One session in the Win App that runs up to 24 h: it refines cards, starts scoped workers, checks what they ship, and runs the
Supervisor and Doctor duties itself. Start it on any device and login (start prompt at the end). It builds nothing itself.
**This file wins** where SUPERVISOR.md, SUPER_LOOP.md or `roles/supervisor.md` disagree (they still hold the `supervisor.py plan`
mechanics; cutting them to pointers is a follow-up after the tooling freeze, ANNOUNCEMENTS A-20261024-1).

## Decisions (2026-10-24 design session; the operator agreed D1-D6 in chat)
| # | Question | Decision | Why (data) |
|---|---|---|---|
| D1 | Scope, models | One super session runs everything. Any model may start any model (a Haiku coordinator may start Opus). The worker model is the card's `model` field; `opus` only when the operator names it or the card has `approved_by`. Coordinator on Sonnet unless the operator starts it on another. | Opus costs 2.5x the tokens per ship (WORKERS.md:13). `model_guard` is being deleted (DELETION_LIST item 5), so the card field is the control, not a hook. Replaces WORKERS rule 6 (b)'s lane-OPUS + `crucial` test. |
| D2 | Lead, Supervisor, Doctor | Supervisor = this session. MTS_Doctor runs inside it as a one-use Sonnet Agent at boot and on any wake where the last Doctor report is over 12 h old (reply max 5 lines, findings become cards). The Lead is the separate session with the operator; it starts this session as its wave worker. The super session runs think cards and turns a design call it cannot default into a think card for the Lead. | The Lead talks to the operator (Opus when named); Doctor needs nobody. No schedulers, so "every 12 h" is checked on wake. |
| D3 | What ships when | A normal change ships on a green smoke gate. A live-path change (gate_select FULL_RE) ships on local `--full` plus the diff-only review Agent (below). CI runs all 66 steps after the push. Red trunk: revert the breaking commit within 10 min (`git revert`, whoever wrote it), card the author's lane, start no new shipping work until green. Workers: **default 2** at once. More, with no fixed top, when the operator says so, or when the coordinator first writes one justification line in the notes file: a `get_usage` read this turn shows Pacing SPEND or NORMAL and the 5 h window under 60 %, each extra worker has its own ready card on files no other worker holds, and the last smoke gate took under 5 min. Only 2 gates run at once per machine whatever the worker count (`sync.py` GATE_SLOTS = 2 enforces it; the rest wait), so extra workers cost waiting, not broken tests. Read-only and Haiku Agents do not count (max 5). One editor per central file: run_all_tests, run_extra_tests, sync, tasks, supervisor.md. | DECISIONS rows 3, 7, 14. Two gates side by side pushed tests past the 240 s cap. Operator 2026-10-24: default 2, more on his word or a logged budget check; a hook that checks the line waits for the freeze to lift (card `super-session-hook-that-checks-the-notes`). |
| D4 | Refinement | Session_Planner (`roles/session_planner.md`) runs as a foreground Sonnet Agent at boot and on any wake with **fewer than 6 ready cards**; it refines the top 5 raw/refined cards per run. Never dispatch `raw`/`refined` cards. A card needing an operator-only fact gets the conservative default, logged `DECISION (OURS)`. | 2026-10-24: 33 ready, 96 raw, 32 refined. 10-17: three Haiku workers came back empty on raw cards. |
| D5 | Long runs, compaction | The super session keeps a notes file (`handover/SUPERVISOR_<L>.md` in its worktree), rewritten on every wake: running workers, who holds which central file, ships waiting for verification, last Doctor time. After any compaction it rebuilds from that file, the card board, `git cherry` and `list_sessions {"linked": true}`, never from memory. Other sessions are unchanged; auto-compaction stays on everywhere. | 10-15 audit: 68 compactions, 39 lost work because state lived only in the context. `start_session` is refused on event turns, so overnight the session cannot hand off to a successor; compaction must be safe. |
| D6 | Safety, overnight | Testnet only. It never deploys, restarts processes, touches HALT, opens trades or reads `.secrets/`; deploys stay with the operator or a JIS-NB desk task. It wakes from workers ending a turn and from one background watcher (`supervisor.py wait`) it leaves running before every pause. It stops starting work, drains and hands over on: STOP/HOLD in ANNOUNCEMENTS, CI red (revert only), 5 h window over 80 % or the weekly cap (75 % for logins B/C on JIS-NB), no ready cards the Planner can fix, or 24 h since start. | No schedulers exist (SCHEDULING_POLICY.md). Without a watcher a quiet session never wakes. |

## Every wake
1. `get_usage`, `supervisor.py plan ...` (roles/supervisor.md), read the notes file. Stop conditions (D6) first.
2. Verify notes from workers: `git cherry origin/fast-track <sha>` empty, commit body has `Result:`, CI moved `origin/green/fast-track` past it; one other-model spot check (a Haiku Agent re-runs the named test or count). Then `mark_completed` + `archive_session`.
3. Doctor due (D2)? Ready cards < 6 (D4)? Run those Agents.
4. Start workers for free slots (D3): on an operator turn as sessions (`start_session` user_asked); on an event turn as background Agents (the app refuses sessions there). Interactive roles (Eagle_Eyes) are always sessions.
5. Rewrite the notes file, start the watcher, end the turn.

## Rules
1. **Thin coordinator.** It reads results, decides, spot-checks one claim per worker, archives. Batch tool calls in one message.
2. **Worker brief**: line 1 `You are <Role>.` (Builder for build cards), the card id, `Boot: python scripts/dev/sync.py start <slug>; work only in the printed WORKTREE`, files, DONE-when, defaults for every open question, ship order (`after <earlier shipper>`), "Run with zero operator input: never ask; take the conservative default, log DECISION (OURS), continue", "stop at 40 turns and report" (size S: 20), final reply max 6 lines starting with the ROLE LOADED banner, then `Result:` and the sha. Every call passes `model`.
3. **Review Agent**: a diff touching the live path, gates (`run_all_tests.py`, `sync.py` gate), `promote.py`, `prereg_gate.py` or decision numbers gets a second Sonnet Agent that sees only the diff against origin/fast-track. Reply max 5 lines, APPROVE or BLOCK. One re-submit; a second BLOCK goes to the coordinator, logged.
4. **Blockers go bottom-up**: a defect blocks only cards that read its output; release holds that name no defect.
5. **Spend the window**: pace workers so the meter reaches the cap near the reset (remaining minutes / 40 = workers to launch); quote quota only from a `get_usage` made this turn.
6. **Stuck worker**: no note, commit or gate slot for 45 min -> one SendMessage; still nothing next wake -> `stop_session`, check trunk for a late ship, `tasks.py tried <id>`.
7. **Stuck on a fact**: never ask the operator; `mts_signal.py who`, else a HIGH broadcast, continue on the default.
8. **Learning loop**: before it ends, it corrects Boot facts (under ~25 lines) and adds one Session log line (last 5 kept).

## Boot facts (read, do not re-look-up; every super session corrects this list)
- Live tree = main checkout `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` (`.mts_live` marker file), read-only; deploy result `MyTradingSys/runtime/sched/auto_deploy_last.json`; HALT `MyTradingSys/execution/HALT`. State: `live_mirror.py brief`, `scripts/sched/check_live_health.py`. Live-tree work goes to a JIS-NB desk row.
- Agents are invisible in the sidebar: name each in one line. The app continues the coordinator when a started session ends a turn or a background Agent/shell finishes.
- Run `sync.py ship` detached when it may pass the 600 s tool cap (`nohup ... > log &`, poll the log). One ship per worker.
- CI: the `ci_watch.py` hook prints `CI RED`; manual `python scripts/dev/ci_watch.py`. `gh` is not installed on JIS-NUC or DESKTOP-F7IU69N; in CI rerun only the failed job (`gh run rerun <id> --failed`).
- New research test files must be registered in run_all_tests / run_extra_tests.EXTRA (or skipped with a reason); study scripts need a `wiring_registry.json` entry.
- `tasks.py` has no host field: `lane` carries it (JIS-NB, CODEX, DSA-NUC, SONNET, HAIKU). Ready list: `tasks.py list | grep ready`. Cards that change the live tree (nb-*) are operator-side. A card can hold a hidden HOLD `note` that `tasks.py brief` omits: read it first.
- Codex lab: `codex_run.py` merges origin/fast-track before it picks; a brief must name its data path (F:/MTS/data/bigtrade/cache/perp/klines_1h.npz). Status from NUC: `printf 'Set-Location F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py status\n' | ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps`. Keep 8+ ready luna/medium cards. Codex and Gemini ship directly; D3's revert rule covers them.
- Research Map: `Artifact read` first, edit the one `const DATA = ` line by script in `system/artifacts/research_map.html`, republish to claude.ai/artifact/9nqpZeMeEehadoBoYopZU3 from the jishusharma1985 login. Backtest = fee check at the stated stop first (fee R = 0.14% / stop%), then PRE_REG on DEV only.
- A worker that merges late hits VERDICTS.csv and wiring_registry.json conflicts: union both sides.
- Login letters: A jishu.sharma, B jishu.awgp, C jishusharma1985.

## End (any D6 stop)
Stop spawning; every worker shipped (`git cherry` empty) or its partial work written into NEXT_SESSION.md; workers archived; `get_usage` in the
hand-over; refresh the Research Map; `supervisor.py handover --login <L> --note "<next step>"`; one Session log line here; one docs-only `sync.py ship --release`.

## Pacing (when no super session runs) - state from the weekly meter
`f` = fraction of the week elapsed since the last weekly reset, `U` = Weekly all-models % used. `traffic.py budget` prints it per login
from the newest `BUDGET` signal line (older than 6 h counts NORMAL). The meter is readable only from an App session (`get_usage`).
| State | Condition | What runs |
|---|---|---|
| SPEND | U < 100 f - 10, or less than 24 h to the reset with U < 85 | super session worth starting |
| NORMAL | between | Sonnet builders, coordinator dispatches |
| THROTTLE | U > 100 f + 5, or the 5-hour window > 80 % | only model-free work: Codex lab, DSA desk, CI |

## Session log (newest first; one line each, last 5)
- 2026-10-24 design session (Opus): this file rewritten from 137 lines; D1-D6 above.
- 2026-10-21 Supervisor B (NUC): GPT lane up, 5 cards back to CODEX; lab caps window 65 / week 90 / 14 runs (DECISION (OURS)); pitchfork layer 79da493c.
- 2026-10-19 Supervisor A (NUC): weekly 93%/95 cap, mode=STOP all window, no workers; handover/SUPERVISOR_A.md; DSA chats need arming.
- SUPER-LENOVO-1019b (2026-10-19, Sonnet): chunk 2 landed 4e88b6d1; full gate passes only with MTS_GATE_JOBS=2, ONE ship at a time; chunk 3 unshipped.
- SUPERLOOP-NB-1019 (2026-10-19, Opus agent): five-hour loop `supervisor.py plan`/`handover`. Lesson: a T0 command beats prose.

## Prompt: start a super session (new session, model Sonnet, permission mode bypass or auto; zero operator input)
```
You are Supervisor. Run the super session per MyTradingSys/system/SUPER_SESSION.md for up to 24 h; never ask, take the defaults.
```
The role_loader hook injects `roles/supervisor.md` (banner `ROLE LOADED: Supervisor ...`); the login letter comes from the session's email
(CLOUD_ACCOUNTS.md), else env `MTS_LOGIN`. First turn: `get_usage`, ANNOUNCEMENTS ACTIVE entries, STATUS.md, NEXT_SESSION.md, Session_Planner, Doctor, then workers.
