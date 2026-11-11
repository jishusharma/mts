COUNTS: MATCH=12 DIFF=0 NOT_IN_DATA=0

# Independent Gemini Blind Read: A's 3xt Test Speedups (`651aab2e`) Kept Every Assertion

- **Card**: `gemini-blind-read-3xt-speedup-coverage-1111`
- **Date**: 2026-11-11 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-blind-read-3xt-speedup-coverage-1111`)
- **Scope In (read-only)**:
  - `git diff 651aab2e^1 651aab2e^2` across 5 files:
    1. `MyTradingSys/research/context_null_2026-10-16/context_null.py`
    2. `MyTradingSys/research/context_null_2026-10-16/test_context_null.py`
    3. `MyTradingSys/tools/live_aid/test_live_aid_replay.py`
    4. `scripts/dev/test_refresh_main_checkout.py`
    5. `scripts/dev/test_refresh_main_checkout_errors.py`
  - The same 5 files at `origin/fast-track` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-3xt-speedup-coverage-1111.md` (this report)
- **Scope Out Respected**:
  - No edit to the source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`.
- **Audit Mandate**:
  - Verify every assertion removed or rewritten in the 3xt speedup diff (`git diff 651aab2e^1 651aab2e^2`) is still made elsewhere or is genuinely redundant.
  - Verify behavior change in `context_null.py` (and dropped FFT in `phase_tag`) preserves reported study numbers.

---

## 1. Executive Summary

- Total target clauses audited: **12**
- Audit result: **MATCH = 12, DIFF = 0, NOT_IN_DATA = 0**
- Coverage integrity: **100% PRESERVED**. Every assertion rewritten, refactored, or removed across all 5 audited test and implementation files remains fully asserted with equivalent or identical semantics.
- `context_null.py`: The `_terciles` replacement of `np.quantile` uses numpy's exact linear interpolation formula with `np.partition`, bit-for-bit identical to `np.quantile(w, [1/3, 2/3])`, verified by new equivalence test `test_terciles_equal_np_quantile_bitwise` (600 random windows with ties and varying sizes). No reported study numbers are changed.
- `phase_tag`: As noted in commit `238a40e64`, the FFT shortcut in `phase_tag/harness.py` was completely reverted prior to `651aab2e^1`, so the original roll loop was kept and zero behavior or study numbers changed.

---

## 2. Clause Audit Table

| # | File & Line (`651aab2e^1` vs `651aab2e^2` / `origin/fast-track`) | Removed / Rewritten Clause | Status | Coverage Location & Verification (SOURCED / OURS) |
|---|---|---|---|---|
| 1 | `MyTradingSys/research/context_null_2026-10-16/context_null.py:108` vs `108-128` | Rewritten: `c1, c2 = np.quantile(w, [1.0 / 3.0, 2.0 / 3.0])` -> `c1, c2 = _terciles(w)` with helper `def _terciles(w)` | `MATCH` | SOURCED (`context_null.py:112-128`): Implementation uses `np.partition` at `lo, hi = floor(v), min(floor(v)+1, n-1)` where `v = (n-1)*[1/3, 2/3]`, followed by linear interpolation matching NumPy's `method="linear"`. Verified bitwise equal to `np.quantile` across 600 random iterations with ties in `test_context_null.py:189-198`. |
| 2 | `MyTradingSys/research/context_null_2026-10-16/test_context_null.py:117-122` | Rewritten: `test_trigger_effect_recovered()` ran fresh `CN.run(C, ev, h=H, d=D, cfg=cfg)` -> uses `@functools.lru_cache` shared fixture `_trigger_run()` | `MATCH` | SOURCED (`test_context_null.py:117-129`): All assertions (`check_trigger_recovered(res)`, `assert abs(res["context_effect"]) < 3 * res["context_se"] + 1e-9`) are 100% preserved. Caching is safe because `run()` does not mutate its inputs or outputs. |
| 3 | `MyTradingSys/research/context_null_2026-10-16/test_context_null.py:244-245` vs `261` | Rewritten: `test_controls_avoid_event_windows()` ran fresh `CN.run(...)` -> reads shared fixture `_trigger_run()` | `MATCH` | SOURCED (`test_context_null.py:260-263`): Assertion `assert abs(res["control_mean"]) < 0.01, res["control_mean"]` is identical and evaluated on the same fixture output. |
| 4 | `MyTradingSys/research/context_null_2026-10-16/test_context_null.py:189-198` | Added test: `test_terciles_equal_np_quantile_bitwise()` | `MATCH` | SOURCED (`test_context_null.py:189-198`): Adds bitwise equivalence assertions `assert CN._terciles(w) == (want[0], want[1])` across 600 random windows (including ties `if i % 3 == 0: w = np.round(w, 1)` and lengths from 2 to 400). |
| 5 | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:126-130` | Rewritten: bare wait `try: page.wait_for_selector("#strip td.x", ...)` guarded by `if fixture:` | `MATCH` | SOURCED (`test_live_aid_replay.py:126-130`): In non-fixture runs, `#strip td.x` never appears (empty data), so the 5 s timeout was pure dead time. In fixture runs (`fixture=True`), `wait_for_selector` still executes with the exact same try/except pass block. |
| 6 | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:157,173,185` | Rewritten: `open_replay(...)` -> `open_replay_cached(...)` in `test_rendered_strip_matches_python_maths` and `test_short_windows_read_not_in_data` | `MATCH` | SOURCED (`test_live_aid_replay.py:140-147,169,185`): Caches result by `(fixture, wrap)` key for read-only checks on frozen-clock fixture. All assertions on `errs`, `visible`, `strip_problems(rows)`, and `NOT_IN_DATA` in short windows remain 100% intact. |
| 7 | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:219-242` | Rewritten: `_cal_text(...)` loop refactored into batched `_cal_texts(...)` | `MATCH` | SOURCED (`test_live_aid_replay.py:219-245`): Batches page creation across cases before awaiting the 1.3 s render timeout, returning identical `(page.inner_text("#mc-next"), page.inner_text("#mc-sub"), page.eval_on_selector_all("#mc-rows tr", ...))`. `_cal_text` delegates to `_cal_texts(browser, [(iso_now, events)])[0]`. All test assertions in caller tests remain unchanged. |
| 8 | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:260-267` | Rewritten: `test_calendar_time_honesty_at_the_event_minute` calls `_cal_texts(browser, [case1, case2])` instead of two sequential `_cal_text` calls | `MATCH` | SOURCED (`test_live_aid_replay.py:260-267`): Assertions `assert nxt == "none left"`, `assert [r[1] for r in rows][0] == "Advance GDP q/q" and len(rows) == 3`, `assert "-" not in nxt`, and `assert "Advance GDP q/q" not in [r[1] for r in rows2]` are bitwise identical. |
| 9 | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:277-293` | Rewritten: `test_no_calendar_on_429_then_numbers_on_200` batches both 429 and 200 page loads concurrently with a single `wait_for_timeout(1500)` | `MATCH` | SOURCED (`test_live_aid_replay.py:277-293`): The loop over `opened` verifies both pages: `assert nxt == "in 30 min"` for 200, and `assert nxt == "NO CALENDAR" and "429" in page.inner_text("#mc-sub") and page.query_selector_all("#mc-rows tr") == []` for 429. Exactly the same assertions as sequential code. |
| 10 | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:307-349` | Rewritten: sequential `_snap_page_text` calls refactored to batched `_snap_pages_text` | `MATCH` | SOURCED (`test_live_aid_replay.py:307-349`): Evaluates the 4 snapshot cases (`fresh`, `old`, `missing`, `unreadable`) concurrently. Exact assertions checked: `assert nxt == "in 30 min" and "Advance GDP q/q at 12:30Z" in sub`, `assert nxt == "NO CALENDAR"` (for old and unreadable), and `assert nxt == "NO CALENDAR" and "no snapshot file" in sub` (for missing). No assertion lost. |
| 11 | `scripts/dev/test_refresh_main_checkout.py:27-52` | Rewritten: per-test git repo creation in `setUp()` replaced by `setUpModule()` / `_build_template()` and `shutil.copytree` in `setUp()` | `MATCH` | SOURCED (`test_refresh_main_checkout.py:27-52`): The baseline git repository (bare origin, fast-track clone with dummy user config, commits a, b, c) is generated once in `setUpModule()`. Each test gets a clean, independent `shutil.copytree` copy and resets the origin url with `git remote set-url origin`. All 15 test methods and every assertion (`assertEqual`, `assertTrue`, git branch status) are preserved identically without any modification. |
| 12 | `scripts/dev/test_refresh_main_checkout_errors.py:28-53` | Rewritten: per-test git repo creation replaced by `setUpModule()` / `_build_template()` and `shutil.copytree` in `setUp()` | `MATCH` | SOURCED (`test_refresh_main_checkout_errors.py:28-53`): Identical template optimization as in `test_refresh_main_checkout.py`. All 6 error test methods and their assertions (verifying exit codes, error messages on dirty trees, missing branches, detached heads) remain untouched and fully preserved. |

---

## 3. Verification Commands & Outputs

- `python -m pytest MyTradingSys/research/context_null_2026-10-16/test_context_null.py`
  - Output: `11 passed in 9.10s` (OURS)
- `python -m pytest scripts/dev/test_refresh_main_checkout.py scripts/dev/test_refresh_main_checkout_errors.py`
  - Output: `21 passed in 16.99s` (OURS)
- Git diff verification:
  - `git diff 651aab2e origin/fast-track -- <5 files>` is completely empty (OURS).
  - All 5 files on `origin/fast-track` match `651aab2e^1` (the sped-up code committed by A and merged in `651aab2e`).
