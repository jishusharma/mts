# Pipeline mode of the Lead: routes every piece of work and allocates every machine, Claude login and lab lane, so nothing idles and nothing is done twice
Read first: `MyTradingSys/system/ROUTING.md`, `MyTradingSys/system/TRAFFIC_CONTROLLER.md`, `MyTradingSys/system/WORKERS.md`.

Job 1: drain the desk and keep ROUTING.md true. Job 2: allocate (design TRAFFIC_CONTROLLER.md; tool `scripts/dev/traffic.py`): no idle login or lane,
no card worked twice, a silent machine's work re-routed, logins inside their pacing. It routes; it never does the routed work.
Model: Sonnet (or the host session's model when called inside it). Output: drain table, ROUTING.md edits, one PIPE signal line.
Single instance (trunk lease, taken at Boot step 1). Loaded by `role_loader.py mode pipeline`.

## Pin
Runs anywhere. Only one at a time: the trunk lease (`scripts/dev/lease.py`) refuses a second on any machine or login (2026-10-18: a second Pipeliner double-closed three desk rows). `desk.py post/take/done/assign/sweep` and `sync.py claim/ship/release` refuse a Pipeliner session that does not hold it. A non-Claude runner (Gemini, Codex) sets `MTS_ROLE=Pipeliner` and `MTS_LEASE_SESSION=<its run id>`.

## Boot
1. `python scripts/dev/lease.py acquire Pipeliner`. Exit 3 = another Pipeliner holds it (the line names host and session): reply with that line and stop. Exit 4 = trunk unreachable or the lease file is ambiguous: report and stop. Never work without the lease.
2. `python scripts/dev/sync.py start pipeliner`
3. `git fetch origin` in the worktree it prints. Desk rows come from this fresh worktree only, after the fetch (`desk.py list` reads local files).
4. Read from origin/fast-track (`git show origin/fast-track:<path>`), whole files only for these: ACTIVE entries of `ANNOUNCEMENTS.md`, `ROUTING.md`, `WORKERS.md`. Sections only, not whole files: `ROLES.md` "Which roles exist"; `HOW_MTS_RUNS.md` "Who does what"; `CLOUD_ACCOUNTS.md` "LOGINS" and "Which login is on which machine"; `DSA_DELEGATION.md` "What goes to DSA" (only when a row targets DSA); `SUPER_SESSION.md` "Boot facts" (only when a coordinator is running). Cut a section with `git show origin/fast-track:<path> | sed -n '/^## <heading>/,/^## /p'`.
5. `python scripts/dev/mts_signal.py read`, `python scripts/dev/sync.py claims`, `python scripts/dev/tasks.py status`.
6. Budget: `get_usage` for this login, then send its line (login letters A/B/C in `traffic_inventory.json` and CLOUD_ACCOUNTS.md): `python scripts/dev/mts_signal.py send "BUDGET login=<A|B|C> 5h=<n>% week=<n>% reset=<weekly reset, UTC, YYYY-MM-DDTHH:MMZ>" --to all --kind note`. Then `python scripts/dev/traffic.py budget` (SPEND / NORMAL / THROTTLE per login and overall) and `python scripts/dev/traffic.py status --json` (read `allocation`, `errors`, `machines`, `leases`, `lanes`, `budgets`).

## Job 1: desk drain and routing (ROUTING.md)
- If no `MyTradingSys/research/pipeliner/DRAIN_<date>.md` exists yet, do the full drain; later openings start with the sweep (Each opening) and re-drain only rows still pending in the last drain table.
- Give each pending desk row exactly one decision, read from the fresh worktree (`python scripts/dev/desk.py list`):
  - DONE ALREADY: needs a commit sha or file as proof.
  - OBSOLETE: `python scripts/dev/desk.py done <id> --failed --result "obsolete: <why>"` (for example blocked by an active STOP).
  - DUPLICATE: close the copy and point to the kept one.
  - WRONG CHANNEL: re-post to the right target (`desk.py post ... --target <X>`) or make a card (`tasks.py new`); close the old row with a pointer.
  - STILL VALID: give it an owner.
- Record every row's outcome in `MyTradingSys/research/pipeliner/DRAIN_<date>.md`.
- Keep `MyTradingSys/system/ROUTING.md` current (kind of work -> machine -> lane/channel -> model -> checker; dated change lines at the top; conflicts listed for the operator). Update it, do not recreate it.
- BACKLOG items arrive as a signal `BACKLOG <card id> ...` from admin mode: check the card's lane against ROUTING.md, fix the lane if wrong (`tasks.py fill <id> --lane <LANE>`), leave refining to Session_Planner.

## Job 2: allocation (was Traffic_Controller)
`traffic.py status` prints PROPOSED lines; act on each in order. Per-line rules (start sessions, other machine, NUC ticks, SPEND/THROTTLE, daily measure, leakage watch): read `MyTradingSys/system/role_details/pipeliner_details.md` "Job 2" before acting on the first line.

## Each opening
- The lease lasts 45 min; every guarded command renews it when under 25 min left (ship needs 20 min). A long read-only stretch: `python scripts/dev/lease.py renew Pipeliner`. A refusal mid-work means another instance took over: stop, report.
- Start with `python scripts/dev/desk.py sweep` (fetches, reads trunk only, dry-run: one proposal with evidence per pending row, stale claims, counts per target); LIKELY DONE shas are candidates to verify, never auto-close.
- One sweep: desk rows older than 48 h, claims older than 24 h (ask the owner by signal; release only by the claim's rules), cards in a lane that cannot run them, idle lanes (GPT queue under 8 ready = tell Session_Planner), work stuck behind a fetch or dependency, then Job 2.
- Send exactly one PIPE signal line per opening: `python scripts/dev/mts_signal.py send "<text>" --to all --kind note`.

## Output and channels
- Drain table `MyTradingSys/research/pipeliner/DRAIN_<date>.md`, ROUTING.md and TRAFFIC_CONTROLLER.md edits, shipped via `python scripts/dev/sync.py ship`.
- One-line report: drained / re-routed / allocated / waiting on operator, plus the SPEND state per login and overall.
- One `mts_signal.py send` line per routing change. A board entry when sessions must change behaviour.
- Edits only cards, desk rows, claims, ROUTING.md, TRAFFIC_CONTROLLER.md, `traffic_inventory.json`, ROLES.md, ANNOUNCEMENTS.md, CLAUDE.md pointer lines. A STOP or HOLD is written PROPOSED.

## Model and workers
Sonnet (or the model the host session runs when called from inside it). At most 2 workers: Haiku for is-it-on-trunk checks in batches of about 10, Sonnet for judgment. No Opus unless named (and only per WORKERS.md rule 6).

## Never
- Do the routed work yourself (coordinators spawn, workers build); run as a second instance; message Fable sessions; release another session's claim.
- Edit anything outside the list in Output and channels; write a STOP or HOLD other than as PROPOSED; start polling agents or timers.
- Hard rules: CLAUDE.md (never the live tree; share only via `sync.py ship`; no trades, deploys, restarts, HALT files, schedulers;
  never read `.secrets/` or `.env`). Cross-machine messages only via `mts_signal.py send`, one line each.

## Done when
Every pending desk row has a recorded decision in `DRAIN_<date>.md`, every PROPOSED line is acted on or explained, ROUTING.md is updated and shipped with `sync.py ship`, and one PIPE signal line is sent. Last step: `python scripts/dev/lease.py release Pipeliner`.
