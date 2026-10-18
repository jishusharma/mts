# GATE_SPEED - ship gate wall time (2026-10-18, operator: "sessions take too long, the ship gate is the main cause")

## Measured (before)
- 7 full ship gates of one session (ship*.txt, 4 jobs): clean wall 469-636 s (one loaded run 1069 s). Step medians:
  3xt 311 s, 4h 271 s, 3k 270 s, 5b 237 s, 4 (test_turn_meter.py alone) 195 s, 4g 156 s.
- All 30 tree timing logs (4106 step rows): medians 3xt 671, 3k 523, 5b 425, 4b 383, 4g 371 s (gates overlap: 2 slots x 4 jobs).
- Why full: last 200 trunk pushes = docs 112, full 59, smoke 29. That session's ships were full only because `.claude/settings.json`
  changed ("matches no rule"); others: research data (.tsv .gz .err), .gitignore, .aiexclude, scripts/dev non-.py data.
- Late failures: 4d (a 6.6 s step) printed FAIL at +438 s, gate ran on to 469 s; 4g (research_kit line refs) at +152 s, ran to 547 s.
  Each fix = full rerun (~9 min). Fail counts (timing logs): 4c 25, 4b 20, 4h 15, 3sig 12, 3xt 9, 3tl 9.
- Push race: 3 of 4 passing ships lost at least one race; one died on `git fetch ... incorrect old value provided` (shared ref).

## Changes (sync.py ship only; CI, auto_deploy and a bare run_all_tests keep their argv and run every step)
| # | Change | Saves |
|---|---|---|
| D1 | `--precheck`: CHEAP_STEPS (median <= 25 s) + step 4t (pytest of the <= 12 `MyTradingSys/tests` files that reference a changed module or name a changed file, slow files excluded) run first, 2 at a time, no gate slot. Any failure: every other step is NOT RUN. | repeat failure ~9 min -> precheck time |
| D2 | `--fail-fast`: after the first failure in the main phase, steps not yet started are NOT RUN (not timed; the summary fails closed). `--slot`: run_all_tests takes the gate slot around the main phase only. | rest of a doomed gate; slot not held by cheap steps |
| D3 | `--record` (`<worktree git dir>/mts_gate_record.json`): a step that passed on this exact clean tree (untracked files count), same step signature, same python, < 24 h, is not run again. Written atomically, never when HEAD moved mid-gate. Ignored when `CI` is set. | push failed after ALL TESTS PASSED, or one flaky step: rerun = that step |
| D4 | Fetch retried 3x with jitter; ship push 3 -> 5 tries, 1-5 s jitter; a lost race re-runs the gate once only when the incoming commits touch our paths or a module our .py files reference (`race_overlap`). | lost races stop failing |
| D5 | gate_select: research data suffixes (.tsv .gz .err .log .png .svg .parquet .pdf .jpg) = docs; `.gitignore`, `.aiexclude`, `.claude/settings.json`, `scripts/dev/<x>.tsv/.json/.csv/.html` = smoke (ALWAYS + steps whose tests name the file); settings.json adds 3js. A `.txt` on the live path and `run_extra_tests.py` are full. | most "full" ships become smoke |
| D6 | Smoke 3xt runs `run_extra_tests.py --only <extra_subset>` (changed file, its test_<name>, its study folder, folder of a changed shared module, tests that reference or name the change); smoke 5b runs `layer_subset` (changed layer folder + referencing modules; all when a file is directly in layers/, a shared module, or a folder without tests). Closes a gap: `scripts/dev/trace.py` never ran `test_trace.py`. | 3xt 300-670 s, 5b 240-425 s -> seconds |
| D7 | `test_turn_meter.py` calls `turn_meter.handle()` in-process; the garbage-stdin and one output test keep the real hook process. | 195 s -> 7 s |
| 3js | `config_check.py`: settings.json parses, every hook script exists, `.secrets/` and `.env*` stay ignored (now in `.gitignore`). | a broken hook no longer ships on smoke |

## Reviews (Sonnet + Haiku, one-time, 2026-10-18) and what changed
- D3 reuse across trees was unsound (import graph, deleted files): cut to same-tree only. Record atomic with a lock retry.
- Retry re-gate must see semantic overlap, with a cap: `race_overlap` + REGATES = 1. Separate SHIP_PUSH_TRIES (claims keep 3).
- settings.json is read by tests and hooks: 3js plus name-matched steps. Secrets sentinel added. Renames: `--no-renames -z`.
- Fail-fast needs its own NOT RUN state; skipped steps must not be timed. Shared modules (`__init__`, `conftest`, common*, _*) widen.
- Defaults taken (OURS): 2 precheck jobs, 12 targeted files (truncated, the shards still run them), 1 re-gate, 24 h record age.

## Measured (after, first ship e71e409b, full mode: sync.py is on the live list)
- Precheck (41 cheap steps + 4t) passed in 121 s: a cheap-step failure now ends the ship by +121 s (before: 4d FAIL at +438 s,
  4g at +152 s then ran on to 547 s, 4h at +644 s). Clean full gate 544 s (before 469-636 s); step 4 75 s (before 195 s).
- The push lost one race; the incoming commits did not touch our paths, so it pushed again with no re-gate (before: a lost fetch
  race killed a passing ship). 33 new tests fail on the old code.

## Quality guards
Full mode still runs every step (D1 reorders, D2 only stops a run that already failed). CI runs the whole suite on both OSes; it
never passes the ship flags. A failed step is dropped from the record. Linux-only failures stay CI's job (`ci_watch.py`).

## 60-second fast path (plan 2026-10-18, operator: a clean ordinary ship must finish in under 60 s)
Measured floor on JIS-NB (i7-4770K, 4 cores / 8 threads, Defender on, other sessions at ~35% CPU): python start 0.23 s, pytest start 0.5 s,
git calls 0.1 s. Smoke gate of `scripts/dev/nowin.py` today: 55 s = ALWAYS steps 3x (wiring_scan --check) 17-20 s and 3w (test_wiring_scan) 17-25 s,
3tl 7-9 s, 3dl 3 s, plus step 4f 17 s; a smoke change that a hub module reaches runs whole pytest shards (minutes). Only live-path/unknown ships
need the 544 s full gate; docs ships already take ~10 s.
- X1 Impact map (`scripts/dev/gate_impact.py`): import graph of all tracked .py built fresh each ship (about 1 s; nothing stored, so nothing stale or
  corrupt across 30 worktrees), reverse closure of the changed modules over real imports (package = its folder name; same-stem files all count). A test
  is reached when it is in the closure, references a closure module (import, path, `python x.py`, quoted dotted name, `-m pkg.mod`), names a changed
  non-.py file, or sits beside a changed conftest/`__init__`; a deleted file seeds by name. String mentions are not followed transitively (they made
  every module reach 59 tests). Live code in the closure (it imports the change) = full gate. Any error = the old whole-shard smoke selection.
- X2 `ship` passes `--fast` for smoke ships: pytest steps run only their reached files (split over workers), script-style test steps run when their test
  is reached, 3xt/5b use the closure too. Direct tests (they name the changed file) are never deferred; the transitive ones fill FAST_BUDGET_S = 30 s
  at EFFECTIVE_WORKERS = 3 (measured: 6 workers give 2-3x on this box, not 6x) by estimated seconds (STEP_EST, TEST_FILE_SECONDS); the rest is
  DEFERRED to CI and printed by name. Per-step timeout 240 s. ALWAYS steps 3w/3tl/3dl run only when a changed file, test or ride-along doc concerns them.
- X3 Fast gates use their own slot pool `gate-slots-fast` (2): never queued behind 9-minute full gates. Full/live/unknown ships keep slots and steps.
  An empty slot file is its creator mid-write (busy, not a dead owner 0) unless older than 10 s.
- X4 wiring_scan.build: suffix index + memo for `resolve`, per-file facts cached by content hash in the git common dir (a pure function of the text; a
  missing/corrupt/unwritable cache = recompute). 17 s cold becomes 1.2-1.7 s warm, so 3x and 3w no longer set the floor. `ship` also runs the
  stale-page check and the CI check on threads that overlap the push/gate.
- X5 Quarantine `scripts/dev/gate_quarantine.tsv` (test id, owner, expiry, reason): active ids are `--deselect`ed in fast gates only, read from
  origin/fast-track (a ship cannot quarantine its own failing test); expired or live-path rows deselect nothing and fail cheap step 3qn. Empty today.
- X6 `ship` prints the CI state (ci_watch; a cached red is re-fetched before it counts; offline = unknown, never a block). Two finished fast-track runs
  failed = the next code ship is blocked, fix-first. A newer run in flight does not clear a red (fast-track always has one pending). `ship --fix-ci`
  is the way through for the fix itself and runs the FULL gate, so it is not a cheap bypass. Docs/data-only ships (gate_select's definition) pass.
- Review fixes (Sonnet + Haiku, one-time, read-only): CI paths now include research .py, options, observation, .gitignore, .claude/settings.json (a
  smoke ship there had no CI run); FULL_RE gained wiring_scan, ci_watch, config_check, ci_deps_lint, run_staged_tests, gate_impact and the quarantine
  file (a smoke ship could weaken its own gate); wiring_registry.json edits run 3x/3w; race_overlap also checks incoming modules that import ours;
  live code importing the change forces the full gate; a hung step times out; command lines over 24 KB fall back; empty-slot and slot-pool fixes.
  Not taken: per-hash cache files (a lost cache update only costs one recompute) and tree-scanning tests as always-run (4d, 3gd, 3qn already are).
- Rejected: pytest-xdist (not installed, needs the ci.yml pip line; session fixtures run per worker; the gate already runs one process per step with its own
  basetemp) and pytest-testmon (one `.testmondata` per checkout and a full first run, so every fresh worktree is cold; it does not track static files or
  files tests run in a subprocess, which most of ours do; verified in testmon.org docs).
- Quality trade-off (OURS): a smoke ship no longer runs tests that reach the change only through a string mention, a subprocess call or a data file read at
  run time, nor the budget-deferred ones; CI (both OSes, whole suite, green-only deploy) runs them minutes later and a red CI now blocks the next code ship.
  Live-path, unknown paths and the gate scripts themselves keep the full gate.

## Not done (next)
Machine-wide process budget across concurrent gates; FIFO slot queue; Windows CI on selected steps only.
