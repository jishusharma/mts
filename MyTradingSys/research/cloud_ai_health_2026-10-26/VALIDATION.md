# Validation

Baseline ce8194ba2. Documentation-only investigation; no implementation tests added.

- Existing focused suite: `python -m pytest scripts/dev/test_lane_health.py scripts/dev/test_usage_reminder.py scripts/dev/test_usage_log.py -q --tb=short --basetemp F:/MTS/mts-jis-nuc-cloud-ai-health/.pytest-health-audit-20261026`: **52 passed, 2 subtests passed**, 12.73 seconds.
- Initial run using default Windows temp: **44 passed, 8 setup errors, 2 subtests passed**. All eight errors were pytest temp-root PermissionError (WinError 5); this motivated the isolated writable basetemp rerun. No production failure inferred from fixture setup errors.
- No private Claude histories, account state, .env or secret files read. Source inspection includes paths describing private records, not their contents. Historical budget observations are already committed hand-over evidence.
- Public provider status and docs fetched through web browsing; status response timestamp retained in report. No paid model health calls made.
- Exact ship gate outcome is recorded by sync.py and summarized in the chat completion. Focused test success is not a claim about currently running remote sessions or installed hooks.
