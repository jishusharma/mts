# AUDIT_RUNBOOK: is the dev process fast and cheap? (operator 2026-10-17: no guessing, same steps every time)

Goal: less dev time and fewer tokens per shipped task. Security is not a goal here (personal project); live-money safety rules stay.

## 1. Measure (one command, ~6 s, read-only)
`python scripts/dev/health_audit.py 72` (hours; 24 for a day-over-day check). Prints Flags first, then the evidence:
commit mix (traffic_report), gate bookkeeping share, B4 adoption, CI red runs with failed step + first annotation, stale claims,
workflow-file commits. Never rebuild these numbers by hand or from NEXT_SESSION prose.

## 2. Act on each flag (decision table)
| Flag | Cause to look for | Change that worked / to try |
|---|---|---|
| CI RED | the step + annotation in the report | fix first (CLAUDE.md boot 2). A card-format or freshness check must warn, never fail trunk (B13). |
| BOOKKEEPING > 5% | one hand-kept list failing repeatedly (wiring registry, EXTRA, allowlist, size cap) | auto-discover it or scope the gate to production code (B14, B15, B18). |
| B4 ADOPTION < 50% | docs say it, code does not force it | enforce in `sync.py` (B16), not another doc line. |
| OVERHEAD > 50% | merges (one ship per task, B3), claim/release plumbing (B2, B4), status commits on trunk (B17) | measure again after 24 h; a buster counts only when `health_audit.py 24` moves. |
| STALE CLAIM | owner gone | `sync.py release <slug>` or escalate in NEXT_SESSION. |

## 3. Verify (always a different model)
After any change from step 2 a second worker on another model (Haiku session via `start_session`, `model` set) gets: the report text,
the diff, and "recompute these three numbers from raw `git log`/the GitHub API, then list errors in the reasoning and anything the
change breaks". Apply its confirmed findings; say in the commit which were rejected and why. The author never verifies alone.

## 4. Record
One line in TRAFFIC_BUSTERS.md per change (B-number, test name, date) and the before/after of `health_audit.py 24`.

## Known limits of the report
- Bookkeeping is a subject-regex count: an upper bound (words like "register" also appear in real feature commits).
- B4 "folded" counts commits whose body says `closed with the ship`; a release done another way shows as neither.
- CI uses the unauthenticated API (60 calls/h); on a rate limit it prints `unavailable`, then use `gh run list`.
- Commit counts measure traffic, not wall time. Wall time per task needs the gate timing log (`gate_select`) and session transcripts
  (`worker_cost_report.py`); not in this report yet.
