# Retention policy (2026-10-08)

Rule: nothing is kept "just in case". A file stays only if a script, test, live process or a human
workflow reads it, or git cannot recreate it. `python scripts/dev/retention.py` is the single place that
encodes the discard rules (dry run; `--apply` deletes). Run it weekly; it prints what it would remove.

| What | Who writes | Who reads | Rule |
|---|---|---|---|
| `Dumps.pre_B138/` | B138 copy | nobody | delete once it is a strict subset of `Dumps/` (script checks) |
| `backup_session/` | pre-git hand backups (09-16..09-26) | nobody | delete entries older than 14 days |
| `Dumps/_archive/<date>/` | `declutter_backups.py` | nobody | delete after 14 days |
| `Dumps/workers/NUC-QUEUE/done/` | NUC lane (decommissioned 2026-10-01) | `scripts/worker/audit_digest.py` (task/verdict/reply files) | never deleted: `retention.py` skips it on purpose (B152, `test_retention_b152.py`); it becomes a candidate only if audit_digest stops reading it |
| `system/session_end_logs.md` | `StateCodeEmitter.appendTransitionLog` (one line per state transition) | nobody (grep: only the writer) | keep last 2000 lines; writer removed from source 2026-10-08 (running JVM still writes until its next restart/rebuild) |
| `runtime_data/mts-watch.log`, `supervisor_log.txt` | watch / supervisor | nobody | keep last 2000 lines |
| `*.pre_*` next to live files | promote step | nobody | `declutter_backups.py` moves them; retention deletes after 14 days |
| `*.new` older than 7 days | staging | nobody once promoted | promote or delete; never leave |

Kept on purpose (read by code): `runtime_data/snapshots/` (replay, outcome labeler, backtests),
`apparatus_log.txt` (parity.py), `outcome_labels.json`, `Dumps/backtest/raw*` (research inputs, re-downloadable).

Open: `Dumps/backtest/raw/bookDepth` is 700 MB; confirm which backtests use it before trimming.
Scheduled: task `MTS-Retention` daily 09:10 local runs `retention.py --apply` via `runtime_data/launch-retention.vbs`.
