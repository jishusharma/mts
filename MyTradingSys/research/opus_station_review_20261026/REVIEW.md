# Claude Opus Review: Coordination Audit, AI-Health and Rolling Sessions

Review executed on JIS-NUC under operator authorization (2026-10-26, card `opus-station-review-act`).
Audited base: `3dc47d91d` (coordination audit) / `ec00608e9`, `3ed1c8b9a` (cloud AI-health), `05b22b756` (rolling audit), `ce8194ba2` (parent reproduction run).
Current trunk evaluated: `4e79a8a0c` / `a177bb682`.

---

## 1. Finding Verdicts & Status Matrix

Evaluated via hermetic per-finding recheck (`MyTradingSys/research/opus_station_review_20261026/recheck.py`, isolated clones, no network or production writes).

| # | Grouped Finding | Repro Key | Status on Current Trunk | Disposition | Proof & File Reference |
|---|---|---|---|---|---|
| **1** | Racing claim push overwrite | `racing_claims_both_succeed` | **FIXED in this change** | **ACCEPT** | `sync.py:1244` (`push_claim_commit`), `sync.py:1330` (`claim`). Push loop now executes push guard `still_free` against the fetched parent before committing; refuses collisions and area overlaps. Fail-first tests: `scripts/dev/test_sync.py::SyncTest::test_racing_claim_*` |
| **2A**| Single canonical claims reader | `tasks_misses_side_claim` | **FIXED in this change** | **ACCEPT** | `tasks.py:522` (`open_claims`), `codex_run.py:803`, `lane_health.py:392`. Pointed to `sync.open_claims(repo, fetch=False)` (side branch + legacy trunk). Fail-first test: `scripts/dev/test_tasks.py::NextSkipsClaimedTest::test_next_skips_a_card_claimed_on_the_claims_side_branch` |
| **2B**| Fetch does not refresh dispatch snapshot | `fetch_does_not_refresh_dispatch` | REPRODUCED | **ACCEPT** | `supervisor.py:101` reads working tree cards rather than fetched ref snapshot. Deferred to successor card. |
| **2C**| Dispatch bypasses stop tag | `dispatch_bypasses_stop_tag` | **ALREADY FIXED upstream** | **ALREADY FIXED** | Resolved in commit `d2e575feb` (`tasks.py:1430` stop_tag check in `exclusion()`). |
| **3** | Green completion not watched | `green_completion_not_watched` | REPRODUCED | **ACCEPT** | `supervisor.py:386` drops `on_green` and gate pool status. Deferred to successor card. |
| **4A**| Failed ship emits done signal | `failed_ship_emits_done` | REPRODUCED | **ACCEPT (ALREADY CARDED)** | Covered by existing card `ship-signal-send-done-only-on-a-complete`. |
| **4B**| Timeout cached as pass | `timeout_cached_as_pass` | REPRODUCED | **ACCEPT** | `run_all_tests.py:235` returns `True` on step timeout when `TIMEOUT_DEFERS=True`. Deferred to successor card. |
| **4C**| Ship wall excludes CI wait | `ship_wall_excludes_ci_wait` | REPRODUCED | **ACCEPT (ALREADY CARDED)** | Covered by existing card `bug-session-handoff-ship-speed-audit`. |
| **5A**| Uninvoked tool passes wiring gate | `uninvoked_tool_passes_wiring` | REPRODUCED | **ACCEPT (OBSERVATION)** | Wiring check is inventory-based; behavior tested via unit/integration suites. |
| **5B**| Supervisor host-alias test failure | `test_supervisor.py:446` | REPRODUCED | **ACCEPT** | Stale host-alias expectation in test fixture. Excluded from gate; needs dedicated repair card. |
| **5C**| git log ban in doc tests | doc integrity check | REPRODUCED | **ACCEPT (LOW PRIO)** | Invariant doc check rule. |
| **6** | Worker brief drops context contract | `worker_brief_drops_context_contract` | REPRODUCED | **ACCEPT** | `supervisor.py:589` omits card context/reads/tests/done_when. Needs card renderer integration. |
| **7** | Full card ID release mismatch | `gemini_full_id_release_mismatch` | **FIXED in this change** | **ACCEPT** | `gemini_queue.py:96` now releases `sync.slugify(card)` matching the 40-char slug created on claim. Fail-first test: `MyTradingSys/tests/test_gemini_claim_skip.py::ReleaseSlugTest::test_run_job_releases_the_slug_the_claim_was_filed_under` |

---

## 2. Implemented & Verified First Repairs

1. **Race-safe claim push validation (`Finding 1`)**:
   - `sync.py`: Added `guard` parameter to `push_claim_commit`. `sync.claim` now validates the candidate slug and overlapping areas against the parent commit on every push retry. If another worker's claim landed, `SyncError` is raised immediately.
   - Tests added in `scripts/dev/test_sync.py`:
     - `test_racing_claim_on_the_same_task_does_not_overwrite_the_winner`
     - `test_racing_claim_with_an_overlapping_area_is_refused`
     - `test_racing_claim_with_disjoint_areas_both_land`

2. **Unified claims discovery (`Finding 2A`)**:
   - `tasks.py`: Updated `open_claims()` to query `sync.open_claims(repo, fetch=False)` rather than trunk-only `read_claims`.
   - `codex_run.py` & `lane_health.py`: Updated claim readers to use unified side-branch aware claims query.
   - Test added in `scripts/dev/test_tasks.py`:
     - `test_next_skips_a_card_claimed_on_the_claims_side_branch`

3. **Gemini queue release slug fix (`Finding 7`)**:
   - `gemini_queue.py`: Changed `release` invocation to pass `sync.slugify(card)` instead of raw `card` id.
   - Test added in `MyTradingSys/tests/test_gemini_claim_skip.py`:
     - `test_run_job_releases_the_slug_the_claim_was_filed_under`

---

## 3. Test Evidence

- **Pre-change failure (fail-first proof)**:
  - `scripts/dev/test_sync.py` racing claim tests: FAILED (asserted winner was silently overwritten).
  - `scripts/dev/test_tasks.py` side-branch claim test: FAILED (asserted `b1` was not found in trunk-only claims).
  - `MyTradingSys/tests/test_gemini_claim_skip.py`: FAILED (asserted full 60-char card id was passed to release).
- **Post-change verification**:
  - `scripts/dev/test_sync.py` + `scripts/dev/test_tasks.py` + `MyTradingSys/tests/test_gemini_claim_skip.py`:
    **245 passed, 990 subtests passed** in 190.74s.
  - Recheck runner: 8 reproduced, 4 not reproduced (3 fixed here + 1 already fixed upstream), 0 errors.

---

## 4. Bounded Successor Cards for Remaining Work

The following successor work remains and is mapped to existing or ready cards:
1. `ship-signal-send-done-only-on-a-complete`: Fixes finding 4A (signal `done` only emitted on successful ship).
2. `bug-session-handoff-ship-speed-audit`: Fixes finding 4C (ship wall time accounting for CI wait).
3. `supervisor-dispatch-pinned-snapshot`: Successor for finding 2B (dispatch reads from fetched trunk snapshot).
4. `supervisor-watcher-probe-pools`: Successor for finding 3 (watcher probe green-completion and fast/full gate slots).
5. `run-all-tests-deferred-result-status`: Successor for finding 4B (recording DEFERRED separately from PASS).
6. `supervisor-brief-context-contract`: Successor for finding 6 (`supervisor.brief` delegates to `tasks.brief`).
7. `test-supervisor-host-alias-fix`: Successor for finding 5B (restore `test_supervisor.py` into test matrix with current host aliases).
