# Vacuous-test audit: last 30 test-adding commits (2026-10-31)

Method: for each commit, a detached throwaway worktree at the parent; the commit's version of each touched test file is copied in and only the newly added test functions are run (`pytest -k`, MTS_REPO_ROOT = that worktree). `fails-on-old` Y = fails or errors on the parent code (including ImportError/collect error because the code under test did not exist yet: a weaker Y, marked `Y*`); N = passes on old code = vacuous for this gate; skip = skipped (Chromium/fixture absent), unproven. Reverts/reapplies excluded. Script: audit run from the session scratchpad; commits are the 30 newest non-revert commits adding `def test_` to a test file.

| sha | commit | new tests | fails-on-old Y (strict / import-error*) | N | skip |
|---|---|---|---|---|---|
| 12b43fe17 | AIBridge 0.7.3: run-lock expiry (B210), task gate FAILED=FAIL, kind fr | 6 | 5 / 0 | 1 | 0 |
| 908cbb858 | gemini_queue: serialise git worktree setup with lock + retry; GOLAS-B  | 5 | 5 / 0 | 0 | 0 |
| 2a758b657 | cbp: all 10 analysts, bottom-call + alt verdicts per video, dashboard  | 1 | 1 / 0 | 0 | 0 |
| bb7731974 | ship: 7 file(s) | 5 | 1 / 4 | 0 | 0 |
| e31013dfb | T058 per-TF break event study re-land (ledger P0-45): W/1D/4h/1h/15m,  | 4 | 0 / 4 | 0 | 0 |
| f17fb6f75 | Main checkout fast-forwards past local edits trunk does not touch | 1 | 1 / 0 | 0 | 0 |
| 92aa0ab3d | ship: 6 file(s) | 5 | 0 / 0 | 1 | 4 |
| 2037b9246 | Supervisor never idle with ready work: role rule, re-arm after compact | 4 | 4 / 0 | 0 | 0 |
| 2877e1fed | G7: BTCUSDT stop-slippage proxy from public aggTrades by volatility te | 10 | 0 / 10 | 0 | 0 |
| a43b9fbff | B163 v2: run Alpha vs buy-and-hold and Beta per-sweep on DEV/VAL; RESU | 4 | 0 / 4 | 0 | 0 |
| b3442d6ca | super sessions: D11 work programme (streams, order, failure modes, tes | 1 | 1 / 0 | 0 | 0 |
| 46cb4255e | splits module + holdout guard; BB state map re-run DEV-only | 6 | 0 / 6 | 0 | 0 |
| 8582e5678 | Supervisors keep going for the work period; stop guard finds role-less | 5 | 5 / 0 | 0 | 0 |
| 36f311c44 | artifact testing: four-layer design (ARTIFACT_TESTING.md) + layer 3 ga | 3 | 0 / 0 | 0 | 3 |
| 589685fbb | analyst levels: no hit before the video could exist; cbp_run prompt ca | 4 | 3 / 0 | 1 | 0 |
| 135c8a848 | token_audit: per-session load_tokens and thinking_chars columns (A3-20 | 1 | 1 / 0 | 0 | 0 |
| 122323253 | live_aid: US open ladder (if up / if down) with measured reach and hol | 1 | 1 / 0 | 0 | 0 |
| 876dcb791 | shot.py: worktree hook runs use the shared screenshot store even when  | 1 | 1 / 0 | 0 | 0 |
| 966f15bbc | Chart paste rebuilds live_aid analyst_data.js | 1 | 1 / 0 | 0 | 0 |
| c409e3f6b | WHERE_IS: re-apply topic index and where_is.py without role-file lines | 2 | 2 / 0 | 0 | 0 |
| 1448911c7 | live_aid: verdict board + analysts panel (every roster analyst, levels | 7 | 6 / 1 | 0 | 0 |
| f8c5e4895 | live_aid: news headline panel, pulse tile, word tags (Tree News REST) | 2 | 2 / 0 | 0 | 0 |
| 14f601e2c | Wire CBP analyst levels into every chart read (analyst_levels.py) | 5 | 0 / 5 | 0 | 0 |
| 2d7d4d49c | fix-single-cost-module: test_no_own_costs + frozen cost allowlist, fee | 6 | 6 / 0 | 0 | 0 |
| 2210e9d77 | Land phone-chat uploads from the parent folder in any MTS session | 2 | 1 / 0 | 1 | 0 |
| 792ae66b6 | Add on-demand fix_verifier.py (ledger A4-18) | 5 | 0 / 5 | 0 | 0 |
| d3570f13b | Retire headless successor wake as handover default; claude -p ok prefl | 8 | 8 / 0 | 0 | 0 |
| f20eeed04 | US open countdown line: pure DST-aware function + tests (T054 step 5) | 8 | 0 / 8 | 0 | 0 |
| 50b9036ff | lab gpt-spec-tests-check-sourced-params: DONE (build) | 9 | 5 / 0 | 4 | 0 |
| 99ff967f2 | asks audit: LEDGER (319 distinct asks), 20 cards for OPEN+relevant, ga | 1 | 1 / 0 | 0 | 0 |

## Vacuous (pass on old code) and unproven tests

| sha | test | fails-on-old |
|---|---|---|
| 12b43fe17 | MyTradingSys/tests/test_aibridge_cmd_kind.py::test_real_writes_still_write | N |
| 92aa0ab3d | MyTradingSys/tools/live_aid/test_live_aid_replay.py::test_fixture_is_the_expected_window | N |
| 92aa0ab3d | MyTradingSys/tools/live_aid/test_live_aid_replay.py::test_missing_fixture_reads_not_in_data | skip (unproven) |
| 92aa0ab3d | MyTradingSys/tools/live_aid/test_live_aid_replay.py::test_rendered_strip_matches_python_maths | skip (unproven) |
| 92aa0ab3d | MyTradingSys/tools/live_aid/test_live_aid_replay.py::test_short_windows_read_not_in_data | skip (unproven) |
| 92aa0ab3d | MyTradingSys/tools/live_aid/test_live_aid_replay.py::test_wrapped_rsi_is_caught | skip (unproven) |
| 36f311c44 | scripts/dev/test_artifact_pages.py::test_live_aid_fails_closed_without_feeds | skip (unproven) |
| 36f311c44 | scripts/dev/test_artifact_pages.py::test_page_opens_clean_offline | skip (unproven) |
| 36f311c44 | scripts/dev/test_artifact_pages.py::test_planted_defects_are_caught | skip (unproven) |
| 589685fbb | scripts/dev/test_analyst_levels.py::test_k_on_both_bounds | N |
| 2210e9d77 | scripts/dev/test_shot.py::test_hook_skips_old_parent_uploads | N |
| 50b9036ff | scripts/dev/test_check_sourced_params.py::test_allowlist_expiry_at_limit_is_still_allowed | N |
| 50b9036ff | scripts/dev/test_check_sourced_params.py::test_allowlist_one_day_above_expiry_fails | N |
| 50b9036ff | scripts/dev/test_check_sourced_params.py::test_allowlist_one_day_below_expiry_is_allowed | N |
| 50b9036ff | scripts/dev/test_check_sourced_params.py::test_missing_root_value_is_reported_as_cli_argument_error | N |

7 tests pass on old code (N): `test_real_writes_still_write` is a guard pinning unchanged behaviour (legit); the sourced-params expiry-boundary tests and `test_k_on_both_bounds`, `test_hook_skips_old_parent_uploads`, `test_fixture_is_the_expected_window` assert behaviour that already held (pure characterisation, not a regression for the change). No raw cards filed (run instruction: do not file cards); each N above is a candidate card.
