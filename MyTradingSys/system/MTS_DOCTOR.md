# MTS_DOCTOR: the standing health check (operator 2026-10-17: structured runs, no guessing, cheap)

The MTS doctor is a pinned session role. One command, read-only, ~10 s, one dated report. It covers two things that were separate:
AI health (is the guidance the sessions read correct, short, non-duplicated) and process health (is shipping fast and cheap).
Goal: less dev time and fewer tokens per shipped task. Security is not a goal here; live-money safety rules stay.

## Run
`python scripts/dev/mts_doctor.py [--hours 72]` writes `MyTradingSys/research/mts_doctor/REPORT_<utc date>.md`.
`--no-process` = AI health only (no network). `python scripts/dev/health_audit.py 24` = the process part alone (day-over-day check).
Cadence: once per day by the pinned doctor session, and whenever CI is red or a buster ships. Do not rebuild these numbers by hand.

## Part 1: AI health (deterministic for a repo state)
DEAD-REF (a path or doc name in guidance that is not tracked), DUPLICATE (same 80+ char line in 2+ guidance files), MEMORY (index line
without file, file without index line), CARD (`tasks.py lint` warnings), DUP-CARD (`tasks.py twins`: two open cards for one job; `tasks.py new` warns at filing; cards created within 30 min of
each other are one batch and never paired; silence a false pair with `not_twin_of`), SKILL (no name/description frontmatter), BOOT-COST (CLAUDE.md
bytes and the biggest guidance files). Each finding: file:line, what, suggested fix. The script never edits. The doctor fixes DEAD-REF,
DUPLICATE and MEMORY text itself; every other finding is a card for its owner (ROLES.md "Who does what").

## Part 2: process health (trunk and CI at run time) and what each flag means
| Flag | Cause to look for | Change that worked / to try |
|---|---|---|
| CI RED | the failed step and annotation printed in the report | fix first (CLAUDE.md boot 2). A card-format or freshness check must warn, never fail trunk (B13). |
| BOOKKEEPING > 5% | one hand-kept list failing repeatedly (wiring registry, EXTRA, allowlist, size cap) | auto-discover it or scope the gate to production code (B14, B15, B18). |
| B4 ADOPTION < 50% | docs say it, code does not force it | enforce in `sync.py` (B16), not another doc line. |
| OVERHEAD > 50% | merges (one ship per task, B3), claim/release plumbing (B2, B4), status commits on trunk (B17) | a buster counts only when `health_audit.py 24` moves after a day. |
| STALE CLAIM | owner gone | `sync.py release <slug>` or escalate in NEXT_SESSION. |

## Verify every change with another model
After a change from the table, give a second worker on a different model (Haiku, plus Sonnet with a fresh context; Opus only if the
operator names it, `model_guard` refuses it otherwise) a self-contained brief: the report text, the diff, three numbers to recompute
from raw commit history or the GitHub API, and "list errors in the reasoning and what the change breaks". The operator's wording
2026-10-17: agents, not sessions, for these narrow checks. Apply confirmed findings; say in the commit which were rejected and why.

## Record
One line per change in TRAFFIC_BUSTERS.md (B-number, test name, date) and the before/after of `health_audit.py 24`. Commit the report.

## Known limits
- Bookkeeping is a subject-regex count (an upper bound; "register" also appears in real feature commits).
- B4 "folded" counts commit bodies saying `closed with the ship`; a release done another way shows as neither.
- CI uses the unauthenticated API (60 calls/h); on a rate limit the report says `unavailable`; then use `gh run list`.
- Commit counts measure traffic, not wall time. Wall time per task needs the gate timing log (`gate_select`) and session transcripts
  (`worker_cost_report.py`): not in the report yet (next doctor task).
- DEAD-REF skips runtime-generated paths (`runtime/sched`, `orderflow`); other generated files can still show as false positives.
