# Station watcher flow guard: design note, 2026-10-28

Card `watcher-ship-flow-guard` (Lab_Guy ACCEPT, 356e109a8). Design only: no code changes. Target: `MyTradingSys/research/pipeliner/station_watcher_monitor.py` (a bare `while True` loop, no functions, no tests today). Its 5-min loop reads `traffic.py status --json` and flags only liveness flips, `CODEX-STALLED`, lease expiry and the desk-pending count.

Goal: also catch a stuck ship (CI red on the last ship, a gate slot held long, a STALE claim, a ready-card lane sitting idle) and re-propose routing centrally. Every number below is labelled OURS unless a source line says SOURCED.

## 1. Per signal: data source and threshold (one default each)

| Signal | Data source that already exists | Default threshold | Label | False-positive risk |
|---|---|---|---|---|
| CI red on the last ship | `git fetch origin green/fast-track`, then compare `origin/green/fast-track` with `origin/fast-track` (the same logic as the `CI green:` line in `scripts/dev/make_status.py:241-259`, rendered into STATUS.md). The watcher does not run `make_status.py` (slow); it reuses the one git comparison: green tip lags trunk by more than docs-only commits for 20 min. | trunk ahead of green by a CI-gated commit for > 20 min | OURS | A normal CI run is a few minutes, so 20 min is 4x a healthy run; docs-only landings are excluded exactly as make_status excludes them. |
| Gate slot held long | Slot files `mts_gate_slots/gate-slots/slot-N` in the host gate dir (`sync.py:221-237`, `GATE_SLOTS = 2` at `sync.py:190`); file mtime = acquisition time, content = owner PID (`sync.py:262-266`). | slot mtime older than 20 min with a live PID | OURS | Host-local only: the watcher sees its own host's slots, not the other machines'. A full `--full` gate can be long, so the flag says "held > 20 min", never "dead"; dead PIDs are already reclaimed by `gate_slot`. |
| STALE claim | `sync.py health` prints `STALE-CLAIM <slug>: <host>/<acct> <n>h old` (`sync.py:527-528`); `STALE_HOURS = 24` (`sync.py:52`). | reuse `STALE_HOURS` (24 h), do not define a second constant | SOURCED (the repo's own constant, `sync.py:52`) | Low; a claim on a long card is the owner's to release, so the signal asks the owner, it releases nothing. |
| Lane idle with ready cards | `traffic.py status --json`: `queue` (ready cards by lane) and `lanes.<name>` state; `allocate()` already builds a proposal when a lane is idle (`traffic.py:529-560`). | ready cards for a lane > 0 and its lane idle/not-running for two consecutive 5-min polls (10 min) | OURS | One poll can catch a lane between two cards; two consecutive polls removes that. |

## 2. Output format (reuses traffic.py's PROPOSED text)

Per flagged signal, per change only (not every poll):
1. One `STATE-CHANGE` line in the existing log, same shape as today, with a flag token appended: `CI-RED-20m`, `GATE-HELD-<slot>-<min>m`, `STALE-CLAIM-<slug>`, `LANE-IDLE-<lane>`. Same mechanism as the existing `CODEX-STALLED` token (the `lane_flags` list feeds `snap_key`, so a flag appearing or clearing is automatically a STATE-CHANGE).
2. One `mts_signal.py` PIPE note (the `PIPE` prefix is already how the Pipeliner reads signals), carrying the PROPOSED text from `traffic.py`'s `render_status` PROPOSED block (`scripts/dev/traffic.py:720-721`, format `[<who>] <action>  (<why>)`): `PIPE [who] action (why)`. The watcher builds `who/action/why` from the signal: CI red -> `[operator] last ship red: revert it (CI_RED rule)`; gate held -> `[<owner host>] gate slot N held <min> min by PID`; STALE claim -> `[<claim owner>] release or finish <slug>`; lane idle -> the existing `allocate()` proposal for that lane. Send at most one signal per flag per appearance (repeat only if it clears and returns), so a 5-min loop cannot spam the 200-character signal channel.

The watcher proposes and never acts: it does not revert, release claims, kill PIDs or start sessions (CLAUDE.md: builders never touch live processes; the Pipeliner session acts on PROPOSED).

## 3. Refactor: yes, extract a pure `check_once()`

Default: yes. Today the loop mixes subprocess calls, JSON parsing, logging and `time.sleep`, with the module body executing on import, so nothing can be tested without running it forever. Minimal refactor:
- `check_flags(status: dict, extras: dict, prev_flags: set) -> (flags: list[str], proposals: list[dict])`, pure: `extras` carries the three non-status readings (`green_lag_min`, `gate_slots`, `stale_claims`) gathered by thin `read_*()` functions.
- `main()` keeps `run`/`log`/`sleep`; module body guarded by `if __name__ == "__main__":`.
- Tests (fail first on the old file, which has no `check_flags`): CI lag 19 vs 21 min; gate slot 19 vs 21 min and dead PID ignored; claim 23 vs 25 h; lane idle one poll vs two; flag appears -> one signal, stays -> none, clears and returns -> one; malformed `extras` field -> no flag and a `MONITOR ERROR` line (fail closed means "unknown", never "all good").

## 4. Follow-up

One implementation card opened by the planner/coordinator from this note (`tasks.py new`), est 6 turns, scope = `station_watcher_monitor.py` plus its test file; markable done only with passing test output in its result field. Not opened here because this card's scope is the note only.
