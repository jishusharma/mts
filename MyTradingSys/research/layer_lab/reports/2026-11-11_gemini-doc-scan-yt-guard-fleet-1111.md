COUNTS: MATCH=8 DIFF=0 NOT_IN_DATA=0

# Audit Report: Fleet-wide YouTube Guard Implementation vs Test Suite

- **Card**: `gemini-doc-scan-yt-guard-fleet-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/fetch_captions_timed.py` (read)
  - `scripts/dev/test_yt_guard_fleet.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-yt-guard-fleet-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Guard Behaviours

An independent blind read of `scripts/dev/fetch_captions_timed.py` evaluated the core fleet-wide YouTube guard behaviours against the test suite in `scripts/dev/test_yt_guard_fleet.py`:
1. **Fleet Lockout Sharing**: Remote `ytblock` row for matching IP hash blocks local execution (`EXIT_BLOCKED=3`), while a block for a different IP hash is ignored.
2. **Local 429 Fleet Broadcast**: When HTTP 429 occurs locally, `mark_blocked()` broadcasts `ytblock` with sha256 8-char pseudonymous IP hash `ih` without revealing the raw IP address.
3. **Mid-run Block Interruption**: When a fleet block appears during batch processing, `guarded_run()` halts before initiating the next network request, marking subsequent items `UNVERIFIED`.
4. **Fleet Signal Unavailability Fallback**: When fleet signals cannot be fetched and there is no local record, `blocked_until()` emits a warning and safely fails open/proceeds with local records only.
5. **Per-IP Rolling 24 h Budget**: `spend()` checks total requests against `daily_budget()` (40 direct / 150 proxy / `YT_DAILY_BUDGET`), aggregating local requests and other machines' unexpired (`<24 h`) `ytuse` rows, raising `BudgetExceeded` and deferring without making a network request.
6. **Request Accounting Across Operations**: Channel listing, video date, and metadata queries count against `_unflushed` / budget via `spend()`.
7. **Escalating Lockout (6 / 24 / 72 h)**: Consecutive blocks escalate through `BLOCK_LEVELS_H = (6, 24, 72)` hours, syncing with fleet `ytblock` levels, and resetting back to 0 (6 h baseline) upon a clean fetch (`mark_clean()` / `ytclean`).
8. **No Second Path & Offline Status**: A 429 response prevents fallback to secondary network paths (transcript API) and avoids redundant metadata requests; `--status` reads local state and cached signals without making any network calls.

Audit outcome across the 8 behaviours:
- **MATCH (8)**: All 8 core guard behaviours implemented in `scripts/dev/fetch_captions_timed.py` are explicitly pinned and verified by unit tests in `scripts/dev/test_yt_guard_fleet.py`.
- **DIFF (0)**: None.
- **NOT_IN_DATA (0)**: None.

---

## 2. Clause Comparison Table

| # | Guard Behaviour | Implementation in `fetch_captions_timed.py` | Pinning Test in `test_yt_guard_fleet.py` | Status | file:line Quotes & Findings |
|---|---|---|---|---|---|
| 1 | Fleet lockout sharing (matching IP blocked, differing IP ignored) | `scripts/dev/fetch_captions_timed.py:219-234,307-323`: `blocked_until()` inspects `rows` from `fleet_rows()`, matches on `ip_hash(ip)`, and takes `max(local, remote)` | `scripts/dev/test_yt_guard_fleet.py:46-58`: `test_remote_429_blocks_this_machine` & `test_remote_block_for_other_ip_ignored` | MATCH | SOURCED (`fetch_captions_timed.py:233`, `test_yt_guard_fleet.py:46-58`). Code `remote = fleet_block(rows, ip_hash(ip) if ip else "")` blocks when hash matches; test confirms `assertIsNotNone(f.blocked_until())` for matching IP and `assertIsNone(f.blocked_until())` for other IP. |
| 2 | Local 429 broadcast to fleet without revealing raw IP address | `scripts/dev/fetch_captions_timed.py:96-98,413-429`: `ip_hash()` generates 8-char hex sha256 prefix; `mark_blocked()` sends `fleet_send("ytblock", ..., ih=ih, until=stamp, level=level)` | `scripts/dev/test_yt_guard_fleet.py:59-64`: `test_local_429_is_sent_to_fleet_without_the_address` | MATCH | SOURCED (`fetch_captions_timed.py:98,428`, `test_yt_guard_fleet.py:59-64`). Code hashes IP with `hashlib.sha256(("mts-yt:" + str(ip)).encode("ascii", "replace")).hexdigest()[:8]`; test verifies `'ytblock' in kinds` and `self.assertNotIn(IP, repr(self.sent))`. |
| 3 | Mid-run block appearance halts execution before next request | `scripts/dev/fetch_captions_timed.py:378-380,448-473`: `guarded_run()` calls `fetch_one()` which checks `spend()`; `spend()` raises `YTBlocked` if `blocked_until()` is active; remainder marked `UNVERIFIED` | `scripts/dev/test_yt_guard_fleet.py:65-78`: `test_block_appearing_mid_run_stops_before_next_request` | MATCH | SOURCED (`fetch_captions_timed.py:378-380,450`, `test_yt_guard_fleet.py:65-78`). When mid-run fetch encounters a block injected into fleet rows, `guarded_run` halts subsequent fetch attempts, returning `calls == [IDS[0]]` and `res[1][1] == "UNVERIFIED"`. |
| 4 | Unreadable fleet signals without local record warns and proceeds | `scripts/dev/fetch_captions_timed.py:224-229`: In `blocked_until()`, if `rows is None` and no local record, appends to `_warned` and prints `YT_GUARD WARNING...` | `scripts/dev/test_yt_guard_fleet.py:86-91`: `test_unreadable_remote_no_local_record_warns_and_proceeds` | MATCH | SOURCED (`fetch_captions_timed.py:225-229`, `test_yt_guard_fleet.py:86-91`). With `fleet_rows` returning `None`, `blocked_until()` returns `None` and prints warning; test checks `assertIsNone(f.blocked_until())` and `'WARNING' in str(c)`. |
| 5 | Rolling 24 h per-IP budget enforcement across fleet machines | `scripts/dev/fetch_captions_timed.py:359-371,374-394`: `budget_used()` counts local stamps + unexpired (`> cutoff`) `ytuse` rows from other hosts; `spend()` raises `BudgetExceeded` if used >= `daily_budget()` | `scripts/dev/test_yt_guard_fleet.py:94-108,120-125`: `test_over_budget_defers_without_request`, `test_budget_counts_other_machines_and_expires`, `test_fetch_over_budget_is_deferred` | MATCH | SOURCED (`fetch_captions_timed.py:362-371,385-386`, `test_yt_guard_fleet.py:94-108,120-125`). Code tallies other machines' unexpired `ytuse` signals; tests verify `BudgetExceeded` raised when budget met, expired entries (>24 h) ignored, and over-budget fetch returns `DEFERRED` without calling yt-dlp. |
| 6 | Network metadata and channel listing queries counted against budget | `scripts/dev/fetch_captions_timed.py:510,521,551`: `list_channel()`, `video_date()`, and `meta()` all invoke `spend(...)`, which increments `_unflushed[0]` | `scripts/dev/test_yt_guard_fleet.py:109-119`: `test_metadata_and_listing_count` | MATCH | SOURCED (`fetch_captions_timed.py:392,510,521,551`, `test_yt_guard_fleet.py:109-119`). Code calls `spend("channel listing")` and `spend("metadata")`; test calls `list_channel`, `video_date`, `meta` and asserts `self.assertEqual(f._unflushed[0], 3)`. |
| 7 | Escalating lockout intervals (6 / 24 / 72 h) and clean fetch reset | `scripts/dev/fetch_captions_timed.py:69,326-341,404-411,413-429`: `BLOCK_LEVELS_H = (6, 24, 72)`; `mark_blocked()` advances level `min(current_level + 1, 3)`; `mark_clean()` resets to level 0 and emits `ytclean` | `scripts/dev/test_yt_guard_fleet.py:127-145`: `test_6_24_72_72`, `test_clean_fetch_resets`, `test_level_follows_fleet_rows` | MATCH | SOURCED (`fetch_captions_timed.py:69,408-410,417-418`, `test_yt_guard_fleet.py:127-145`). Code steps through hours `(6, 24, 72)`; tests confirm sequential blocks give `[6, 24, 72, 72]`, `mark_clean()` resets next block to 6 h, and remote fleet rows at level 2 escalate to 72 h. |
| 8 | No second network path on 429 and offline `--status` reporting | `scripts/dev/fetch_captions_timed.py:73,432-446,611`: `ALLOW_FALLBACK = False`; 429 terminates with `BLOCKED` without calling fallback; `guard_status()` queries local block file and local signal clone with zero network calls | `scripts/dev/test_yt_guard_fleet.py:147-165,167-180`: `test_429_makes_no_fallback_or_metadata_request` & `test_status_shows_budget_and_level_without_network` | MATCH | SOURCED (`fetch_captions_timed.py:73,433-435,611`, `test_yt_guard_fleet.py:147-165,167-180`). Tested by verifying 429 produces `BLOCKED` without fallback transcript calls, and `--status` completes without calling `public_ip` network lookup. |
