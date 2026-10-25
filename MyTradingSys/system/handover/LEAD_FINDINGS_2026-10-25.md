# Findings log, Lead session 2026-10-24/25 (MTS_Doctor as Lead). Each row: what happened, evidence, where it must land (card or doc)
Status: OPEN until the "lands in" cell names a shipped commit. Updated by the Lead as findings arrive.

| # | Finding | Evidence | Lands in |
|---|---|---|---|
| 1 | A coordinator ended its turn on one Bash call and idled (pilot 2, super-run-2h 23:09Z) | SUPERVISOR_C.md, super-run notes | rule in every brief: each wait = one background shell; heartbeat line 15 min. Card super-session-coordinator-stalls (needs SUPER_SESSION.md edit) |
| 2 | Ship via `| head` or a lost background shell never reaches trunk; second ship during first = duplicate-push reject | sim_build1, sim_build2 notes | ship recipe: ONE background shell to a file, no pipes, `git cherry` empty; add to PARALLEL.md |
| 3 | A results/*.json without a catalogue row broke CI (test_artifact), caused by the Lead's own smoke run, reverted `e0a985ca2` | CI run 40142444401 | fixed in build 2 (catalogue-safe saving, `67426492d`); doc note in sim_desk/ROADMAP.md |
| 4 | CI path filter skips json/md-only pushes, so a revert of such a push has no CI run; use `gh workflow run CI --ref fast-track` | ci.yml paths | PARALLEL.md one line |
| 5 | Sessions cannot be started from a system event/timer turn, only on an operator message; a card waits for his click | start_session refusal 00:5xZ and 10-25 pilot | design: coordinators that must spawn need an operator-typed start; unattended spawn = Agents only |
| 6 | Pilot 3 Haiku Agents were refused writes inside their own sync.py worktrees (12-14 tool calls, no edits); supervisor moved edits into its own worktree with explicit-path commits | PILOT3 supervisor note | OPEN cause; Haiku Agent needs cwd = its worktree or an allowed-dir grant; record in PILOT3_RESULTS.md |
| 7 | Sessions may not delete their own scratch files (rm and Remove-Item denied), so the Stop guard keeps flagging them | pilot supervisor, Lead | scratch files go to the scratchpad dir, never the worktree; add to WORKERS.md brief template |
| 8 | "Pages follow builds" (operator 2026-10-12) is prose in QUICK_ANSWERS.md; only a WARNING at ship; no brief, super-run, pilot or Lead step names it; MTS Home stale (3 pages lag) | artifacts.py stale; ship output | card pages-follow-builds-make-the-republish-s (p1): run-end step in SUPER_SESSION End, Lead wrap, pilot template; stale gate; owner Artifacts_Guy (login jishusharma1985 = C) |
| 9 | Haiku "agents" have no session of their own, so context/turn numbers per worker are not readable the way PILOT3 wanted | PILOT3 supervisor note | PILOT3_RESULTS.md: ask agents to report tokens; Pilot 3b with Haiku sessions started on an operator message |
| 10 | Context-files changes (card+fixed-form handover, fold-on-ship hook, context_gap.py) are design only, not on trunk; not applied to Haiku | impact map: C1 NOT_FOUND | cards C1-C7; Pilot 3 is the no-change baseline |
| 11 | JIS-NB CPU: Program Compatibility Assistant service 13% while sessions spawn many processes | operator Task Manager 10-25 | Admin_Guy child, research/admin/PCA_CPU_2026-10-25.md |
| 12 | No single "layer integration guidelines" file; stitched from 6 docs; no layer ahead; 94% live exits are time exits | LAYER_REALITY_2026-10-25.md | one LAYER_INTEGRATION.md card (not yet filed) |
