# 48h failure review: merged (Opus + Sonnet + Haiku + web research), 2026-10-23

Inputs: `2026-10-23_operator_asks_48h.md` (46 rows), `_failure_review_{opus,sonnet,haiku}.md`,
`_web_research_anthropic.md`, `_web_research_community.md`. Every fix below is a proposal with its test until a Builder ships it.

## Ranked root causes

| # | Root cause | Found by | Rows | Fix | Test |
|---|---|---|---|---|---|
| 1 | The approval card is drawn by the desktop app, not our hooks. It appears on a first turn that is a pasted brief, after compaction, on event turns; Remote Control refuses. Every hook/rule fix (8fd2c71ac, 3edcc612d, 96784f370) could not remove it. | all 3 + docs (NOT_DOCUMENTED) | 1,3,4,5,18,19,38,41,46 | Stop promising "no click". Starts only from an operator-typed turn; anything else = background Agent. One live test: Bypass mode + "Always allow" on start_session once. Allow-list alone: weak (sessions already in bypass still waited). | Timed start_session on a typed turn, bypass on: returns <15 s, no card |
| 2 | model_guard refuses starts/messages the app would allow; 4 rule files disagree on session vs Agent | Opus, Haiku | 2,3,4,5,46 | One rule source (supervisor.md); model_guard reads it; allow SendMessage to own Agents | Guard unit test: typed-turn start + own-Agent SendMessage allowed |
| 3 | turn_meter does not recognise the Supervisor: first message starts with the worktree notice / pasted wrapper, `turn_meter.py:195` matches only a leading "You are Supervisor" -> 49 false "unattended" stops; exemption 34fe4a420 never fires | Opus | 3,5,11,12,16,17,31,41 | Search the role line anywhere in the first user message after stripping system-reminder / pasted wrappers | Feed the real captured first message: exempt=True (fails on old code) |
| 4 | role_loader scans 300 chars; the role line in a started session sits at char 644 behind a system-reminder -> ROLE NOT LOADED | Sonnet | 3,4,5 | Same wrapper-strip helper as #3, shared | Real captured prompt -> Eagle_Eyes loaded |
| 5 | Main checkout (where hooks run, per docs) never fast-forwards: `trunk_lag.py:86` skips any tree with tracked edits; it always has runtime CSV deletes + SUPERVISOR_LOG | all 3 + docs | 1,18,25,26,5 | Untrack runtime files (.gitignore + git rm --cached), then the fast-forward runs; or user-scope hooks pointing at a copy outside the tree (community #83953) | After fix: main checkout `git rev-list --count HEAD..origin/fast-track` = 0 after a ship |
| 6 | "Done/started" claimed from launch, not read-back (Gemini 10 s after Start-Process, robocopy exit 16, A1/A2 not on trunk, CBP SKILL.md left) | Sonnet, Haiku, Opus | 9,22,30,31,32,33,39,43 | Launchers verify the job ran (pid alive + output after N s) before printing started; "shipped" only from `git cherry` empty | Launcher test with missing exe -> FAILED, not started |
| 7 | 15 MTS-* Windows scheduled tasks enabled on JIS-NB (policy: none); MTS-Audit-Rotation 13 h, 38,540 CPU-s -> ship timeouts | Opus (+ ship's STRAY PID 21716 warning) | 6,9,30,31 | Disable after checking which watch the live system (operator/coordinator decision) | `schtasks /query` shows 0 enabled MTS-* |
| 8 | Ship/CI claimed before the gate finished; CI path filter skips `MyTradingSys/system/**`; green quoted for the wrong sha | all 3 | 16,18,22,25,26 | CI includes system/**; green claimed only for the shipped sha from `origin/green/fast-track` | 3edcc612d-type change triggers the role-budget test in CI |
| 9 | Supervisor handed over while async work (CBP Workflow) still ran; results never recorded | Sonnet, Haiku | 6,11,12,13 | Handover refuses while own background jobs run | handover with a live job -> refuses |

## Table corrections
Row 15, 21: answered (21 via wrap_up recap). Row 20: tried and dropped after A/B (9e9d9ed63), operator never told. Rows 26, 46: FAILED, not HELD.

## Web research, the parts that change the plan
- Worktree sessions load settings and hooks from the main checkout (docs). That makes #5 the reason every hook fix lagged.
- Hooks block only with exit 2 or JSON deny (docs).
- Cross-session wake needs `crossSessionInbound: "accept"` in user settings; held messages are dropped after 5 min (docs) -> row 2.
- Resumed background agents lose a pinned model (#75054): respawn with explicit model.
- No issue or doc covers the start_session card; treat as app UI until the live test says otherwise.

## Fix order
1. Builder: #3 + #4 (shared wrapper-strip helper, tests from real captured prompts). Started 2026-10-23.
2. Builder: #5 (untrack runtime files in main checkout) and #8 (CI path filter).
3. Operator/coordinator: #7 scheduled tasks (some may watch the live system); `crossSessionInbound` user setting.
4. One timed live test for #1 on a typed turn; result decides whether the "no click" promise is ever made again.
5. #2, #6, #9 after 1-2 land.
