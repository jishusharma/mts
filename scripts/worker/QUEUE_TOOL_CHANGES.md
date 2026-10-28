# queue_tool.py.new - changes

Fixes audit findings 1, 2 and 4 (`MyTradingSys/research/fast_track_2026-09-27/DEV_VELOCITY_AUDIT.md`).
Smallest-change patch on top of the current `queue_tool.py`; nothing existing was modified in place.

1. **False-BLOCKED on new-file proposals (Finding 1)**
   - New repeatable spec header `CREATE: relative/path` (bare paths, comma-separated).
     `pack` resolves and stores it as `task["create"]`.
   - `verify_one`'s "unknown file name" check now also treats as known: CREATE paths,
     and any `<<<FILE ...>>>` header the model wrote (even one whose closing marker
     never matched, so its content leaked into "prose" -- this is what actually
     produced 011/012/013's false FAILs).
   - A path-looking (`a/b.py`) unknown reference still FAILs (a genuinely invented
     file path); a bare, no-slash unknown reference is downgraded to a review/warning
     line (kept, not blocking) -- covers literals like `2026-01-01.csv` inside test data.
   - The scope-vs-proposal write gate (`verify_one` step 4) now also accepts a
     proposal target that's in `create`, and writes it to `<path>.new` exactly like
     an existing-file edit (same code path as before, no special-casing needed).

2. **Compile/test gate (Finding 2)**
   - After proposals are written, every proposed `.py` is `py_compile`'d in a fresh
     temp dir (copy, `.py` suffix, 30s timeout) -> syntax failure forces FAIL.
   - If both `X.py` and `test_X.py` were proposed, the pair is copied into one temp
     dir and run with `python -m unittest test_X` (120s timeout); failing/erroring
     tests are named and force REVIEW; a clean run adds a `compile OK, tests N/N`
     note. Nothing from the real repo is ever executed, only the copies.

3. **Spec linter (Finding 4)**
   - `check_bare_path_line()` rejects a SCOPE/CREATE entry containing a space or
     parentheses, with a message pointing at the offending entry.
   - New `queue_tool.py lint SPEC [SPEC ...]` subcommand runs only this check
     (no SCOPE resolution, no packing).

4. **Re-verify by id**: already worked (`verify <id>` always re-runs and
   overwrites that id's `.verdict.txt`); no change needed.

No `QUEUE_ROOT` env override was added: `REPO` is derived from `__file__`'s
location, and the scratch test below reproduces the same relative folder layout,
so the existing behaviour already worked unmodified for testing.

## Test evidence (scratch dir, outside mnt/, real done/ untouched)

Setup: `$HOME/qt_test/{scripts/worker/queue_tool.py.new, Dumps/workers/NUC-QUEUE/done/{011,014}.*}`,
plus a dummy `MyTradingSys/backtest/bt/README.md`. `011`/`014` task.json copies were
given a `"create"` field (what `pack` would have produced had their specs used the
new `CREATE:` header -- the real specs were not touched).

```
$ python3 scripts/worker/queue_tool.py.new verify 011-bt-data-loaders
...
FINDINGS: verdict REVIEW; expected 5/5; unknown file names 0; proposals 1
  - name not found in scope or repository, referenced only in code/text: 2026-01-01.csv
  - name not found in scope or repository, referenced only in code/text: 2026-01-02.csv
  - proposal MyTradingSys/backtest/bt/bt_data.py.new: +133 -0 lines
  - compile OK (no matching test_*.py proposal to run)
```
Before the fix this was `unknown file names 5` / `STATUS: BLOCKED`; now 0 unknown
names and `bt_data.py` compiles clean. (The reply's own second `<<<FILE
test_bt_data.py>>>` block has a malformed closing marker -- `>>>>>>>END FILE`
instead of `>>>END FILE` -- so that file isn't recognized as a proposal by
either the old or new tool; separate issue, not in scope here.)

```
$ python3 scripts/worker/queue_tool.py.new verify 014-bt-stats
...
FINDINGS: verdict FAIL; expected 6/6; unknown file names 0; proposals 2
  - syntax error in proposal MyTradingSys/backtest/bt/bt_stats.py: SyntaxError: invalid syntax. Perhaps you forgot a comma?
```
014 is correctly BLOCKED again, now for the real reason (the `for i i in
oos_indices` syntax error the audit found), not for a false file-name reason.

Lint:
```
$ python3 scripts/worker/queue_tool.py.new lint 901-lint-bad.md
REFUSED 901-lint-bad.md: CREATE entry is not a bare path (looks like prose): '...'
```

`pack` with a `CREATE:` line stores it correctly in the resulting task.json
(`"create": ["MyTradingSys/backtest/bt/new_thing.py", ...]`); verified in scratch.

`scripts/worker/queue_tool.py.new` also passes `python3 -m py_compile`.
