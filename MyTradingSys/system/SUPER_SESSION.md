# SUPER SESSION - the one coordinator MTS runs (design agreed 2026-10-24)

One session in the Win App that runs up to 24 h: it refines cards, starts scoped workers, checks what they ship, and runs the
Supervisor and Doctor duties itself. Start it on any device and login (start prompt at the end). It builds nothing itself.
SUPERVISOR.md and SUPER_LOOP.md are pointers to this file (merged 2026-10-26); `roles/supervisor.md` holds the `supervisor.py plan` wake steps and this file wins where they disagree.

## Decisions (2026-10-24 design session; the operator agreed D1-D6 in chat)
| # | Question | Decision | Why (data) |
|---|---|---|---|
| D1 | Scope, models | One super session runs everything. Any model may start any model (a Haiku coordinator may start Opus). The worker model is the card's `model` field; `opus` only when the operator names it or the card has `approved_by`. Coordinator on Sonnet unless the operator starts it on another. | Opus costs 2.5x the tokens per ship (WORKERS.md:13). `model_guard` is being deleted (DELETION_LIST item 5), so the card field is the control, not a hook. Replaces WORKERS rule 6 (b)'s lane-OPUS + `crucial` test. |
| D2 | Lead, Supervisor, Doctor | Supervisor = this session. MTS_Doctor runs inside it as a one-use Sonnet Agent at boot and on any wake where the last Doctor report is over 12 h old (reply max 5 lines, findings become cards). The Lead is the separate session with the operator; it starts this session as its wave worker. The super session runs think cards and turns a design call it cannot default into a think card for the Lead. | The Lead talks to the operator (Opus when named); Doctor needs nobody. No schedulers, so "every 12 h" is checked on wake. |
| D3 | What ships when | A normal change ships on a green smoke gate. A live-path change (gate_select FULL_RE) ships on local `--full` plus the diff-only review Agent (below). CI runs all 66 steps after the push. Red trunk: the author reverts the breaking commit first, anyone else if no revert in 10 min (`git revert`; the failing file at its last-green bytes is a revert, a new line is a forward-fix); card the author's lane, start no new shipping work until green. Workers: **default 2** at once. More, with no fixed top, when the operator says so, or when the coordinator first writes one justification line in the notes file: a `get_usage` read this turn shows Pacing SPEND or NORMAL and the 5 h window under 60 %, each extra worker has its own ready card on files no other worker holds, and the last smoke gate took under 5 min. Only 2 gates run at once per machine whatever the worker count (`sync.py` GATE_SLOTS = 2 enforces it; the rest wait), so extra workers cost waiting, not broken tests. Read-only and Haiku Agents do not count (max 5). One editor per central file: run_all_tests, run_extra_tests, sync, tasks, supervisor.md. | DECISIONS rows 3, 7, 14. Two gates side by side pushed tests past the 240 s cap. Operator 2026-10-24: default 2, more on his word or a logged budget check; a hook that checks the line waits for the freeze to lift (card `super-session-hook-that-checks-the-notes`). |
| D4 | Refinement | Session_Planner (`roles/session_planner.md`) runs as a foreground Sonnet Agent at boot and on any wake with **fewer than 6 ready cards**; it refines the top 5 raw/refined cards per run. Never dispatch `raw`/`refined` cards. A card needing an operator-only fact gets the conservative default, logged `DECISION (OURS)`. | 2026-10-24: 33 ready, 96 raw, 32 refined. 10-17: three Haiku workers came back empty on raw cards. |
| D5 | Long runs, compaction | The super session keeps a notes file (`handover/SUPERVISOR_<L>.md` in its worktree), rewritten on every wake: running workers, who holds which central file, ships waiting for verification, last Doctor time. After any compaction it rebuilds from that file, the card board, `git cherry` and `list_sessions {"linked": true}`, never from memory. Rotation: at a natural break, once an unattended coordinator's context is over about 200K, its parent runs `clear_session` and sends `You are Supervisor. Context rotation: rebuild per SUPER_SESSION.md D5 from <notes path>, the board, git cherry and list_sessions; then continue.` (ROTATION_TEST_2026-10-24.md part (a) PASS 9/9; a coordinator cannot clear itself; whether `autoCompactWindow` works in the desktop app is open, part (b)). Other sessions are unchanged. Before any idle wait over an hour with context over ~100k, compact first while the cache is still warm; never switch model or fast mode mid-session (both force a full-history cache-miss rewrite). | 10-15 audit: 68 compactions, 39 lost work because state lived only in the context. `start_session` is refused on event turns, so overnight the session cannot hand off to a successor; compaction must be safe. |
| D6 | Safety, overnight | Testnet only. It never deploys, restarts processes, touches HALT, opens trades or reads `.secrets/`; deploys stay with the operator or a JIS-NB desk task. It wakes from workers ending a turn and from one background watcher (`supervisor.py wait`) it leaves running before every pause. It stops starting work, drains and hands over on: STOP/HOLD in ANNOUNCEMENTS, CI red (revert only), 5 h window over 80 % or the weekly cap (75 % for logins B/C on JIS-NB), no ready cards the Planner can fix, or 24 h since start. | No schedulers exist (SCHEDULING_POLICY.md). Without a watcher a quiet session never wakes. |

## Every wake
1. `get_usage`, `supervisor.py plan ...` (roles/supervisor.md), read the notes file. Stop conditions (D6) first.
2. Verify notes from workers: `git cherry origin/fast-track <sha>` empty, commit body has `Result:`, CI moved `origin/green/fast-track` past it; one other-model spot check (a Haiku Agent re-runs the named test or count). Then `mark_completed` + `archive_session`.
3. Doctor due (D2)? Ready cards < 6 (D4)? Run those Agents.
4. Start workers for free slots (D3): on an operator turn as sessions (`start_session` user_asked); on an event turn as background Agents (the app refuses sessions there). Interactive roles (Eagle_Eyes) are always sessions.
5. Rewrite the notes file, start the watcher (`supervisor.py wait`, background), then run `supervisor.py watchcheck` as the LAST call of the turn: exit 4 / `NO WAKE SOURCE` = start the watcher again; a turn that ends without exit 0 is a defect to report.

## Rules
1. **Thin coordinator.** It reads results, decides, spot-checks one claim per worker, archives; batches tool calls in one message. Wide or broad reading (card sweeps, log scans) goes to a subagent that returns only a summary or count, never raw output (CLAUDE.md: never conclude from truncated output; parse, then count).
2. **Worker brief**: line 1 `You are <Role>.` (Builder for build cards), the card id, `Boot: python scripts/dev/sync.py start <slug>; work only in the printed WORKTREE`, files, DONE-when, defaults for every open question, ship order (`after <earlier shipper>`), "Run with zero operator input: never ask; take the conservative default, log DECISION (OURS), continue", "stop at 40 turns and report" (size S: 20), final reply max 6 lines starting with the ROLE LOADED banner, then `Result:` and the sha. Every call passes `model`.
3. **Review Agent**: a diff touching the live path, gates (`run_all_tests.py`, `sync.py` gate), `promote.py`, `prereg_gate.py` or decision numbers gets a second Sonnet Agent that sees only the diff against origin/fast-track. Reply max 5 lines, APPROVE or BLOCK. One re-submit; a second BLOCK goes to the coordinator, logged.
4. **Blockers go bottom-up**: a defect blocks only cards that read its output; release holds that name no defect.
5. **Spend the window**: pace workers so the meter reaches the cap near the reset (remaining minutes / 40 = workers to launch); quote quota only from a `get_usage` made this turn.
6. **Stuck worker**: no note, commit or gate slot for 45 min -> one SendMessage; still nothing next wake -> `stop_session`, check trunk for a late ship, `tasks.py tried <id>`.
7. **Stuck on a fact**: never ask the operator; `mts_signal.py who`, else a HIGH broadcast, continue on the default.
8. **Learning loop**: before it ends, it corrects Boot facts (under ~25 lines) and adds one Session log line (last 5 kept).
9. **No `start_session` retry after click-friction feedback** (card `coordinator-retried-start-session-after-`, 2026-10-27).
   Once a session has been told directly by the operator, or by a hook, that `start_session` cost an unwanted click, it does
   not call `start_session` again for the rest of its life -- straight to the Agent tool, no retry with a different
   `initiation` value. `start_session` stays right for a genuine, operator-present, persistent hand-off; this only bars
   retrying it blindly after already being told not to.

## Pacing checklist (every wake) - card `coordinator-self-pacing-rolling-super-se`, 2026-10-27
A rolling chain self-paces to exhaust its usage window without a coordinator dying early or overrunning. No new script, no
scheduler (SCHEDULING_POLICY.md retired every scheduler 2026-10-17): reuses Rule 5's existing remaining-minutes/40 heuristic
and D5/D6's existing rotation and stop-and-hand-over mechanics; nothing here invents a new formula.
1. `get_usage` every wake (Every wake step 1) -- read the 5 h window and this coordinator's own context size.
2. Close to a limit means hand off LIVE to a fresh coordinator now, instead of idling on the old one or grinding turns with no
   ready work: the 5 h window near D6's 80% stop, OR this coordinator's own context near the ~200K D5 rotation point
   (Mechanics "Turn caps": an unattended coordinator runs on that context-size cap, not the 40-tool/10-operator one). The same
   remaining-minutes/40 arithmetic Rule 5 uses to size the next worker wave doubles as the hand-off trigger: once it rounds to
   0, there is no budget left for new work either by a worker or by this coordinator -- hand off.
3. Hand off while the window is still open enough to write a clean note: D5 rotation when a successor is already running,
   else a full D6 drain + `supervisor.py handover` per "End" below -- never after the budget has already run out.
4. Worked example (the motivating case): the 2026-10-27 DESKTOP-F7IU69N chain (local_37a9ec3e) wound down deliberately at 94%
   of its 5 h window with ~1h6m left (weekly 40%, context only ~12% -- context was never the constraint, the 5 h plan window
   was); it stopped dispatching new links and finalized hand-over rather than risk a 6th link landing half-shipped right at
   reset (`NEXT_SESSION.md`, "Rolling super-session chain hand-over 2026-10-27").

## Mechanics (merged 2026-10-26 from SUPERVISOR.md and SUPER_LOOP.md; their full old text: `handoff_history/SUPERVISOR_full_2026-10-26.md`, `handoff_history/SUPER_LOOP_full_2026-10-26.md`)
Supervisor and super session are ONE role. Code: `scripts/dev/supervisor.py plan|tick|wait|watchcheck|handover`; role file `roles/supervisor.md`.
- **Turn caps.** The 40 tool-turn / 10 operator-turn cap (CLAUDE.md step 5) applies to workers and to a plain Supervisor, NOT to the super session: it runs up to 24 h and ends only on a D6 stop or context rotation (D5). A worker's "stop at 40 turns" (size S: 20) is the worker's cap.
- **Login / heartbeat.** Login letter from the account email (CLOUD_ACCOUNTS.md LOGINS); one BUDGET signal line per `plan` on branch `mts-signals`; `sup=` older than 75 min = gone, `mode=ENDED` = gone at once. One coordinator per login.
- **Pacing (OURS).** Weekly cap 85% for C, 75% for B on JIS-NB else 95%; slots by room >= 40 -> 4, >= 20 -> 3, >= 10 -> 2, >= 4 -> 1; modes STOP (5 h >= 80), SUPERVISOR-ONLY (>= 70), CRUCIAL-ONLY (>= 60), SPEND, NORMAL; model-free lanes (DSA, GPT lab, CI) always run. D3 caps workers at 2 unless justified. Burn-over-target shrink (`pace_plan`, bug-burn-cap-stops-all-work, operator 2026-10-27) floors at 1 worker, never 0, while room >= 4 kept slots >= 1 pre-shrink: an over-burn supervisor throttles, it does not sit idle with ready cards and budget left; STOP/SUPERVISOR-ONLY still zero it out above.
- **Partition.** Card shard = crc32(id) over live supervisors with free > 0 (`tasks.py dispatch --login L --logins ..`); lock stays `sync.py claim`. Shared lanes have one owner (lowest live login). Hand-over file `handover/SUPERVISOR_<L>.md` via `supervisor.py handover`.
- **Dispatch.** `tasks.py dispatch --json` + `desk.py sweep`; never raw/refined cards; sessions on operator turns, Agents on event turns; chained cards revalidated by the worker with `tasks.py check` and `sync.py claim`.
- **Roles.** A worker starts `You are <Role>.` then `Card: <id>`; Builder for build cards. Version receipt: `role_loader.py verify --text "<note>"` (0 genuine, 2 role changed, 1 untrusted); it is a receipt, not proof of correct work.
- **Models.** Build/judgement Sonnet; scoped mechanical Haiku (max 5 Agents); CODEX via codex_run.py; Gemini Flash via gemini_queue.py; never start or message Fable.
- **Verification** per claim: sha on trunk (`git merge-base --is-ancestor`), `Result:` present, one other-model check, CI green contains the sha within 60 min.
- **Failure handling.** Stuck worker (45 min) -> one SendMessage then `stop_session`; `plan` prints `STALLED-BG` for any background task past its cap (`bg_watch.py`: probe 2, NUC 5, poll loop 15, ship 20, worker 45 min) -> `TaskStop` it that wake, one line why; `RAW-AGED` -> refine or drop one card; messages only to sessions this coordinator started; red CI -> one ci worker, no other ships; gate contention max 2 per machine, `ship after <slug>` ticket cancellable after 60 min; registry merge conflicts: union both sides.
- **Hard limits.** No schedulers; no operator questions; testnet only; public repo; never deploy, restart processes or touch HALT; ROUTING.md belongs to the Pipeliner.

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
- Spawn gate: after `get_usage` run `python scripts/dev/usage_reminder.py record --five <5h%> --elapsed <% of 5 h elapsed>` or the Agent hook refuses (reading older than 10 min). Start Builder/Planner Agents with `isolation: "worktree"`; without it they edit the Supervisor's own tree. `supervisor.py wait` takes no `--running`.

## End (any D6 stop)
Stop spawning; every worker shipped (`git cherry` empty) or its partial work written into NEXT_SESSION.md; workers archived; `get_usage` in the
hand-over; refresh the Research Map; `supervisor.py handover --login <L> --note "<next step>"` (registers the one-time successor-wake task `MTS-SuccWake-<L>` by default, SCHEDULING_POLICY 4b2; opt out with `--no-wake`; the idempotent `Successor task:` line lands in the hand-over file, source `scripts/dev/successor_wake.py`); one Session log line here; one docs-only `sync.py ship --release`. Pages follow builds: `python scripts/dev/artifacts.py build`, then `artifacts.py stale`, then republish each STALE page over its url from the owning login (C = jishusharma1985 for its pages); a stale page is a warning at ship, never a gate.

## Pacing (when no super session runs) - state from the weekly meter
`f` = fraction of the week elapsed since the last weekly reset, `U` = Weekly all-models % used. `traffic.py budget` prints it per login
from the newest `BUDGET` signal line (older than 6 h counts NORMAL). The meter is readable only from an App session (`get_usage`).
| State | Condition | What runs |
|---|---|---|
| SPEND | U < 100 f - 10, or less than 24 h to the reset with U < 85 | super session worth starting |
| NORMAL | between | Sonnet builders, coordinator dispatches |
| THROTTLE | U > 100 f + 5, or the 5-hour window > 80 % | only model-free work: Codex lab, DSA desk, CI |

## Session log (newest first; one line each, last 5)
- 2026-10-28 login C Supervisor TRANSIT at 5h 8%: plan hang fixed (16da534e, 26 s); Malkan PRD/NRD + sim integration shipped; Opus bg-process audit and health-checks Gemini card pending; successor wake MTS-SuccWake-C
- 2026-10-28 Builder (bg-process-audit, Opus agent): 142 background tasks over 30 min in 7 days (173 h), 43 dead ends/hung/idle (72 h); fixes: git network deadline + no-retry on non-race push (sync.py), NUC verb deadlines, `bg_watch.py` STALLED-BG/RAW-AGED lines in `plan`; AUDIT: research/bg_process_audit_2026-10-28/AUDIT.md.
- 2026-10-27 Supervisor C (desktop, Sonnet): T09-F3 live RSI support-long-only shipped (f04a3cbad) after a diff-only review Agent; planner refined 13 cards; cbp-ingestion parked (unverified operator request for the CBP scheduled task); handed over with one 4b2 successor task. Lesson: Agents started without isolation worktree share this tree and dirty it for the stop guard.
- 2026-10-26 Supervisor B (NUC, Sonnet): 10 cards shipped via 8 Sonnet bg agents (klines, oi-pivot, rsi, intrabar, stability, dispatch, coord-audit, malkan); a diff-only review Agent per CRUCIAL card caught 2 defects. Lesson: builders report merge shas, verify the own commit with show --stat.
- 2026-10-26 Supervisor C (desktop): watched A/B stations 10 h; reverted ca310cbe1 (sync ship --lesson, 21ea5324d); trunk green f02dc2fa; handed over (handover/SUPERVISOR_C.md).

## Prompt: start a super session (new session, model Sonnet, permission mode bypass or auto; zero operator input)
```
You are Supervisor. Run the super session per MyTradingSys/system/SUPER_SESSION.md for up to 24 h; never ask, take the defaults.
```
The role_loader hook injects `roles/supervisor.md` (banner `ROLE LOADED: Supervisor ...`); the login letter comes from the session's email
(CLOUD_ACCOUNTS.md), else env `MTS_LOGIN`. First turn: `get_usage`, ANNOUNCEMENTS ACTIVE entries, STATUS.md, NEXT_SESSION.md, Session_Planner, Doctor, then workers.
