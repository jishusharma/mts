# Context files that heal inside the run (design, Fable 5.1, 2026-10-25)

Operator goal (2026-10-25): every session starts from a file that builds the right context from turn one and guides its thinking; a mechanism watches each run, learns from it and improves those files during the same run. "Both kinds of handover, healing within the same run ... simple, guaranteed to work."
Status: DESIGN. Nothing built except this file, one example coordinator file and the baseline measuring script (`context_files/`). The operator approves before any card runs.

## 1. One line
The handover file is never written by the model: for a worker it is the card (`tasks.py brief`), for a coordinator it is `handover/SUPERVISOR_<L>.md` in a fixed 7-section form; a hook on `sync.py ship` reads the session's own transcript and folds what the file missed (files read before the first edit that the file never named) into that file, so the next session in the run inherits it; `tasks.py next` refuses cards whose work is already on trunk; one script measures cold start, misses, stale facts and cache rewrites and is the pass/fail gate. The operator talks to one session, the Lead (section 10), whose file is vision and board state, never code; it rotates by context size or closed discussions, never by the clock.

## 2. What the evidence says (measured this session unless dated)
| Fact | Number | Source |
|---|---|---|
| First-turn base (what the app loads before our files) | median 71.0K tokens; MTS's own share ~2.8K | health24 24 h; context_cost_2026-10-24.md |
| Context per turn | median 131K, p90 197K | health24, 25 sessions, 33.7K turns |
| Full cache rewrites | 454 in 24 h = 18.2 per session (10-24 baseline 0.94); 84% of context in one Opus Doctor (30.5K turns) | health24 |
| Tool calls before the first edit (10 newest sessions, 36 h) | median 12, range 4-29 | coldstart_baseline.py |
| Files read before the first edit that the start prompt never named | median 2.5, range 0-13 | same |
| Context at the first edit | median 95K, range 73K-145K | same |
| Tight brief vs open prompt | brief with files + commands (confluence S2, refine-c, sim-v2): 4-10 calls, 0 unnamed reads, 73-88K; open prompt ("check what MTS says about cleanups", "I need a thinker"): 24-29 calls, 6-13 unnamed reads, 125-145K | same |
| Stale handover | REFINE run: 10 of 28 cards already done on trunk; NEXT_SESSION.md block 2 "Next card: tc4-desk-done-once" while `tasks.py brief` says `STATE SHIPPED@fb6479e15` | REFINE_2026-10-25.md; `tasks.py brief tc4-desk-done-once` |
| Coordinator notes grow by appending | SUPERVISOR_C.md: 82 lines, 8 `## Update`/time-stamped sections, the queue superseded 3 times inside the file | handover/SUPERVISOR_C.md |
| What the unnamed reads were | STATUS.md, ANNOUNCEMENTS.md ACTIVE, the role file, handover/SUPERVISOR_*.md, `tasks.py next/dispatch`, PILOT doc, `mts_signal.py --help` | coldstart sample |

Reading: the base is not ours to cut; the cost we control is the 4-25 exploratory calls (20-70K tokens) a session spends finding what its handover should have named, the sessions that redo shipped work, and the long-lived coordinator whose every wake after a >1 h gap rewrites its whole history.

## 3. The two context files

### 3a. Worker -> next worker: the card is the file
Nothing new to write. `tasks.py brief <id>` already renders goal, scope, steps, tests, done-when, `STATE` and `LATEST` (the trunk check). It gains three lines, all machine-filled from fields the card already has or the fold writes:
```
TASK <id> [lane, size, worker ~N turns, prio]: <title>          <- as today
Goal / Scope in|out / 1. 2. steps / Tests / Done when / Close     <- as today
STATE READY | ACTIVE@host | SHIPPED@sha | STALE:<why>              <- as today; SHIPPED/STALE = `next` hides it, `brief` prints STOP first
Read first: <path[:lines]>, ... (max 8)                           <- NEW, from card.context.reads (the fold, section 4)
Ruled out: <LATEST decision lines + `tried` notes>                 <- NEW, from fields latest[kind=decision] and note
Traps: <card note HOLD lines> + the role file's 3 standing traps   <- NEW, from note; role traps come with the role_loader injection
First commands: sync.py start <id>; sync.py claim "<id>"; <card.commands[0]>   <- NEW, from commands
```
Guides the reasoning in this order: what is true on trunk now (STATE) -> what to read (Read first) -> what not to retry (Ruled out) -> what breaks (Traps) -> first command. The whole brief stays under the 30-line cap (`tasks.py check` rule 5).

Real example, card `tc4-desk-done-once` as the next brief would render it (fold data taken from the two sessions that touched desk.py in NEXT_SESSION.md and SUPERVISOR_C.md):
```
TASK tc4-desk-done-once [SONNET, size M, session ~15 turns, prio 2]: desk.py done/take refuse a row already closed on trunk
STOP: STATE SHIPPED@fb6479e15 (f787c15f 2026-10-23, traffic.py measure 72h: 0 duplicates). Nothing to build; `tasks.py done` if the card is still open.
Read first: scripts/dev/desk.py:126-150, scripts/dev/lease.py (_write CAS), MyTradingSys/tests/test_desk.py, MyTradingSys/system/TRAFFIC_CONTROLLER.md
Ruled out: a second lease (stops two Pipeliners, not a Pipeliner and a desk writer; 4a6b8562)
Traps: two clones must close the row in the same second for the test to be red on old code; sync.py refuses a second ship from one tree within 10 min (--again)
First commands: python scripts/dev/sync.py start tc4-desk-done-once; python scripts/dev/sync.py claim "tc4-desk-done-once" --area scripts/dev/desk.py; python -m pytest MyTradingSys/tests/test_desk.py -q
```
Today NEXT_SESSION.md still sends a worker to build this. With the STOP line the worker spends one turn, not a session.

### 3b. Coordinator -> fresh coordinator: `handover/SUPERVISOR_<L>.md`, fixed form, rewrite only
`supervisor.py handover` already writes this file from the last `plan`. It becomes the only coordinator handover, in 7 fixed sections, 60 lines / 6 KB cap, rewritten whole at every transit (an `## Update` heading fails `handover`). Every Truth line carries its own check so the next boot can re-run it:
```
# Supervisor <L> handover | written <utc> by <session> | verify: python scripts/dev/supervisor.py handover --verify   (STALE n at last boot)
## Goal        2 lines: the run, its window, its stop conditions (D6)
## Truth       <= 15 lines, each `claim | check | result@write`: shas (`git merge-base --is-ancestor <sha> origin/fast-track`), counts (`tasks.py list | grep -c ready`), running workers (`list_sessions linked`)
## Ruled out   <= 6 lines: what was tried and why it is closed (so the successor does not retry it)
## Next 3 steps  commands, in order; step 1 is runnable on a cold start
## Traps       <= 6 lines: what broke this run and the cheap avoidance (one ship at a time; EXTRA registration forces the 20 min gate; ...)
## Open        <= 5 lines: waiting on whom / what, with the id to poll
## Missed last time   machine-written by the fold (section 4): files the previous coordinator read before its first edit that this file never named
```
Filled example from pilot 2 (real facts from SUPERVISOR_C.md, rewritten into the form): `context_files/EXAMPLE_SUPERVISOR_C.md` (41 lines; the original is 82 and superseded itself three times).

Rotation (replaces compaction and the long-lived session): a coordinator is one wave long: it stops itself when every worker has shipped or at 3 h, whichever first; it writes the file, ships it (docs-only, ~11 s), replies with the start line `You are Supervisor. Login <L>.` and marks itself completed. The next coordinator is started by the operator's paste or by the Doctor on an operator turn (the app refuses `start_session` on event turns, and `clear_session` is refused while work is live: pilot 2, 3 refusals). Default (OURS): no self-restart is attempted; between waves nothing runs anyway (no schedulers). Auto-compaction stays the safety net; with this file complete, a compaction loses nothing (SUPER_SESSION D5). The 454 rewrites came from wakes after >1 h gaps with 200K+ of warm context; a 3 h wave with a 150K context cap (`plan` prints `TRANSIT` at 150K or 3 h) removes most of them.

## 4. Healing inside the run: the fold
Who: a hook, not the model. When: at `sync.py ship`, once per session, inside the ship (so the fold travels with the ship to trunk and the next session in the run reads it from trunk). How:
1. `preship.py hook-commit` (PreToolUse on Bash, already runs on `git commit`) also matches `sync.py ship`. The hook payload carries `transcript_path` and `session_id` (shot.py and mts_signal.py already read them).
2. It calls `context_gap.py fold --transcript <path> --tree <cwd>`: parse the jsonl; take the tool calls before the first Edit/Write (or first `git commit`) to a repo path; collect the files they read (Read; Bash `cat|head|sed -n|git show`); drop paths named in the first user prompt (the brief plus the injected role file), paths not on origin/fast-track, scratchpad and tool-result paths; keep at most 8, most-read first.
3. Target: the card this tree claimed (`sync.py where` claim slug = card id, else the first card id found in the first prompt) -> `card.context = {reads: [...], misses: n, calls_to_edit: n, folded: utc, session: id}` (replace, never append). No card (a coordinator tree) -> rewrite the `## Missed last time` section of `handover/SUPERVISOR_<L>.md`. Neither -> write nothing; `measure` counts the session as `unfolded`.
4. Stale facts: not a model judgement. `tasks.py next/take` hide `STATE SHIPPED|STALE` cards (brief prints the STOP line); `supervisor.py handover --verify` (run by `plan` at boot) re-runs every `check` in Truth and prefixes a failed line with `STALE`; the count goes in the header and the measure.
5. The next session reads the folded file from trunk: a worker through `tasks.py brief`, a coordinator through `plan` (which prints the file). The healing loop closes without anyone remembering to write anything.
Cost: one jsonl parse (<50 MB, <2 s) once per session, inside a hook that already has a 180 s timeout. Nothing runs between sessions.

## 5. The measure is the gate
`python scripts/dev/context_gap.py measure [--hours N | --since <utc>] [--gate]` (card C1 merges health24.py + `context_files/coldstart_baseline.py`). Per main-thread session with 5+ turns started in the window: `base` (first-turn context), `calls_to_edit`, `ctx_at_edit`, `unnamed_reads` (misses), `stale` (cards dispatched with STATE SHIPPED/STALE + `--verify` STALE lines), `rewrites` (turn with cache-write > 50% of a 50K+ context), `folded` yes/no. It appends one row per run to `research/mts_doctor/context_gap_runs.jsonl` and prints the table.

| Metric (per run, all worker + coordinator sessions) | Baseline 2026-10-25 | Pilot 3 must reach | Run over run |
|---|---|---|---|
| Tool calls to the first edit | median 12, p90 29 | median <= 8, p90 <= 15 | never rises |
| Unnamed reads (misses) | median 2.5, p90 13 | median 0, p90 <= 2 | never rises |
| Context at the first edit | median 95K | median <= 85K (base 71K + 14K) | never rises |
| Stale cards dispatched / STALE truth lines | 10 of 28 cards (36%); NEXT_SESSION block 2 stale | 0 | 0 |
| Full cache rewrites per session | 18.2 (454 / 25); 10-24: 0.94 | <= 1 | never rises |
| Sessions folded | 0 (no fold exists) | 100% of sessions that shipped | 100% |

Pass/fail test the next pilot runs: `python scripts/dev/context_gap.py measure --since <pilot start utc> --gate` exits 0 only when every "must reach" cell holds and no metric is above the previous row of `context_gap_runs.jsonl`; it prints each metric with PASS/FAIL. The Doctor pastes the table into the pilot report. First-turn base is reported, not gated (not ours).

## 6. Simple, certain, no new layer
Uses only what exists: `tasks.py brief/next/tag` (cards and STATE), `preship.py hook-commit` (the hook seam), `supervisor.py plan/handover` (the coordinator file), `sync.py ship` (the moment of truth), the transcript jsonl the app already writes. No new doc, no new rule for the model, no extra step in any brief.

REMOVES:
- NEXT_SESSION.md as a hand-written handover (119 lines, 15 blocks, 3 flagged STALE by STATUS, one sending a worker to shipped work) -> a 5-line pointer: "workers: `tasks.py next`; coordinators: `handover/SUPERVISOR_<L>.md`". `relay.py lint/handoff` and `handoff_lint.py` retire with it; STATUS.md drops its "Hand-over freshness" block.
- CLAUDE.md step 4 "Overwrite NEXT_SESSION.md" for workers; SUPER_SESSION "End" loses "partial work written into NEXT_SESSION.md" (partial work = card.note via `tasks.py tried`).
- The operator's `/compact` as the rotation step (pilot 2 row 7 FAIL) and the 24 h coordinator (D5/D6 "up to 24 h" -> one wave, <= 3 h).
- `## Update` sections in handover files (the form refuses them); "Session log" lines in SUPER_SESSION.md (the handover file's Traps carry the lesson; one line per run is kept by `context_gap_runs.jsonl`).
Adds no gate the model must pass: the hook writes, the measure reads.

## 7. Failure modes and the cheap guard
| Failure | Guard |
|---|---|
| The file grows without limit | card.context replaced, not appended, reads <= 8; handover 60 lines / 6 KB, 7 fixed headings, `handover` refuses anything else |
| Stale truth | every Truth line has a check; `--verify` at boot marks STALE; `next` hides SHIPPED/STALE cards; a brief opens with STOP when the work is on trunk |
| A worker skips the log | there is no log to skip: the fold is a hook on ship. Hook failure (no transcript, no card) ships anyway and shows as `unfolded` in the measure |
| The fold learns noise (a wild-goose chase) | only reads before the first edit, only paths on trunk, cap 8, most-read first; a path read by one session and never again drops out at the next fold (replace semantics) |
| Wrong "first edit" (a notes commit before the real work) | first Edit/Write under the repo excluding `handover/` and scratchpad; stated in `measure --help`; the metric is a median, one misread does not move it |
| Hook cost or hang | runs only on the `sync.py ship` command, one parse, `timeout 30` inside the existing 180 s hook budget; on timeout it writes nothing |
| Coordinator cannot be restarted unattended | by design: the wave ends, the file is on trunk, the start line is one paste; auto-compaction stays on as the fallback and the file makes it lossless |
| Two sessions fold into one card | the claim is the lock (one active claim per card); a fold on an unclaimed card writes nothing |

## 8. Build plan (cards, raw until the operator approves; all Sonnet; est. 1.5% weekly in total, OURS from pilot 2's 0.3% per card)
| Card | Owns | est_turns / worker | Done when |
|---|---|---|---|
| C1 `context-gap-measure` | `scripts/dev/context_gap.py measure`, `test_context_gap.py` (fixture jsonl), `research/mts_doctor/context_gap_runs.jsonl` | 15 / agent | the 6 metrics print for the last 24 h and match the baseline row above within rounding; `--gate` exits 1 on a fixture where misses rose; baseline row committed |
| C2 `context-gap-fold-on-ship` | `preship.py` (match `sync.py ship`), `context_gap.py fold`, `tasks.py brief` (Read first / Ruled out / Traps / First commands lines), card schema `context` | 20 / session | fixture transcript + card: after `fold` the card carries `context.reads` (<= 8, trunk paths only) and `brief` prints them; test red before; one real ship folds a real card |
| C3 `tasks-next-hides-shipped-stale` | `tasks.py next/take/brief` | 10 / agent | a card with STATE SHIPPED or STALE is absent from `next`, refused by `take`, and `brief` opens with the STOP line; test red on old tasks.py; `tc4-desk-done-once` is the live check |
| C4 `supervisor-handover-fixed-form` | `supervisor.py handover` (7 sections, caps, refuse `## Update`), `handover --verify` (STALE count), `plan` prints TRANSIT at 150K context or 3 h, fold target when no card | 20 / session | `handover` writes the 7-section file from a fixture plan and refuses a 61-line or `## Update` file; `--verify` marks a sha not on trunk STALE; `EXAMPLE_SUPERVISOR_C.md` passes `--verify` shape check |
| C5 `next-session-retire` (after C2-C4 ran one pilot) | NEXT_SESSION.md -> 5-line pointer, `relay.py lint/handoff` + `handoff_lint.py` removed, CLAUDE.md step 3-4 words, `make_status.py` drops Hand-over freshness, SUPER_SESSION End/D5 lines | 8 / agent | `git grep -l NEXT_SESSION` lists only the pointer and history; STATUS.md has no Hand-over freshness block; smoke gate green |

Order: C1 first (the baseline is taken before anything changes), C3 same day (it alone stops the redo of shipped work), then C2 and C4 (one editor each: tasks.py vs supervisor.py), C5 after pilot 3 passes the gate. Pilot 3 (REPORT_pilots: Haiku on mechanical cards, after 12+ ready cards and the registration-gate fix) runs with C1-C4 on trunk and reports the section 5 table.

## 10. The Lead (operator addition via MTS_Doctor, 2026-10-25): one session to talk to
The operator wants one session: it discusses and designs a task with him (pros and cons), sends it to refinement at once, then into a super session. Roles stay minimal: **Lead, workers, one independent Checker**. Thinker, Admin_Guy, Pipeliner and the Doctor's judgement duties fold into the Lead; Builder, Session_Planner, Eagle_Eyes and the wave coordinator (today's Supervisor) are worker kinds the Lead starts; Lab_Guy plus the diff-only review Agent become the Checker (never the producer, reads only the diff or the result).

### 10a. The Lead's context file: `handover/LEAD.md` (Thinker kind: vision and state, never code)
Fixed form, 80 lines / 8 KB, rewrite only, same fold and `--verify` as 3b (`supervisor.py handover --kind lead`):
```
# Lead handover | written <utc> by <session> | discussions since last rotation: n | verify: supervisor.py handover --verify --kind lead
## Vision          3 lines + pointer (PROJECT_VISION.md): what MTS is for, what decides what trades (fee-net OOS), what is banned (mainnet, schedulers)
## Priorities now  <= 5, ranked, each with the number it moves and the card or wave that carries it
## Decisions       last 10, `d-<slug> | date | one line` (full text in OPERATOR_DECISIONS.md); decisions older than 10 live only there
## Open questions  <= 6, each with its default and who answers (operator / a run / a Checker)
## Board           machine lines: ready/raw/active cards (`tasks.py list` counts), waves running (`list_sessions linked`), last ship sha, CI, budget per login
## Ruled out       <= 8: options weighed and closed, with the reason (so the next Lead does not reopen them with the operator)
## Discussions     since last rotation: title -> card ids -> refine status (one line each; the discussion text itself is NOT here)
## Missed last time   machine-written by the fold
```
The Lead never reads code: a question about code goes to a one-use read Agent (Sonnet or Haiku) whose brief ends "reply in 5 lines". The REFINE run shows the cost: a coordinator that worked this way used 1% weekly across 28 cards with no compaction. The measure adds `code_reads` per Lead session (Read/cat/sed of .py/.java/.ps1 paths in the Lead's own transcript): target 0.

### 10b. A discussion ends in output, then leaves the context
Every design discussion closes the same way, in one turn, before the next topic: (1) decision record appended to OPERATOR_DECISIONS.md (the operator's exact words, or `DECISION (OURS)` with the default); (2) one card per outcome (`tasks.py new` + `fill --note "OPERATOR QUOTE: ..."`), raw; (3) the refine request now: a Session_Planner Agent on the new cards, 5-line reply; (4) when cards come back ready and the operator said go, the Lead starts the wave (a Supervisor worker session, `start_session user_asked`, allowed because the operator is present); (5) one line in `## Discussions`. The discussion text is dropped from the Lead's context at rotation (10c), never earlier: a model cannot forget selectively, so "drop" means the next Lead starts from LEAD.md, which holds the outcome and not the talk.

### 10c. Lead -> fresh Lead: kind 2 handover, triggered by a measure, never by the clock
Rotate when either holds, checked by the Lead with `get_usage` after each closed discussion: context >= 150K tokens, or 3 discussions closed since the last rotation (OURS; pilot 2's /compact brought 232K -> 93K, so 150K keeps the rebuild under one cold start). Never mid-discussion: finish 10b first. Then: rewrite LEAD.md, docs-only ship, `clear_session` on itself (possible here: the Lead holds no live ship or worker, those run in worker sessions; pilot 2's refusals came from live work in the same session), the role_loader SessionStart hook re-injects `roles/lead.md`, the first turn reads LEAD.md from trunk. If the clear is refused, the Lead prints the one-line start prompt `You are Lead.` and stops. Measure for the gate: Lead sessions' context p90 <= 160K, rewrites per Lead session <= 1, `code_reads` 0, every closed discussion has its card ids in LEAD.md.

### 10d. Where I disagree, and why
1. The Lead must not also be the live wave coordinator. Pilot evidence: the one session that both talked with the operator and woke on worker events (the Doctor) carried 84% of all context and 454 cache rewrites, because event wakes after >1 h gaps re-send a 200K+ history at write price. So the wave runs in a Supervisor worker session the Lead starts; the Lead reads its 5-line reports on the operator's turns and never wakes on events. Same single session for the operator; the coordination cost moves to a short-lived worker.
2. Clock-free rotation is right, but "3 discussions" alone can hide a 300K context from one long topic: the context threshold stays as the second trigger.
3. Model: Opus when the operator names it (the Thinker rule), Sonnet otherwise; the Lead's file, not its model, is what makes it good from turn one.

### 10e. Cards added
| Card | Owns | est_turns / worker | Done when |
|---|---|---|---|
| C6 `lead-role-and-handover` | `roles/lead.md` (Thinker + Admin_Guy + Pipeliner + Doctor-judgement Jobs; old files become one-line pointers), ROSTER.json, `supervisor.py handover --kind lead` (8 sections, caps, `--verify`), fold target for a Lead tree, `context_gap.py measure` `code_reads` and discussions-per-rotation | 20 / session | `You are Lead.` loads the file with its banner; `handover --kind lead` writes the 8 sections from a fixture and refuses a 9th heading; `EXAMPLE_LEAD.md` passes the shape check; test red before |
| C7 `checker-role` | `roles/checker.md` = Lab_Guy stamp duties + the diff-only review Agent brief; the super session's rule 3 points at it | 10 / agent | review Agent and Lab_Guy pass both start `You are Checker.`; `role_loader.py check` green |
Example LEAD.md filled with today's real state: `context_files/EXAMPLE_LEAD.md`.

## 9. Defaults taken (no operator questions; change any by card note)
- The fold runs at ship, not at Stop (a Stop-time write would dirty a just-shipped tree and trip stop_guard).
- Reads before the first edit define a "miss"; reads after it are the work itself.
- A coordinator wave is 3 h / 150K context; the successor starts on an operator turn (no unattended self-restart).
- The measuring tool stays read-only on `~/.claude/projects` jsonl files; nothing is uploaded; session ids only in `context_gap_runs.jsonl`.
- Role files are not changed: their injected text already counts as "named" for the miss metric.
