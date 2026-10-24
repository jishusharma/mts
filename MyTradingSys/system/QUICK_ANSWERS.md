# QUICK ANSWERS

Reference that only some tasks need, moved out of CLAUDE.md on 2026-10-15 (CLAUDE.md is loaded on every turn; this file is read on demand).
The operator is not a developer: do these, do not ask, do not re-investigate. Hard rules and gates stay in CLAUDE.md.

## Operator page, pages, inbox
- Operator page = MTS Control Room (pinned artifact). Their questions/tasks arrive in its Inbox, verbatim; procedure `MyTradingSys/system/CONTROL_ROOM.md`. Ask the operator via a page decision, not chat.
- Session start (operator 2026-10-09): after `sync.py start`, read the Control Room Inbox/decisions (ArtifactData, CONTROL_ROOM.md) only if your task aligns; fetch full text of aligned items only.
- Pages follow builds (operator 2026-10-12): a session that shipped ends with `python scripts/dev/artifacts.py build`, then republishes the Control Room
  (and MTS Layers if layer_index.json or layer_map.json changed) over its url for this account (`artifacts.py plan --account <account>`). Blocked on the operator = a
  `decisions` doc on the page plus its entry in `system/OPERATOR_DECISIONS.md`, never only a chat line. What sessions did: `python scripts/dev/session_log.py`.

## Sessions, claims, task cards
- Same-page check on any Claude login, and before ending a session: `python scripts/dev/sync.py where` (this tree plus trees holding unshipped work; `where --all` lists every tree); commit + ship what is yours. `sync.py health` lists collisions (PARALLEL.md).
- Task cards (refinement stage: raw idea -> ready task, Definition of Ready, Backlog on the Control Room): `MyTradingSys/system/TASK_REFINEMENT.md`; `python scripts/dev/tasks.py next` before picking work, `tasks.py new` for follow-ups you find.
- Writing tasks into NEXT_SESSION.md: RELAY.md "Task list standard" (curated, one session each, `DONE when:`); check it with `python scripts/sched/relay.py lint --file MyTradingSys/system/NEXT_SESSION.md`; no dispatcher reads it, the coordinator does (SCHEDULING_POLICY.md).
- Surface fallback (operator 2026-10-08): only if a task truly cannot run in the Claude Code Win App (e.g. needs a process this App cannot reach) file a card (lane JIS-NB) or a desk row with the exact commands, why forced and the expected result, and say so in one line. Never stay silent.
- Archive backups/rejects with `python scripts/dev/declutter_backups.py --apply` (moves, never deletes).
- C: low or `%TEMP%` full: nothing to do by hand. The logon run (`c_drive_guard.py install`, once per station) and the SessionStart hook prune it; what each station cleans and why: `MyTradingSys/system/STATION_CLEANUP.md`.
- "What did study X lead to?" (its card, VERDICTS.csv row, pre-registration, follow-up cards, commits, LAYERS.md, open claim): `python scripts/dev/trace.py <study_dir | card id | layer id>`; one read-only call, report only (T043 stays WONTFIX).
- "Is this stat already in research_kit?" (Holm, day-clustered SE): `MyTradingSys/backtest/research_kit.py` (tests: `test_research_kit.py`); `python scripts/dev/research_kit_lint.py` lists scripts that re-implement it (new ones under NEW; known ones in `research_kit_lint_allow.tsv`); report only.

## Layers
- Layers (Tom, Fabio, RSI, CryptoCred, positioning, session, ...): ONE index per layer with spec, code, ledger, latest results, roadmap and open cards, for Claude and Codex sessions: `MyTradingSys/system/LAYERS.md` (pointers in `system/layer_index.json`; regenerate `python scripts/dev/make_layers_md.py`). Same commit: a new backtest is a row in `system/layer_map.json`, a new layer joins a family in `layer_index.json`, a layer card gets `tasks.py new ... --layer <family>` (gate step 3ly fails on a dead pointer or an unowned layer).
- Live state off the desktop (NUC, laptop): `sync.py start` pulls the read-only mirror; `python scripts/dev/live_mirror.py brief` before any live read; say `mirror@<utc>` when you quote it (LIVE_MIRROR.md).

## Push, CI/CD, deploy, machines
- Push: never from the live tree (the folder holding `.mts_live`). `sync.py ship` is the way. Cloud containers (claude.ai/code, harness branch `claude/...`): start from origin/fast-track, push the harness branch, open a PR into fast-track; CI auto-merges it when green (PARALLEL.md). `python scripts/dev/cloud_setup.py` installs the gate deps and prints the state. If sync.py itself is broken, the manual recipe is PARALLEL.md "Fallback if sync.py is broken".
- CI/CD without the operator: `.github/workflows/ci.yml` gates every push (ubuntu AND windows) and moves `green/fast-track`;
  `MTS-AutoDeploy` (RETIRED 2026-10-17, see SCHEDULING_POLICY.md; deploy by hand) deployed only that SHA, stops on red; `MTS-DailyHygiene` (RETIRED 2026-10-17) wrote the report STATUS.md embeds. Details,
  restart map, registration: `MyTradingSys/system/DEPLOY_RUNBOOK.md`. STATUS.md's `CI green:` line says RED when the tip has not
  gone green for an hour: then nothing deploys, and fixing CI is the first job of any session.
- Deploy to the live tree by hand only if that job is down: DEPLOY_RUNBOOK.md "Manual fallback" (operator pre-authorised "just do it" 2026-10-09).
- Machine off = stack down. `MTS-Supervisor` (RETIRED 2026-10-17, see SCHEDULING_POLICY.md) no longer revives processes; the coordinator or operator restarts them. Missed events are not replayed
  after an outage on purpose (no stale-signal trades); do not build catch-up.
- Runner output: `runtime_data/live_runner.log`. alert_rate_check candles: `scripts/dev/refresh_klines.py` runs daily before it.
- Local gate needs `pip install numpy` (Step 3p). Two `htf_context_live` loops = duplicate rows: keep one (shim parent + child = one loop).

## Codex, DSA
- "How is Codex doing?" = `python scripts/dev/codex_run.py status` (also in STATUS.md, "Layer Lab (Codex)"). Codex works lane `CODEX` cards
  on JIS-NUC (`codex_run.py tick`, run by the coordinator; MTS-CodexLab RETIRED 2026-10-17, see SCHEDULING_POLICY.md); how it works, its limits and how to feed it: `MyTradingSys/system/LAYER_LAB.md`.
  A NEEDS A LOOK line is a NUC session's first job. GPT out of credits/limit or silent: `python scripts/dev/lane_health.py status` (cards move to DSA/Claude or pause by themselves; flag a must-wait card `tasks.py flag <id> crucial`). Scoped research or backtest-code work goes to lane CODEX before a Claude session takes it.
- DSA delegation (operator 2026-10-09): run-and-report work (backtest reruns, stratifying, inventories, source hunts, gate runs) goes to DSA: `desk.py post "<t>" --need "<commands>" --done-when "<obs>" --target DSA`. Routing and operator guide: `MyTradingSys/system/DSA_DELEGATION.md`. Low on budget: post the rest to DSA, then hand off.

## Screenshots (the operator's charts and random images are evidence, not decoration)
- A hook saves every pasted image and prints `[SCREENSHOT INTAKE] ... SAVED` with ids; no notice = nothing new landed. On the notice: `python scripts/dev/shot.py classify <id> --kind ... --why "<operator's meaning>"`, read, `shot.py read`, `shot.py done`. Never leave a shot `new` at session end (`shot.py status`, also in STATUS.md).
- Charts of one moment are one set, read together; every claim is MATCH / MISMATCH / NOT_IN_DATA against files you read; file the last two. Process and per-surface rules: `MyTradingSys/methodology/screenshot_intake.md`. Project map (which group an item belongs to): `MyTradingSys/system/PROJECT_MAP.md`.

## Interview Prep notes
- "Note this for InterviewPrep" / a "teach me" answer: save it as a note in `MyTradingSys/learning/` with front matter `interview: yes` (topic, level, date); design in RUN_MODEL.md section 7.
- `python scripts/dev/interview_feed.py list` shows which notes may leave; `export --to <dir>` (or env MTS_INTERVIEW_DIR) copies them with an INDEX.md and skips any holding paths, secrets or runtime data.
- Jis decides when to push the exported folder to the Interview Prep project.

## Ask Gemini or GPT directly (no desk row)
`python scripts/dev/ask_model.py gemini|gpt "<prompt>" [--model flash|argon|sonnet|opus] [--effort low|medium|high] [--file PATH ...]` sends the prompt to the model and prints the answer (read-only, runs in a scratch folder under F:/MTS/ask, never a work tree). Gemini = Antigravity `agy` on the Google Pro login; GPT = Codex CLI on the lab login. Use it for questions, second opinions, frame reads. Work that must change the repo stays on cards (`gemini_queue.py`, `codex_run.py`). Quota error (429) means wait for the reset it prints; do not fall back to a desk row for a question.
