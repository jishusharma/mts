# Rolling super sessions on every ACTIVE station: design note, 2026-10-28

Card `rolling-supersessions-per-station` (design only, no code). Operator idea 2026-10-26: a rolling (up to 24 h) super session on every ACTIVE station, one per login, kept alive by D5 context rotation (`clear_session` + rebuild from the notes file) instead of restarts; the station watcher re-broadcasts a PROPOSED start line when a station goes idle with ready cards.

Station = one device with one login (DEVICES.md line 3). Every default below is OURS (judgement, not tuned) unless it says it is inherited; none is the trader's.

## Mechanisms reused (nothing new is invented)
| mechanism | where | what it already gives |
|---|---|---|
| One coordinator per login; heartbeat | `SUPER_SESSION.md:59`; `supervisor.py:730` `HEARTBEAT_MIN = 100`, `HB_RE` at `:759` | a BUDGET signal line with `sup=` newer than 100 min = a live coordinator; older, or `mode=ENDED` = gone |
| D5 rotation | `SUPER_SESSION.md:14` | parent runs `clear_session`, sends `You are Supervisor. Context rotation: rebuild per SUPER_SESSION.md D5 from <notes path>, ...`; rebuild from the notes file, board, `git cherry`, `list_sessions` |
| Start prompt | `SUPER_SESSION.md` "Prompt: start a super session" | `You are Supervisor. Run the super session per MyTradingSys/system/SUPER_SESSION.md for up to 24 h; never ask, take the defaults.` |
| PROPOSED block | `traffic.py:720` `render_status`, built by `allocate()` | one line per proposal: `   - [who] action  (why)`; a card already proposed is not proposed again for `RESERVE_MIN = 60` min (`traffic.py:667`) |
| Machine liveness | `traffic.py:403-408`, `traffic_inventory.json` `liveness_min` | ACTIVE <= 30 min since last event, IDLE <= 180, else SILENT |
| STATE-CHANGE | `research/pipeliner/station_watcher_monitor.py` | session-owned 5-min loop (`INTERVAL_S = 300`), not a machine scheduler; prints `STATE-CHANGE` when the snapshot key changes (liveness, codex stall, desk pending) |

## 1. Which stations count ACTIVE, and the idle threshold
Options:
| option | cost | risk |
|---|---|---|
| A. Every device x login in `traffic_inventory.json` | none | proposes starts on a laptop nobody is at; 3 devices x up to 3 logins = up to 8 stations, one weekly budget per login |
| B. Device liveness not SILENT (<= 180 min) | reuses `liveness()` | liveness is per device, but the coordinator is per login: cannot say which login to start |
| C. B, plus the login is not in STOP/THROTTLE and has room for a worker (`pace_plan` slots >= 1), plus the login has no live coordinator | reuses `pace_plan` and the `sup=` heartbeat | needs the per-login heartbeat read inside `traffic.py`, which `allocate()` does not do today |

**Default: C.** A station is ACTIVE when (a) its device is ACTIVE or IDLE by `liveness()`, (b) its login's mode is SPEND or NORMAL with at least 1 slot, (c) no coordinator of that login is live. Hold-offs come first: STOP/HOLD in ANNOUNCEMENTS, CI red, and the D6 stops mean no proposal.
**Idle threshold: 100 min with no live coordinator and at least 1 ready non-raw card for this lane (OURS, inherited from `HEARTBEAT_MIN`; no new number invented).** The 5-min watcher loop only evaluates it; one re-broadcast per 60 min at most (inherited `RESERVE_MIN`), so a proposal the operator ignores is not repeated every 5 min.

## 2. The PROPOSED start line: trigger and exact text
Trigger (all true, evaluated by the watcher each loop): station ACTIVE per point 1 and idle >= 100 min, ready cards for the lane >= 1, and no proposal for this station in the last 60 min. This becomes one more entry from `allocate()`; the watcher prints it as a `STATE-CHANGE` line because the snapshot key gains a `station_idle` component.

Text (same `[who] action  (why)` shape as today; `who` gains the login, the one change from today's machine-only `who`):
```
   - [JIS-NUC/A] start a session with: You are Supervisor. Run the super session per MyTradingSys/system/SUPER_SESSION.md for up to 24 h; never ask, take the defaults.  (no coordinator for login A for 135 min, 7 ready cards, 5 h 22%, mode SPEND)
```
- When this line is proposed it replaces the existing `start sessions for <card ids>` line for that station: workers are background Agents of the coordinator (`roles/supervisor.md:35`), not separate sessions, so proposing both double-counts the same cards.
- The line is a proposal for the operator or the Lead, not an auto-start: `start_session` is refused on event turns and no scheduler may start one (SCHEDULING_POLICY.md). It must carry the whole command, so the operator copies one line.

## 3. D5 rotation versus a cold start
| | D5 rotation | cold start on a station with no coordinator yet |
|---|---|---|
| trigger | the coordinator exists; context over about 200K at a natural break (`SUPER_SESSION.md:14`) | the PROPOSED line of point 2 |
| who acts | the parent session (a coordinator cannot clear itself); `clear_session`, then the rotation message | the operator or Lead starts a new Sonnet session with the start prompt |
| state | `handover/SUPERVISOR_<L>.md` in the coordinator's own worktree is current (rewritten every wake) | no worktree notes file; `handover/SUPERVISOR_<L>.md` on trunk is history only and may be hours old (CLAUDE.md step 2); state comes from the board and `git cherry` |
| boot work | rebuild only; no Planner/Doctor run unless due by their own clocks (D2, D4) | full first turn: `get_usage`, ANNOUNCEMENTS ACTIVE, STATUS.md, NEXT_SESSION.md, Planner, Doctor, then workers |
| clock | the 24 h clock does not restart (D6): a rotated coordinator ends at the 24 h from its first start | starts a new 24 h clock |
| one per login | already holds the login | must read the login's heartbeat first; if `sup=` is under 100 min old, stop (another coordinator holds it) |
| first act | rewrite the notes file | write the notes file and emit the first BUDGET line with `sup=` in the first wake, which silences the re-broadcast |

**Default: rotation is preferred whenever a parent session exists; a station without one lets the coordinator end at D6 (24 h, a stop condition, or the transit hand-over) and the re-broadcast is its successor path, as a cold start.**

## Left open (the card did not settle these; no code here)
- `allocate()` has no per-login coordinator liveness: it reads `liveness` per device and budgets per machine (min over logins). Point 1(c) and the `[device/login]` `who` need the `sup=` heartbeat read inside `traffic.py`.
- Overlap between hand-over rules: `supervisor.py:1332-1333` `TRANSIT_CONTEXT = 150_000` / `TRANSIT_HOURS = 3.0` (OURS) make a coordinator write its hand-over at 150K context or a 3 h wave, while D5 rotates at about 200K and D6 runs 24 h. The note assumes D5 and D6 win for rolling sessions; reconcile before implementing.
- Who owns the station-watcher loop: `station_watcher_monitor.py` is a session-owned loop for the Pipeliner watcher with a dated log path (`STATION_WATCH_2026-10-26.log`). A rolling-session broadcast needs a session that keeps it running; nothing in the repo guarantees one.
- No evidence file exists for the original operator idea beyond the card title (no transcript on disk), so the 100 min threshold and "ACTIVE" definition are untested judgement.

## Follow-up implementation card
To be opened with this ship (`tasks.py new`), pointing at this note: per-login station-idle trigger in `traffic.py allocate()` and the monitor's snapshot key, with tests; markable done only when shipped with passing tests and the test output attached to its result field.
