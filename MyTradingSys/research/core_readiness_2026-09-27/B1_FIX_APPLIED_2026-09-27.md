# B1 fix applied + re-verified — 2026-09-27 (Sonnet, continuing Opus handoff)

Status: **fix applied to `scripts/core/start-trading-day.ps1.new`, re-verified against real data. Still not committed — awaiting your review per protocol.**

## What was done
Applied the exact one-line fix Opus specified in `B1_OPUS_REVIEW.md`, verbatim:

```powershell
if ($status -eq "aligned" -or $status -eq "contradiction") { $pd = $status }
elseif (-not $status -and -not $snap.setup_candidates) { $pd = "aligned" }
```

Location: `scripts/core/start-trading-day.ps1.new`, right after the existing status check (line ~465, inside the `build_mo_cli` try block, after `$mo` is parsed). `$snap` was already in scope (loaded at line 444), confirmed before editing.

- Backup of the pre-fix `.new` kept at `scripts/core/start-trading-day.ps1.new.bak_preB1fix`.
- Isolated diff at `research/core_readiness_2026-09-27/B1_fix.diff` (one added line).
- No other files touched. `.ps1` itself (the live, non-`.new` file) was **not** touched, per your no-direct-live-write rule.

## Verification performed (Linux side, can't execute PowerShell here)
Built a throwaway scratch copy under `_scratch_b1_verify/` (repo-local, gitignored-worthy, **not committed, safe to delete**) with:
- `backtest/verdict.py` = `verdict.py.new` (the already-fixed Python port, unchanged by me — matches the `.ps1.new` fix line-for-line: `if pd is None and not (snap.get("setup_candidates") or []): return "aligned"`)
- `runtime/build_mo_cli.py` = `build_mo_cli.py.new`
- symlinks to the real `runtime_data/snapshots` (9289 files) and `runtime_data/apparatus_log.txt` so the harness runs against actual data, not synthetic.

Results:
- **`fail_closed_spec.py`**: S1 PASS, S2 PASS (0/9287 real snapshots leak WATCH/SETUP_FORMING under fail_closed) — first real run with actual snapshot data (Opus's note said "predates this fix" but the earlier run also seems to have had 0 snapshots loaded from wherever it ran; this run loaded all 9287).
- **`verdict_golden.py`**: `NO CHANGE vs baseline` (9160 compared, 126 new since baseline, 0 diffs) — confirms `verdict.py.new`'s fix doesn't regress any already-frozen verdict.
- **`parity.py`**: `PARITY 838 / 841`, the same 3 pre-existing "known live-side misses" pattern the file's own docstring documents (541/544 as of 2026-09-26; log has grown to 841 matched lines since, ratio/miss-count is consistent, no *new* misses introduced).

## What is NOT verified (can't be, from here)
- The actual live `.ps1` execution on a running candle loop — no PowerShell available in this environment. The fix is a straight textual mirror of the already-verified `verdict.py.new` logic, using a field name (`setup_candidates`) confirmed present on the raw snapshot JSON (`math_object_builder.py:359,379`), so risk is low, but it hasn't been *run*.
- Opus's open question — whether WATCH/SETUP_FORMING can occur with zero `setup_candidates` (i.e., whether the bug also changed live verdicts, not just the logged `pd`/parity) — is still unchecked. Worth a quick grep/inspection of `compute_verdict`'s branches before you commit, if you want that closed out too.
- The `fail_closed` cutover for `parity.py`/`replay.py` (still default `fail_closed=False`) — Opus flagged this as a decision for you (pick a timestamp before old/new logs mix). Untouched, still open.

## Cleanup
`_scratch_b1_verify/` is disposable — delete it whenever; it's not referenced by anything and wasn't added to git.

## Bottom line
B1 is now fix-complete in the `.new` files (all three), and both regression harnesses pass clean against real data. Recommend: review `B1_fix.diff`, then commit `verdict.py.new`, `build_mo_cli.py.new`, `start-trading-day.ps1.new` over their live counterparts together (they're a matched set), then decide the fail_closed cutover timestamp for parity.py/replay.py before mixing old/new logs.
