# S3 (G-d) supervision decision note - keeping position_manager.py alive

2026-09-28. Research only, per the FAST_TRACK_WORKERS S3 task - no
implementation here, just the current state and a recommendation.

## What exists today

Read `MyTradingSys/execution/position_manager.py` (`manage()`, `main()`) and
`scripts/core/loop-supervisor.ps1` (the Java data-feed loop's supervisor).

**Nothing today keeps `position_manager.py` running.** `loop-supervisor.ps1`
supervises the Java candle-read/decide loop (`datafeed.Scheduler` and
friends) only - it has no reference anywhere to `position_manager.py` or
`executor.py`. `execution/README.md` documents T050 explicitly as "a module,
switchable, never gating core behavior" alongside the core loop, and that
separation appears to hold literally: the execution layer has no supervisor
of its own yet.

`position_manager.py main()` is a one-shot CLI: `python position_manager.py
<plan_id> [--max-seconds N] [--once]`. With `--once` it does exactly one poll
and returns/exits. Without `--once` and without `--max-seconds` it loops
forever inside that one process (`while True: ... time.sleep(POLL_INTERVAL_
SECONDS)`), until it returns (position closed), raises `ManagerHalted`
(flattened), or the process is killed. Today, an operator (or the same
terminal session that ran `executor.py --go`) is what actually runs it, and
for how long is whatever they choose - there is no evidence in the repo of
an automated wrapper.

## What the S3 code change covers, and its limit

The MAX_UNPROTECTED_SECONDS / `unprotected_since` change just shipped bounds
how long a *running* `manage()` call will keep retrying a stop re-place
before it gives up and flattens - it is a bound on one process's behaviour
while it is alive, not a guarantee that the process IS alive. Its docstring
says this explicitly: `unprotected_since` resets to `None` on every fresh
process, so the bound does not carry over between separate invocations of
`position_manager.py`.

**Deribit-side protection is independent of any of this.** Once a
stop_market is accepted server-side, it protects the position - reduce-only,
trigger=mark_price - regardless of whether `position_manager.py` (or Python,
or the operator's machine) is running at all. What is *not* covered if the
process is dead:
  - a target fill shrinking the stop (G1) - the position stays over-covered
    (the stop still covers the pre-fill size, which is safe, just not
    tight) until something restarts management;
  - the stop being cancelled or expiring and needing a re-place (G-d) - if
    nobody is running `position_manager.py` at that moment, the position is
    genuinely naked until the process restarts and notices;
  - detecting a manual/behind-MTS's-back close or a grown position (G2) -
    purely a journal/audit gap while the process is down, not a live-risk
    gap, since the exchange side is unaffected either way;
  - the reconciler (`reconciler.py`) never runs on its own schedule either -
    same one-shot-CLI shape, same gap.

So the risk that matters is specifically: stop gets cancelled/expires ->
process is not running -> nobody re-places it -> naked position for as long
as the process stays down.

## Options

1. **In-process thread inside executor.py**, started right after
   `execute_plan()` returns `entry_filled_stop_placed`, running `manage()`
   in a background thread for the life of the `executor.py --go` process.
   Simplest to wire (no new process, no IPC), but ties the position's
   ongoing protection to the same process/terminal the operator used to
   enter the trade - if that terminal is closed or the machine sleeps, the
   thread dies with it, same failure mode as today just less likely
   (the process now has a reason to stay open).

2. **Separate process launched by executor.py** (`subprocess.Popen`,
   detached) right after a successful entry, one per plan_id, so it
   survives the parent terminal closing. Needs a way to know it crashed
   (a pidfile + a periodic check, or just relying on the operator noticing)
   and a way to stop it cleanly once the position closes (it already exits
   on its own when `manage()` returns "closed" or raises `ManagerHalted`,
   so mainly need to make sure it doesn't silently die and stay dead).

3. **PowerShell scheduled watchdog**, following the exact
   `loop-supervisor.ps1` pattern already proven for the Java loop: a
   supervisor script that checks whether a `position_manager.py <plan_id>`
   process is running for every plan_id with an open, un-halted journal,
   and restarts it if not. Matches the repo's existing operational pattern
   (PowerShell for loop/session control per the project's own stack
   description) and decouples supervision from whatever
   `executor.py`/Python process happened to enter the trade - a crash of
   either doesn't take the watchdog down with it, and the watchdog is
   already how the Java side is supervised, so there is one supervision
   story instead of two.

4. **Exchange-side protection only** (do nothing beyond the stop_market
   already placed): accept that between a stop being cancelled/expiring and
   an operator noticing and manually re-running `position_manager.py`, the
   position is naked. Cheapest, matches "discovery phase" project status,
   but is exactly the gap this task was raised to close.

## Recommendation

**Option 3** (PowerShell watchdog, `loop-supervisor.ps1`-style), for one
reason: this repo already solved "keep a Python-adjacent long-running loop
alive across crashes/restarts" once, for the Java data-feed loop, and the
project's own stack choice (PowerShell for loop/session control) says this
is the intended place for that job, not inside the execution-layer Python
itself. Option 1 (thread) is the fastest to build and fine as an interim
step - the position IS covered exchange-side by the stop even without any
supervisor, so a thread inside `executor.py --go` covers the common case
(operator leaves the entering terminal open) with near-zero extra work -
but it's still a single point of failure the watchdog does not have.
Whichever is chosen, the reconciler has the identical gap and should be
supervised the same way, not left as a second one-shot CLI nobody restarts.

**Precisely what is and isn't covered if the process is dead (repeated for
clarity):** a stop that is currently live and untouched keeps protecting the
position with the process dead - this is unaffected by process supervision
entirely. What supervision buys is recovery from the moment that stop stops
being live (cancelled externally, expires, gets triggered leaving a partial
fill's leftover size unmanaged, etc.) - without a live process to notice and
re-place it, the position is naked from that moment until something
restarts management, for as long as that takes.
