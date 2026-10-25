# LOGIN PLAN, 2026-10-26 (Supervisor on the desktop, login C, from the Lead's operator orders)

Source of truth for cards is `python scripts/dev/tasks.py next` / `check <id>` (a card here that is no longer `ready` is skipped).
A station is one device plus one login. Logins may move between devices; the start lines name the login, never the device.
Read budgets with `get_usage` (A laptop, B NUC, C desktop); the numbers below are 2026-10-26 ~19:10 IST readings and go stale in 6 h.

## Budget rules (operator, 2026-10-26; logins corrected by the Lead: the JIS-NB desktop app is login C, not A)
- **Login C = desktop (JIS-NB, jishusharma1985)**: weekly cap 80% until the end of Monday 2026-10-26 (week 61% at the reading, about 19 points to spend), then only the most important work; Tuesday uses the last 20% (reset 2026-10-27T20:00Z). Fable quota counts. The Supervisor reads `get_usage` before each wave and stops launching desktop Builders at 80%.
- **Login A = laptop** (week 9%, fresh, reset 2026-10-30T09:00Z): takes the BULK of new work, full sessions, exhausts its week before the reset.
- **Login B = NUC** (fresh week): full sessions, exhausts its week in time.
- Hand-over rule: one task per session; hand over when done (NEXT_SESSION.md + `sync.py ship`); the watcher hands over every 3 to 4 hours (its hand-over line says Login C). A Builder's final report starts with its role banner, then `Result:` and the sha.
- Never discard, demote or park a layer (operator NO, 2026-10-25). Testnet only; no live-tree changes.

## Queues (ordered; claim each with `sync.py claim`, ship each with `sync.py ship --release <slug>`; skip a card that is no longer `ready`)

### Login A laptop (BULK; no F: drive; started by the operator; sized to a fresh week, about 20 cards)
1. quota-source-numbers-bug, pages-follow-builds-make-the-republish-s, station-tidy-sync-py-where-all-at-sessio (p1 S)
2. auto-compact-at-25-for-all-sessions-clau, super-session-coordinator-stalls-when-it, main-checkout-stays-a-clean-copy-of-trun, worktree-substantive-recovery (p1)
3. gate-test-lease-timeout-under-load, hook-reminder-get-usage-before-after-age, habib-holdout-prereg-draft (p2; the last is a DRAFT the operator approves)
4. trendline-v11-detector-fixes (p2 M), trendline-g3-pack-align, trendline-ledger-registry-hygiene (p3)
5. ship-waits-own-ci, ship-under-2-min, context-gap-fold-on-ship, rv05-h2-position-line-evidence, research-top-level-declutter, one-coordinator-doc (p3-p4)
6. then `tasks.py next` for SONNET cards that need no F: drive
Start line:
`You are Builder. Login A. Tasks: quota-source-numbers-bug, pages-follow-builds-make-the-republish-s, station-tidy-sync-py-where-all-at-sessio, auto-compact-at-25-for-all-sessions-clau, super-session-coordinator-stalls-when-it, main-checkout-stays-a-clean-copy-of-trun, worktree-substantive-recovery, gate-test-lease-timeout-under-load. Follow MyTradingSys/system/LENOVO_NEXT_SESSION.md; tasks.py next loop; one task per session then hand over; report each ship with mts_signal.py send "lenovo: <card> <sha>" --to jis-nb.`

### Login B NUC (BULK; fresh week; SONNET cards, one at a time; report `nuc-B: <card> <sha>`)
1. machine-rename-aliases (p2 M), dsa-audit-04-clean-room-twin, dsa-audit-05-placebo-nulls, dsa-audit-06-cost-fill-realism, dsa-audit-07-stale-verdicts (p1 M)
2. context-composite-v2-dev-read (p2 M)
3. apply-gpt-fix-fabio-notes-gemini, apply-gpt-review-fix-items-to-gemini-ext, argon-fix-defects-and-re-land (p3)
4. analyst-ingest-roman-x (p3 M), gap-g7-stop-slippage (p4 M), supervisor-role-trim (HAIKU)
5. then `tasks.py next` for SONNET cards
Start line:
`You are Builder. Login B. Tasks: machine-rename-aliases, dsa-audit-04-clean-room-twin, dsa-audit-05-placebo-nulls, dsa-audit-06-cost-fill-realism, dsa-audit-07-stale-verdicts, context-composite-v2-dev-read. Boot: python scripts/dev/sync.py start <slug>; work only in the printed WORKTREE. One task per session, then hand over; report each ship with mts_signal.py send "nuc-B: <card> <sha>" --to jis-nb.`

### Login C desktop (JIS-NB; capped at 80% through Monday; layer review (the old Thinker job; no role line, see the start line below), design and the cards that need F:/JIS-NB; Fable included)
1. layer-review-after-simulator (p3 M): layer-review brief (confluence, agreement trades, what old backtests got wrong); input `layer_facts/` (lands from the lf-*-gemini-facts cards); never discard, demote or park a layer.
2. sim-dashboard-v1 and the sim-desk cards (launcher, Krown plug-in, side-by-side) once the sim-v2 Builder has shipped.
3. JIS-NB-lane cards: live-read-from-any-device (p1), host-legacy-tasks-unregister (p1), state-code-accumulator-backfill (p2), t09-f3-rsi-live-untested-events (p1).
4. Claude review of each Gemini `layer_facts` branch before it ships (producer is not the reviewer).
Start line:
`Work card layer-review-after-simulator: python scripts/dev/sync.py start layer-review, read MyTradingSys/system/tasks/layer-review-after-simulator.json and MyTradingSys/system/WATCHER_TASKS_2026-10-25.md task 4; never discard, demote or park a layer before the operator reviews it in the simulator; ship with sync.py ship --release layer-review.`

### Not Claude: NUC lanes (kept busy by the Supervisor's wake)
- GPT lab (`codex_run.py tick`, one every ~21 min): lf-*-gpt-rederive (13 families), trust-recheck-*.
- Gemini (`gemini_queue.py run <card>:low`, Flash only): lf-*-gemini-facts (13 families), yt-gem-fabio-fetch-2, yt-fabio-fetch-retry.

## Every wake (Supervisor, login C desktop)
Count `ready` cards against running workers per station. A station idle with ready cards is reported to the Lead at once (`mts_signal.py send ... --to jis-nb`). Check each reported sha with `git cherry origin/fast-track <sha>` and the CI run whose headSha equals it.
