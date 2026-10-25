# WATCHER TASKS, 2026-10-25 (from the Doctor on JIS-NB, for the next desktop watcher session)

The operator (2026-10-25): one watcher on the desktop governs every station so they stay in sync. The Doctor only prepares this list; the watcher session does the work.
A **station** is one device plus one login (Desktop-A, Desktop-C, Laptop-A, NUC-B). Logins may move between devices later, so write no rule that ties a login to a device. Read who runs where with `python scripts/dev/mts_signal.py who`.
How it governs: the repo is the one plan (task files, cards, broadcasts, signals). The watcher is its only writer of plans. Workers read their file, work, and report each ship with `mts_signal.py send ... --to jis-nb`.
Heavy work goes to the desktop's Max login through Sonnet Builders. The laptop and NUC Pro logins take read-only, review and card work.

## Start line (operator types this in a new desktop session, login A)
`You are Supervisor. Login A. Tasks: MyTradingSys/system/WATCHER_TASKS_2026-10-25.md`

## Every wake
1. `cd C:\MTS\mts-jisnb; git pull`, then `python scripts/dev/mts_signal.py read --hours 1`, `mts_signal.py who` and `mts_signal.py acks`.
2. For every reported sha (`lenovo: ...`, `agy: ...`, Builders): `git cherry origin/fast-track <branch>` must be empty.
   CI: find the run whose headSha equals that sha (`gh run list --branch fast-track --json headSha,conclusion`). A commit touching only `MyTradingSys/system/` or docs gets no CI run (`ci.yml` paths filter); say "no CI run (docs only)", never borrow another run's result.
   Red: `git revert` it and ship within 10 minutes.
3. Hand over to a fresh watcher session every 3 to 4 hours, or when context grows: overwrite this file's "State" section, ship it, then stop.

## Tasks, in order
1. **Laptop-A Claude session** (`LENOVO_NEXT_SESSION.md`, started 15:14Z; holds `exhaust-A` and `B196`). Check each ship. Steer with `mts_signal.py send "<card>" --to desktop-f7iu69n` when its queue runs dry. Its login A 5-hour use was 9% at 15:19Z, so it can run the full window.
2. **Laptop Antigravity Gemini** (`ANTIGRAVITY_LAPTOP.md`, 402f4693b). About 32% of the laptop's Gemini week is left and it resets about 21:15Z today, so use it before then. The operator types its start line in Antigravity; it reports `agy: ...`. Check each ship. Claude reviews its layer fact sheets (producer is not the reviewer). If it runs out of items, file more `[GEMINI]` cards (read-only review or research).
3. **Machine rename, phase 1** (card `machine-rename-aliases`). A Builder started by the Doctor (background Agent `a1c47a4e61ac5d765`) adds `scripts/dev/hosts.py`, so old and new names (JIS-NB / JIS-DESKTOP, DESKTOP-F7IU69N / JIS-LAPTOP) count as one machine, and writes `MACHINE_RENAME.md`. When it ships, verify cherry and CI; red means revert. Phase 2 is the operator's own renames, at a quiet time; the laptop needs a live-loop stop and start per DEPLOY_RUNBOOK. Not before phase 1 is green.
4. **Thinker session on Desktop-C** (login C): gather the thinking on layers. Which analyst and indicator layers confirm each other (confluence), which trades fire when they agree, and what the old backtests got wrong (unvetted parameters, bugs, fabrications, assumptions). Input: Antigravity's `layer_facts/` sheets. Card `layer-review-after-simulator`. **Never discard, demote or park a layer** before the operator reviews it in the simulator (operator NO, 2026-10-25).
5. **Operator decision still open**: freeze new tooling, build one end-to-end drill, cut to 3 roles (Lead, Builder, Eagle_Eyes). Until he answers, start no new tooling.
6. **Open broadcasts**: b-79ee5e and b-10b3d8 are `told` on the laptop. b-be9727 is `told` and b-10b3d8 is `none` on vm. b-9c6516 and b-ed80a5 should go `done` when the laptop session ends. Chase any told-with-blocker note; never re-ask the operator.
7. **Small leftovers**:
   - Eagle_Eyes boot line (`live_mirror.py brief`, quote `LIVE OWNER: <host>`) in `roles/eagle_eyes.md`; another Builder owns that file, so check first.
   - Laptop mirror publish (`live_mirror.py publish`) is in both laptop lists.
   - The ship bootstrap fix (ship re-runs the merged `sync.py`) waits on the operator.
   - JIS-NB C: has 13.7 GB free (under 15). Ship flagged stray `python` processes (`context_gap.py fold`, about 3 h old). Report them; builders never kill processes.

## Not on this list
Mainnet anything. Removing layers. Deploys or live-tree changes (manual or coordinator-run only, DEPLOY_RUNBOOK.md). Schedulers.

## State (overwrite at each hand-over)
- 2026-10-25 ~15:40Z: trunk head 402f4693b; last CI run 242fbf7a1, green. Laptop-A Claude working B196. Antigravity not started yet. Rename Builder running.
