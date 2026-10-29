# CBP ingestion build report

**Changed files + tests:** canonical CBP paths and scheduler dry-run validation repaired; `29 passed` in the focused CBP suite.

## What changed and was run

- `MyTradingSys/cbp/__init__.py:1-39`: documented the implemented `CBP_HOME` fallback and set `DEFAULT_STORE` to the workspace runtime fallback.
- `scripts/dev/fetch_captions_timed.py:16-20`: raw transcript default now follows `CBP_HOME/raw_transcripts_canonical`, while `--canonical-out` remains an explicit override.
- `scripts/dev/cbp_schedule.py:20-55`: validates the twice-daily task XML and provides `dry-run`, which reports validation without registering a task.
- `MyTradingSys/tests/test_cbp_query.py`: added default-path agreement and scheduler dry-run coverage.
- Command: `python -m pytest MyTradingSys/tests/test_cbp_query.py --basetemp=F:/MTS/mts-codex-lab/.pytest-tmp-cbp -q` -> **29 passed**. Pytest emitted one cache-path warning (`WinError 183`); the selected basetemp worked and all cases passed.
- Command: `python scripts/dev/cbp_schedule.py dry-run --home F:/CryptoScrapper` -> task valid at 09:00 and 13:00 UTC, three retries at 15-minute intervals, no registration.
- Command: `schtasks /Query /TN MTS-CBP-Ingestion /FO LIST` -> Windows reports the task path cannot be found; nothing is registered.
- Command: `python scripts/dev/cbp_schedule.py check --home F:/CryptoScrapper` -> **preflight failed: missing analyst config `F:/CryptoScrapper/cbp_v2/analysts.json`**. This is the recorded data-host gap; activation remains off.

## Findings

| Severity | File:line | Finding | Evidence | Resolution |
|---|---|---|---|---|
| MED | `MyTradingSys/cbp/__init__.py:1-39` | Default store documentation and the shared canonical transcript default did not clearly express machine-local fallback behavior. | Test now verifies `cbp.store_path`, runner home, and scheduler home agree when the legacy path is absent; 29 focused tests pass. | Use the checkout runtime fallback unless `CBP_HOME` or an existing legacy home is configured; caption raw store follows `CBP_HOME`. |
| LOW | `scripts/dev/cbp_schedule.py:20-55` | No command exposed a safe task-definition validation without task registration. | `dry-run` validated both UTC starts and retry/overlap policy. Query confirmed no registered task. | Added a dry-run XML validator; host installation still requires successful preflight. |
| MED | `F:/CryptoScrapper/cbp_v2/analysts.json` | Data host/config is absent, so ingestion cannot be activated or preflighted on this machine. | `check` returned the exact missing-config error above. | Leave activation off until a host with the configured CBP data exists. |

The regression expectations pass on the current implementation. A historical pre-fix checkout was not available for a red-before-green run; the sandbox instruction forbids git operations.

## Follow-up cards

None.
