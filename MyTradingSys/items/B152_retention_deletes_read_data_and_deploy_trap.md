# B152 - retention.py deletes/trims files that other tools read (audit digest, supervisor canary), irreversibly; deploy of af91b21 will trip on orderflow _state.json

Status: CLOSED. Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

retention.py deletes/trims files that other tools read (audit digest, supervisor canary), irreversibly; deploy of af91b21 will trip on orderflow _state.json.

## Evidence

- scripts/dev/retention.py:61 deletes Dumps/workers/NUC-QUEUE/done entries older than 14 days, but scripts/worker/audit_digest.py:12,22-39 reads *.task.json/.verdict.txt/.reply.json there, so AUDIT_DIGEST silently loses older findings. It tail-trims runtime_data/supervisor_log.txt to 2000 lines (gitignored, irreversible) although scripts/dev/testnet_canary.py:217 reads its mtime (a daily rewrite makes the canary read 'fresh' once a day) and LOG_GAP_2026-10-02.md cites line 16365 of it as outage evidence. The Dumps.pre_B138 'strict subset' check compares sizes only (retention.py:33-38). Scope is otherwise narrow: it cannot reach ledgers, journals, auto_trades.jsonl, HALT history, transcripts or orderflow/OI data. Dry run is the default; launch-retention.vbs passes --apply.
- af91b21 untracked the orderflow recorder _state.json: on the live tree git merge --ff-only will abort (file modified by the recorder) or delete it; without it orderflow_live.py:187-190 restarts at the current minute and the minutes since the last write are never fetched. The supervisor must copy the file before deploying (mechanism only, live tree not inspected).

## Fix shape

Exclude audit-read paths from retention or change audit_digest to read an archive; keep a dated copy before trimming logs; make the subset check content-based. Add the _state.json copy-and-restore step to the deploy runbook.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-09 consolidate session: retention.py no longer deletes NUC-QUEUE/done (audit_digest reads it), gzips the removed head of trimmed logs beside them, and compares content (filecmp) not only sizes; MyTradingSys/tests/test_retention_b152.py (3 tests). Open: testnet_canary reads supervisor_log mtime (a daily trim still touches it), _state.json copy step in the deploy runbook.

2026-10-10 close (b7e644a, 12530a0): canary mtime test and runbook test in test_retention_b152.py (5 tests); DEPLOY_RUNBOOK.md step 5; scripts/dev/auto_deploy.py copies _state.json to runtime_data/deploy_backup/<stamp>/ before git merge --ff-only and restores it if the merge removed it.

# END
