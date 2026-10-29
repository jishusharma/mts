# CBP ingestion layer lab report

**Verdict: 27 focused tests passed; task XML validates; activation BLOCKED — data host missing.**

## Checked

- `MyTradingSys/cbp/__init__.py:30-46`: `default_cbp_home()` selects explicit `CBP_HOME`, existing legacy home, or checkout runtime fallback; `store_path()` follows that same home unless `CBP_STORE` is explicit.
- `scripts/dev/cbp_run.py:36,98-112,177-205`: runner aliases the canonical home helper; fetch subprocess nonzero results raise; extraction failures cause incomplete run and prevent stamp advancement (`:224`).
- `scripts/dev/fetch_captions_timed.py:161-194,204-217`: per-video failures propagate a nonzero channel result; `--canonical-out` sets the shared raw transcript destination.
- `scripts/dev/cbp_schedule.py:24-44,47-55,59-72`: task XML has daily UTC starts at 09:00 and 13:00, IgnoreNew overlap policy, StartWhenAvailable, and three 15-minute retries. The generated XML parsed in a dry-run (`XML_VALID`, 2 starts, retry count 3); no task was registered.
- `MyTradingSys/tests/test_cbp_query.py:162-176`: regression asserts fallback path alignment when `F:/CryptoScrapper` is absent, legacy path when present, and explicit override. The brittle `startswith("F:")` assertion is replaced by exact path comparison (`:169`).

## Verification

- `python -m pytest MyTradingSys/tests/test_cbp_query.py --basetemp=F:/MTS/mts-codex-lab/.tmp/pytest-cbp-ingestion -q` — **27 passed**, one pytest cache warning. Initial attempt before creating the basetemp directory errored during setup; rerun with directory created passed.
- The audit reference anticipated 29 tests, but this checkout contains only `test_cbp_query.py` among CBP-named test files, and that file reports 27. No separate `test_cbp_schedule.py` exists here.
- `python scripts/dev/cbp_schedule.py check --home F:/CryptoScrapper` — refused as expected: `missing analyst config: F:\CryptoScrapper\cbp_v2\analysts.json`. `Test-Path F:/CryptoScrapper` is false. Activation remains off; the data host is missing.
- Pre-fix behavior was not replayed from a historical checkout. Current regression assertions cover the absent-home and drive-letter cases; their pre-fix red status is supported by the recorded audit at `MyTradingSys/research/cbp/CBP_AUDIT_2026-10-28.md`, not independently reproduced in this sandbox.

## Findings

| Severity | Location | Finding | Evidence / disposition |
|---|---|---|---|
| MED | `MyTradingSys/tests/test_cbp_query.py:162-176` | Test count differs from card/audit expectation. | Current focused file gives 27 passed; no separate scheduler test module found. Scheduler definition was independently dry validated as XML. |
| MED | `scripts/dev/cbp_schedule.py:47-55` | Host prerequisites are unavailable here. | `F:/CryptoScrapper/cbp_v2/analysts.json` is absent, so the scheduled task cannot be safely checked for installation or activated. Leave off per decision. |

No source changes were needed in this review; implementation already contains the repairs described in the audit record. No follow-up cards created.
