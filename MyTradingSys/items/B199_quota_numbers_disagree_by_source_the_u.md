# B199 - Quota numbers disagree by source: the usage panel showed weekly 99% ("Starts when a message is sent") while ge

Filed: 2026-10-23
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B199 | 2026-10-23 | OPEN | HIGH | Quota numbers disagree by source: the usage panel showed weekly 99% ("Starts when a message is sent") while get_usage returned 0% after the 08:59Z reset; the session quoted 97% from a stale pre-compaction reading and from a stale primary checkout (1040 commits behind). Candidate fixes: every quota claim names its source and read time; re-run get_usage after compaction and before any claim; treat a UI window that has not started as unknown, not 99%; exhaust.py plan rejects a week % older than 10 min | [FIXER: Claude] [LOGGER: Claude DESKTOP-F7IU69N] Operator asked 2026-10-23 "from where are you reading these numbers?" - | - |
