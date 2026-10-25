# LOGIN PLAN, 2026-10-26 (Supervisor A, from the Lead's operator orders)

Source of truth for cards is `python scripts/dev/tasks.py next` / `check <id>` (a card here that is no longer `ready` is skipped).
A station is one device plus one login. Logins may move between devices; the start lines name the login, never the device.
Read budgets with `get_usage` (A, B, C); the numbers below are 2026-10-26 ~19:10 IST readings and go stale in 6 h.

## Budget rules (operator, 2026-10-26)
- **Login A**: weekly cap 80% until the end of Monday 2026-10-26 (week was 61% at the reading; about 19 points to spend), then only the most important work; Tuesday uses the last 20% (reset 2026-10-27T20:00Z). Fable quota counts. The Supervisor reads `get_usage` before each wave and stops launching A Builders at 80%.
- **Login B** (NUC, fresh week): run FULL sessions and exhaust the week in time.
- **Login C** (desktop, jishusharma1985; week 21% at the last reading): run FULL sessions and exhaust the week in time.
- Hand-over rule: one task per session; hand over when done (NEXT_SESSION.md + `sync.py ship`); the watcher hands over every 3 to 4 hours. A Builder's final report starts with its role banner, then `Result:` and the sha.
- Never discard, demote or park a layer (operator NO, 2026-10-25). Testnet only; no live-tree changes.

## Queues (ordered; claim each with `sync.py claim`, ship each with `sync.py ship --release <slug>`)

### A desktop (Supervisor A starts Sonnet Builder Agents here; stop at 80%)
1. quota-source-numbers-bug (p1 S)
2. pages-follow-builds-make-the-republish-s (p1 S)
3. station-tidy-sync-py-where-all-at-sessio (p1 S)
4. gate-test-lease-timeout-under-load (p2 S; the gate flake that cost sim-v2 two ships)
5. sim-dashboard-v1 (p1 M, only after the sim-v2 Builder has landed)
Start line when a desktop session is wanted instead of an Agent:
`You are Builder. Login A. Tasks: quota-source-numbers-bug, pages-follow-builds-make-the-republish-s. Boot: python scripts/dev/sync.py start <slug>; work only in the printed WORKTREE. One task per session, then hand over.`

### A laptop (no F: drive; Claude Builder, started by the operator)
1. ci-red-one-wording (p2 S)
2. mid-turn-image-intake-gap (p3 S)
3. auto-compact-at-25-for-all-sessions-clau (p1 S)
4. hook-reminder-get-usage-before-after-age (p2 S)
5. habib-holdout-prereg-draft (p2 S, DRAFT: the operator approves)
Start line:
`You are Builder. Login A. Tasks: ci-red-one-wording, mid-turn-image-intake-gap, auto-compact-at-25-for-all-sessions-clau. Follow MyTradingSys/system/LENOVO_NEXT_SESSION.md; tasks.py next loop; report each ship with mts_signal.py send "lenovo: <card> <sha>" --to jis-nb.`

### B NUC (fresh week; SONNET cards, one at a time; report `nuc-B: <card> <sha>`)
1. machine-rename-aliases (p2 M)
2. dsa-audit-04-clean-room-twin (p1 M)
3. dsa-audit-05-placebo-nulls (p1 M)
4. dsa-audit-06-cost-fill-realism (p1 M)
5. dsa-audit-07-stale-verdicts (p1 M)
6. context-composite-v2-dev-read (p2 M)
7. apply-gpt-fix-fabio-notes-gemini and apply-gpt-review-fix-items-to-gemini-ext (p3 M)
8. then `tasks.py next` for SONNET cards
Start line:
`You are Builder. Login B. Tasks: machine-rename-aliases, dsa-audit-04-clean-room-twin, dsa-audit-05-placebo-nulls, dsa-audit-06-cost-fill-realism, dsa-audit-07-stale-verdicts. Boot: python scripts/dev/sync.py start <slug>; work only in the printed WORKTREE. One task per session, then hand over; report each ship with mts_signal.py send "nuc-B: <card> <sha>" --to jis-nb.`

### C desktop (jishusharma1985; Thinker + design, Fable quota included)
1. layer-review-after-simulator (p3 M): Thinker brief (confluence, agreement trades, what old backtests got wrong); input `layer_facts/` (lands from the lf-*-gemini-facts cards); never discard, demote or park a layer.
2. sim-dashboard-v1 and the sim-desk cards (launcher, Krown plug-in, side-by-side) once the sim-v2 Builder has shipped.
3. Claude review of each Gemini `layer_facts` branch before it ships (producer is not the reviewer).
Start line:
`You are Thinker. Login C. Card: layer-review-after-simulator. Never discard, demote or park a layer.`

### Not Claude: NUC lanes (kept busy by the Supervisor's wake)
- GPT lab (`codex_run.py tick`, one every ~21 min): lf-*-gpt-rederive (13 families), trust-recheck-*.
- Gemini (`gemini_queue.py run <card>:low`, Flash only): lf-*-gemini-facts (13 families), yt-gem-fabio-fetch-2, yt-fabio-fetch-retry.

## Every wake (Supervisor A)
Count `ready` cards against running workers per station. A station idle with ready cards is reported to the Lead at once (`mts_signal.py send ... --to jis-nb`). Check each reported sha with `git cherry origin/fast-track <sha>` and the CI run whose headSha equals it.
