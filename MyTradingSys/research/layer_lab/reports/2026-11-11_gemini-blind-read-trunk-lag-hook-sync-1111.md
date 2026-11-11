Counts: MATCH: 4, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/dev/trunk_lag.py` (sync_hook_files, release_synced, main_checkout, catch_up)

- **Card ID**: `gemini-blind-read-trunk-lag-hook-sync-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In Read**:
  - `scripts/dev/trunk_lag.py` (`_hook_state`, `_ours`, `sync_hook_files`, `release_synced`, `main_checkout`, `catch_up`)
  - `scripts/dev/test_trunk_lag.py` (`test_blocked_main_checkout_still_gets_trunk_hook_scripts`, `test_main_checkout_with_an_edit_trunk_does_not_touch_fast_forwards_and_keeps_it`, `test_session_start_fast_forwards_a_clean_trunk_checkout_only`)
- **Report Target**: `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-trunk-lag-hook-sync-1111.md`

---

## Verification Table

| Clause ID | Clause Description | Target Functions / Sources | Status | File:Line Citations & Detailed Audit Findings |
|---|---|---|---|---|
| C1 | (1) a dirty hook file not written by the sync is left alone | `scripts/dev/trunk_lag.py:216-222,235,241,268` | MATCH | **`scripts/dev/trunk_lag.py:218-219`**: `if path in dirty: return False` in `_ours(path, head, index, dirty, record)`. Dirty paths (worktree modified vs index via `_blobs(repo, "diff", "--name-only", ...)` at line 212) are explicitly excluded from `_ours`.<br>**`scripts/dev/trunk_lag.py:235`**: in `sync_hook_files`, if `index.get(p) == t and p not in dirty: continue`. Untracked files or deleted paths are also skipped (`scripts/dev/trunk_lag.py:237-239`). Only if `_ours(...)` returns True (unedited vs HEAD or matching prior sync record without worktree dirty) is path appended to `take` (`scripts/dev/trunk_lag.py:241-242`).<br>**`scripts/dev/trunk_lag.py:268`**: in `release_synced`, `foreign = {p for p in paths if not (p in record and index.get(p) == record[p] and p not in dirty)}`; dirty hook files or files not matching `record` are treated as foreign and left alone, aborting fast-forward if trunk changed them (`scripts/dev/trunk_lag.py:269-270`). Verified in test at [test_trunk_lag.py:171,176](file:///F:/MTS/gq/gemini-blind-read-trunk-lag-hook-sync-1111/scripts/dev/test_trunk_lag.py#L171-L176): `someone's edit` in `mine.py` is preserved intact. |
| C2 | (2) a file the sync wrote is refreshed when trunk changes | `scripts/dev/trunk_lag.py:216-222,233-255` | MATCH | **`scripts/dev/trunk_lag.py:221`**: `_ours` returns True if `i == record.get(path)` when `path not in dirty`, recognizing a path previously updated and recorded by `sync_hook_files`.<br>**`scripts/dev/trunk_lag.py:234-242`**: in `sync_hook_files`, iterates `trunk.items()`. When trunk blob `t != index.get(p)` and `_ours(p, ...)` returns True because index matches recorded sync blob `record.get(p)`, path is added to `take` and checked out (`scripts/dev/trunk_lag.py:246`).<br>**`scripts/dev/trunk_lag.py:249-252`**: `record.update({p: trunk[p] for p in done})` and writes back to `_record_path(repo)` (`mts_hook_sync.json`). Verified in test at [test_trunk_lag.py:180-188](file:///F:/MTS/gq/gemini-blind-read-trunk-lag-hook-sync-1111/scripts/dev/test_trunk_lag.py#L180-L188): updating `hook.py` from v2 to v3 on origin re-syncs to v3 via `sync_hook_files`. |
| C3 | (3) release_synced drops a record only when the working bytes equal HEAD | `scripts/dev/trunk_lag.py:258-282` | MATCH | **`scripts/dev/trunk_lag.py:268`**: `foreign = {p for p in paths if not (p in record and index.get(p) == record[p] and p not in dirty)}`. Only paths that cleanly match `record` (staged as sync recorded and worktree not dirty) are handled for rollback.<br>**`scripts/dev/trunk_lag.py:271-275`**: paths in `head` are checked out back to `HEAD` via `git(repo, "checkout", "HEAD", "--", *back, timeout=60)`; if checkout fails (non-zero return code), returns `False` without releasing.<br>**`scripts/dev/trunk_lag.py:276-281`**: new paths not in `head` are un-cached and unlinked from worktree. Once `fast_forward` succeeds (`scripts/dev/trunk_lag.py:167`), working bytes and index are merged to trunk `HEAD`, clearing divergence. |
| C4 | (4) git failure or timeout leaves the tree unchanged | `scripts/dev/trunk_lag.py:45-48,246-248,274-275,293-314` | MATCH | **`scripts/dev/trunk_lag.py:45-48`**: `git()` wraps subprocess calls with timeouts (`timeout=60` in checkout at line 246 and line 274; default `GIT_TIMEOUT_S = 8` or `MTS_TRUNK_LAG_GIT_TIMEOUT`).<br>**`scripts/dev/trunk_lag.py:246-248`**: chunk checkout in `sync_hook_files` executes `git checkout origin/{TRUNK} -- *chunk`; if `returncode != 0` (or raises on timeout), `done` is not extended with failed chunk, `record` is not updated with unapplied paths (`scripts/dev/trunk_lag.py:249`).<br>**`scripts/dev/trunk_lag.py:274-275`**: in `release_synced`, if checking out `HEAD` fails, function immediately returns `False` without unlinking new files, causing `fast_forward` to abort cleanly (`scripts/dev/trunk_lag.py:157-158`).<br>**`scripts/dev/trunk_lag.py:167-168`**: `fast_forward` performs `merge --ff-only`; if non-zero, returns `0, False`, leaving working tree untouched. |

---

## Summary of Findings

- Total clauses audited: 4
- **MATCH**: 4
- **DIFF**: 0
- **NOT_IN_DATA**: 0
- All 4 clauses are accurately implemented in `scripts/dev/trunk_lag.py` and covered by tests in `scripts/dev/test_trunk_lag.py`.
