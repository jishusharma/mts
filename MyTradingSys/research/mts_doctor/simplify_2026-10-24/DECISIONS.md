# Decisions from the operator chat, 2026-10-24 (MTS_Doctor session gulf-otter)

Every point the operator raised, what was decided, and where it lives. Owner = who carries it out. The simplification
session (`simplify-tooling`) works from BRIEF.md plus this file.

| # | Point | Decision | Where it lives | Owner | State |
|---|---|---|---|---|---|
| 1 | Too much tooling, too many bugs | Freeze new tooling; deletions, one-line fixes and reverts allowed; trading code unaffected | ANNOUNCEMENTS A-20261024-1 | all sessions | in force |
| 2 | Ship takes 16-22 min | Goal: a non-live-path ship passes locally in under 2 min, measured | BRIEF "Done when" | simplify-tooling | open |
| 3 | 66 steps on every ship | Local ship runs only the tests of the changed code; all 66 steps run in CI (15 shards); local `--full` only for live-path files (gate_select FULL_RE) | BRIEF 3.1-3.2 | simplify-tooling | open |
| 4 | Step 66 fails, all rerun | Short local gate makes a rerun cheap; in CI rerun only the failed job (`gh run rerun <id> --failed`), never the whole run | this file | all sessions | open |
| 5 | Smoke gate ignores its budget | Direct tests inside the budget, estimates from measured timing, tests >= 30 s go to CI only | cards `gate-impact-direct-obeys-budget`, `soak-six-slots-smoke-cap` | simplify-tooling | open |
| 6 | Ships queue behind each other | 2 gate slots per machine, wait has no limit; two gates side by side pushed tests past the 240 s cap. Fix: no-op/failed ship does not start the 10-min clock (sync.py:524); measure two ships in a row | message to simplify-tooling | simplify-tooling | open |
| 7 | CI red | Any session that sees red reverts the breaking commit within 10 min, whoever wrote it, then cards the author's lane; no forward patching | card `red-trunk-revert-10-min` (raw) | Session_Planner refines | open |
| 8 | Codex/GPT and Gemini ship directly | Keep direct ships (no rework, lower cost); rule 7 covers breakage | operator 2026-10-24 | - | decided |
| 9 | Same rules for Claude, Codex, Gemini | One rule text that CLAUDE.md, AGENTS.md, CODEX_START.md, GEMINI_START.md point to (a merge of duplicates, so a deletion) | card `red-trunk-revert-10-min` goal | Session_Planner, then simplify-tooling | open |
| 10 | Which hooks are really needed | Keep stop_guard, ci_watch, c_drive_guard, role_loader (shrink), trunk_lag (fix); remove turn_meter, model_guard, offer_guard, prereq_guard; preship stays until its catches are counted | BRIEF 3.5-3.7 | simplify-tooling | open |
| 11 | trunk_lag says "88 behind" on a tree equal to trunk | Fix or reduce to one check per session | BRIEF 3.6 | simplify-tooling | open |
| 12 | Clutter | Delete doc-only scripts after an import-graph check; multi-device machinery only on operator's word | BRIEF 3.8-3.9 | simplify-tooling; item 9 operator | open |
| 13 | Is the work double-checked | Deletion list ships first; MTS_Doctor audits it with a fresh agent (import graph, settings.json, CI shard list); only cleared rows are deleted; every removal ship quotes measured seconds/ms; Doctor checks `git cherry` and numbers after each | message to simplify-tooling | MTS_Doctor | open |
| 14 | Two sessions editing one file | One editor per central file (run_all_tests, run_extra_tests, sync, tasks, supervisor.md); at most 2 working sessions at once | BRIEF 3.11 | coordinator | open |
| 15 | Test vs live environment | Already exists: worktrees = test, `.mts_live` on testnet = live, deploy only from `green/fast-track`; nothing new needed | DEPLOY_RUNBOOK.md | - | decided |
| 16 | One super session / big rewrite | No: one simplification session, small removal ships | BRIEF section 5 | - | decided |
| 17 | Fast mode, ultracode, Fable | Fast mode = same model, faster output; none of these shorten the gate. Model per session is the operator's pick | this file | operator | decided |
| 18 | Non-hermetic tests (16 of 110 fixes) | CI on a second OS catches them; rule 7 reverts them; no new lint (freeze) | BRIEF caveat | - | decided |
| 19 | Trading focus (notebook, CBP) | Continues; freeze does not apply to trading code | ANNOUNCEMENTS A-20261024-1 | trading sessions | in force |

Decided by default by MTS_Doctor (operator delegated, 2026-10-24 about 03:00 IST: "decide on all the recommended decisions by yourself"); operator may revise:

| # | Point | Decision | Why |
|---|---|---|---|
| 20 | Skip 5b/4f locally | No: live-path ships keep them locally; 3k, 4, 3dk, 3ad, 3bk run in CI only | gate_select.py:37 FULL_RE matches layers *live*/*writer* files that 5b/4f test |
| 21 | Delete soak_six_slots | Keep; its test runs in CI only (TEST_FILE_SECONDS 150) | trading/supervisor check per inv_research_needs; the time cost is gone without deleting |
| 22 | Multi-device machinery (BRIEF item 9) | Keep, untouched; 3sig, 3lh stay | NB, NUC and desktop all ship to trunk this week |
| 23 | trunk_lag false "N behind" | Fix: read the session's cwd from the hook payload | trunk_lag.py:73 uses os.getcwd() = main checkout (93 behind) while the session tree was 2 behind |
| 24 | Super-session design questions | Design session settles each with its recommended option, ships SUPER_SESSION.md; only Opus-without-naming (WORKERS.md rule 6) stays PROPOSED | operator asleep; hard rules unchanged |

Carried over from before this chat (not part of the simplification):
- Option A: A1, A2 shipped 2026-10-24 (full gate 16 min, `git cherry` empty). A3 (drop ask signals) waits for its turn; A2 agreement fix for its 4 open cases; Lab_Guy re-stamps the 6 dsa-audit cards.
