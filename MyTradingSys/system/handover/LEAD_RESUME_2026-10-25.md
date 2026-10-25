# Lead resume, 2026-10-25 (written by the outgoing Lead session, role MTS_Doctor token gulf-otter; operator asked for a fresh session so no session runs long)
State comes from disk and git this turn, not from this note. Read first: STATUS.md, ACTIVE entries of ANNOUNCEMENTS.md, `handover/LEAD_FINDINGS_2026-10-25.md`, `research/mts_doctor/PILOT_IMPROVEMENTS_AUDIT_2026-10-25.md`, `research/mts_doctor/LAYER_REALITY_2026-10-25.md`, `research/lenovo_start/LENOVO_START_2026-10-25.md`.

## How the operator works (keep)
Answer every operator message in order, plain words, no jargon, no paperwork gates, ask only when blocked. Commands for him start with `cd <full path>;` (his admin shell opens in system32). He is the only one who clicks app switches and runs elevated scripts. Voice dictation mishears: guess from context.

## Budget (operator 2026-10-25)
5-hour window hard cap 80% (read `get_usage`): at 80% let running work finish, start nothing new, spend the rest only on critical tasks until the reset, then free again for 4-5 h. Weekly about 70% (own stop 67%). At hand-over: 5 h window 70%, weekly 52%, reset 2026-10-25T10:20Z. Helper sessions at medium effort, Remote Control off, archive each one when its branch is on trunk.

## Corrections learned today (rules for this session)
1. Ship = ONE background shell writing to a file, no pipes; add `--again` for a second ship within 10 min (without it the ship refuses at once); one ship at a time per machine. Claim "shipped" only after `git cherry origin/fast-track <branch>` shows no `+` lines; a child's note is not proof.
2. Before killing a process identify its owner (parent chain, `--again`, start time) and read your own ship log first. Today a working ship of another session was killed because the refused one of ours was mistaken for it.
3. handover/*.md is NOT exempt from `tests/docs/test_integrity.py::test_2_no_forbidden_refs` (read the word list there); CI skips md/json-only pushes, so that red only shows in the local gate and blocks every later code ship. A new results/*.json needs its catalogue row.
4. Scratch files go to the scratchpad directory, never the worktree or repo root (rm is denied; ship logs hold host data; the repo is public). Use absolute paths; the shell keeps its cwd; `git merge` in a worktree is denied, use `sync.py start` or let the ship merge.
5. Sessions: `start_session` is refused on turns started by an automated event; it works on operator-typed turns. Opus only when the operator names it: standby prompt, `set_session_model claude-opus-5-5`, read back with `get_session`, then send the task.
6. Ultracode workflows are for live-path ships only. Today two workflows spent 12.9 M subagent tokens (about 20 points of the 5 h window) to find 2 real bugs and a backlog; docs and extracts need the verifier plus one Sonnet read.
7. Write prompt files for the NUC without a BOM (`[System.IO.File]::WriteAllText(path, text, (New-Object System.Text.UTF8Encoding($false)))`); `Set-Content -Encoding UTF8` in Windows PowerShell adds one and cburn crashed on it. Check the runner log for START and EXIT lines before relaying.
8. Host health in the ship log suggests `taskkill` on `explorer.exe`: that is the Windows shell, never run it.

## Open items, in order
A. CI runs on the K1 and Krown merge commits (e652aff98, 43d3de90c) were still running: if red, `git revert` and ship within 10 min.
B. Archive CBP (`local_f73a789e-656b-41e3-955c-4138e92db50d`) and super-run (`local_fde1f189-d4d5-4cf0-8994-08efff6d852e`) once idle.
C. Operator-side, waiting on him: Defender exclusions (`cd` to the worktree, run `scripts\operator\defender_exclusions.ps1` elevated; `-Check` showed 4 missing); the two Lenovo steps in `LENOVO_SETUP.md` steps 7-8 (dry run, then `mts_run.py loop --hours 10 --login A`). When he reports, verify a claim and ship from desktop-f7iu69n under login A on the signal branch.
D. Card `t09-malkan-exit-cc-wide-stop` (live path, lane JIS-NB): Session_Planner refines it; two confirmed T09 gaps (malkan 1h has no exit-table entry; cc 1h stops wider than the 2% size cap are refused by the executor).
E. Cheap audit items (one docs-only Haiku or Sonnet session at medium effort, operator asked, not started): close shipped cards (P95), PARALLEL.md line on reverting md/json-only pushes (P122), scratch-file rule in the worker brief (P123), pages-follow-builds run-end step with stale gate (P124), LAYER_INTEGRATION.md card (P127), raw cards C1-C7 for the context-files design (P118), CI note in PILOT3_RESULTS (P129), card for the explorer.exe false alarm in host health.
F. Findings still OPEN in `LEAD_FINDINGS_2026-10-25.md`: 1 (coordinator stall, SUPER_SESSION edit), 2/4/7 (ship recipe, CI dispatch, scratch rule), 6 (cause of Haiku agents refused writes in worktrees), 8 (pages), 12 (layer integration file). Update each row's "lands in" when shipped.
G. Not run: Pilot 3b (Haiku sessions started by the Lead on a typed turn), Pilot 4 (ultracode vs Sonnet), Pilot 5 (three logins). The CCU video (youtube DXntdN3jfTg) is unchecked: Claude fetches get 429, all YouTube work goes to Gemini on the NUC (`gburn.py`); no result yet.
H. Operator decisions still open: C1-C7 build order (K1 role-loader mode shipped), Lead ssh/machine rule, DEV window before 2022 (Krown pre-reg uses 2017+, desk lock is 2022-04..2024-06), volume_fvg off on testnet at next deploy, Lead model default Sonnet, broadcast acks b-2a5b44 and b-10b3d8.

## Mainnet is far: what the Thinker session weighs (do not build here)
Facts read today: no layer has a positive fee-net out-of-sample result (LAYER_REALITY); `promoted_setups.json` ships empty (PROMOTION_PIPELINE.md:3); 94% of live exits are time exits and the live 1%/2%/8-bar bracket was never backtested; the go-live bar for real money (T086) is still OPEN with no signed criteria; live host move not cut over (LIVE_HOST_MOVE.md); repo public until mainnet or the first fee-net OOS pass.
