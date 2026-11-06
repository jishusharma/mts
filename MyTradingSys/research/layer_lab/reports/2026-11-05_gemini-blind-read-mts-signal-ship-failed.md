# Blind read: mts_signal.py ship_failed() / tool_output()

Reader: Builder, 2026-11-06. Code read (scripts/dev/mts_signal.py lines 426-440): SHIPPED_OK = `\bshipped (?:\d+ file\(s\)|[0-9a-f]{7,})`
(case-sensitive, single space); tool_output joins non-empty stdout/stderr/output of a dict, returns a str as is, else ''; ship_failed =
non-blank output AND (no SHIPPED_OK match OR "CI RED" in output). Predictions were written from the regex before running; the
functions were then called directly (no signals sent).

| # | sample input | predicted ship_failed | actual | result |
|---|---|---|---|---|
| 1 | `shipped 3 file(s)` | False | False | MATCH |
| 2 | `shipped abc1234` (7 hex) | False | False | MATCH |
| 3 | `shipped abc123` (6 hex, too short) | True | True | MATCH |
| 4 | `shipped 3 file(s)` + newline `CI RED: smoke` | True | True | MATCH |
| 5 | `` (empty) | False | False | MATCH |
| 6 | whitespace only | False | False | MATCH |
| 7 | dict stdout `shipped 2 file(s)`, stderr empty | False | False | MATCH |
| 8 | dict stdout empty, stderr `fatal: push rejected` | True | True | MATCH |
| 9 | `Unshipped 3 file(s)` (no word boundary) | True | True | MATCH |
| 10 | `shipped ABCDEF1` (uppercase hex) | True | True | MATCH |
| 11 | dict `{"output": "shipped 1 file(s)"}` | False | False | MATCH |
| 12 | None response (tool_output gives '') | False | False | MATCH |
| 13 | `shipped  3 file(s)` (two spaces) | True | True | MATCH |
| 14 | `shipped 0 file(s)` | False | False | MATCH |

14 of 14 MATCH, 0 DIFF. Observations (not mismatches): "shipped 0 file(s)" counts as a completed ship; a non-dict, non-str response
(e.g. list) yields '' and is "unknown, not failed", as the docstring says.

VERDICT: MATCH
