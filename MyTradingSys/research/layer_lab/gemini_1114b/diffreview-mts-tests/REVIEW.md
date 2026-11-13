0 BUG, 2 RISK, 4 STYLE (16 commits reviewed under `MyTradingSys/tests` in the last 24 h on `origin/fast-track`, OURS)

Scope: `git log --since='24 hours ago' --format='%h %s' origin/fast-track -- MyTradingSys/tests` (16 commits).

| sha | file:line | finding | severity | one-line fix |
|---|---|---|---|---|
| `14c728ecc` | `MyTradingSys/tests/test_gemini_queue_delivery_1113.py:1` | Merge of `origin/fast-track` (`d4d417861`, `36debbd42`); no additional test changes beyond parent commits | CLEAN | — |
| `2a576111f` | `MyTradingSys/tests/test_tasks_done_raw.py:1` | Merge of `origin/fast-track` (`d4d417861`); no additional test changes | CLEAN | — |
| `d4d417861` | `MyTradingSys/tests/test_tasks_done_raw.py:31` | All 3 tests fail pre-change (`on_trunk` missing, `cmd_done` refused raw cards), but `mock.patch.object(T, "on_trunk", return_value=on_trunk)` stubs out `tasks.on_trunk` (`scripts/dev/tasks.py:1445`), leaving the git ancestor check untested | RISK | Add one test calling real `T.on_trunk` with a mocked `subprocess.run` |
| `7c78a668a` | `MyTradingSys/tests/test_gate_discovery_b150.py:7` | Reland of `a2df4a0c3`; retains unused `import subprocess` after `tracked_tests()` moved to `run_extra_tests.tracked_tests(ROOT)` | STYLE | Remove unused `import subprocess` |
| `36debbd42` | `MyTradingSys/tests/test_gemini_queue_delivery_1113.py:20` | Reland of `b0e15fa36`; `d = Path(tempfile.mkdtemp())` leaks temp directories without cleanup | STYLE | Use `with tempfile.TemporaryDirectory() as td:` |
| `a3d6c402d` | `MyTradingSys/tests/test_gate_discovery_b150.py:1` | Clean revert of `a2df4a0c3` | CLEAN | — |
| `7bc6e2e2b` | `MyTradingSys/tests/test_gemini_queue_delivery_1113.py:1` | Clean revert of `b0e15fa36` | CLEAN | — |
| `80ee172b6` | `MyTradingSys/tests/test_gemini_queue_delivery_1113.py:1` | Merge of `origin/fast-track` (`b0e15fa36`); no additional test changes | CLEAN | — |
| `f60d339d8` | `MyTradingSys/tests/test_live_onepage_mock.py` | Merge of `origin/fast-track` (`83bee59a6`); deletes retired mock test | CLEAN | — |
| `a2df4a0c3` | `MyTradingSys/tests/test_gate_discovery_b150.py:7` | Fails pre-change (`run_extra_tests.tracked_tests` missing, `all_tests(ROOT)` signature mismatch); leaves unused `import subprocess` | STYLE | Remove unused `import subprocess` |
| `b0e15fa36` | `MyTradingSys/tests/test_gemini_queue_delivery_1113.py:20` | All 5 tests fail pre-change (`deliver`/`review_list` missing, `main` rejects `:review`); `d = Path(tempfile.mkdtemp())` leaks temp dirs | STYLE | Use `with tempfile.TemporaryDirectory() as td:` |
| `83bee59a6` | `MyTradingSys/tests/test_live_onepage_mock.py` | Deletes 89-line mock test for retired pages | CLEAN | — |
| `c0f233455` | `MyTradingSys/tests/docs/test_super_session_doc.py:91` | Both new tests use `@report_only` (`MyTradingSys/tests/docs/doc_drift.py:21`), swallowing `AssertionError` so asserts cannot fail pytest (observed `DOC-DRIFT` on `PLAN_24H_2026-11-14.md` while pytest still passed 20/20) | RISK | Remove `@report_only` if link-row presence in `PLAN_24H_*.md` is a hard requirement |
| `2343ec1c8` | `MyTradingSys/tests/test_gate_discovery_b150.py:50` | Reland of `e9de2fb43`; no new defects | CLEAN | — |
| `528132b81` | `MyTradingSys/tests/test_gate_discovery_b150.py:50` | Clean revert of `e9de2fb43` | CLEAN | — |
| `e9de2fb43` | `MyTradingSys/tests/test_gate_discovery_b150.py:50` | Fails pre-change (`run_extra_tests.OFFGATE` missing); adds `OFFGATE` opt-out set to `skip` | CLEAN | — |
