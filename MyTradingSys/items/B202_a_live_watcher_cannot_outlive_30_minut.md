# B202 - A live watcher cannot outlive 30 minutes: the Monitor tool expires at 30 min and no scheduler is allowed, so t

Filed: 2026-10-26
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B202 | 2026-10-26 | OPEN | HIGH | A live watcher cannot outlive 30 minutes: the Monitor tool expires at 30 min and no scheduler is allowed, so the BTC/ES trigger watcher died 12 times in one session (re-armed each time, gaps up to about a minute, plus a stop/re-arm around each commit). Any trigger firing in a gap is lost. Candidate fix: a sanctioned long-lived local process for observation-only watchers (no orders, no live-path), started by the operator or a coordinator and listed in HOW_MTS_RUNS, or a Monitor persistent mode that survives the 30-minute cap. | watch.py armed 12x on 10-26 (10th 19:25Z, 11th ~20:00Z, 12th ~20:06Z); watch_rows.csv has the minute gaps | |
