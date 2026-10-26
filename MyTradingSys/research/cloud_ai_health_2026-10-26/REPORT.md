# Claude / cloud AI health investigation

2026-10-26. Audited repository revision ce8194ba2; investigation only. Station C rolling-session support. No process restart, deploy, scheduler installation, paid probe, private history or runtime account inspection. All policy numbers below are OURS (proposals), except explicitly attributed historical observations. Repository links are relative to this report's directory.

## Diagnosis and confidence

The evidence supports a combination of budget pressure, context/rotation friction and orchestration defects. It does not establish a current Claude provider outage. Treat service availability, account capacity, session activity and successful delivery as separate dimensions.

| Evidence | Verified conclusion | Limit |
|---|---|---|
| `system/handover/SUPERVISOR_C.md`, budget at 2026-10-26 01:44Z | Historical C reading: week 74%, cap 80%, hard stop 79%; 5h 17%, reset 01:50Z; no C Builders, peers none at hand-over | Not current usage or proof C is sleeping now; a five-hour reset does not clear weekly pressure |
| `system/WATCHER_TASKS_2026-10-25.md`, State and every-wake steps | Watcher expects rolling hand-over, exact-SHA CI and cherry checks; no scheduler; no new tooling pending decision | A plan is not evidence that any watcher currently runs |
| `research/mts_doctor/REPORT_pilots_2026-10-25.md`, score/learning 1-6 | Reported context compaction 232K to 93K and 250K to 97K; clear refused three times with active work; operator rotation required; card starvation and parallel gate CPU contention | Pilot observations, not fresh host telemetry or a measured context failure threshold |
| Same pilot | Reported six-worker pilot fell to 1-3 after ready cards ran out; serial shipping improved gate times | Low concurrency alone is not service failure |
| `research/coordination_audit_20261026/CLAUDE_REVIEW.md` and `system/tasks/coord-audit-review.json` | Earlier unacknowledged-review premise is superseded: card done, review c074aca4d; seven findings accepted, twelve demonstrations confirmed | Review explicitly leaves some counts/remote CI claims unverified; accepted does not mean repaired |
| Official Claude status summary fetched in this investigation | All listed components operational, incidents array empty; response updated_at 2026-10-26T09:19:43.201Z | Aggregate point observation; cannot establish availability during the pilots or an individual account's access |

The user-supplied earlier Codex usage-limit event is credible session context, not an independently inspected account record. No current remote Claude sessions, provider request logs, quotas, laptop/desktop processes or private account files were accessed. Do not turn these unknowns into green health.

## What the existing tools actually measure

Paths below are repository-relative. Named functions make the evidence reproducible without relying on shifted line numbers.

| Tool / code location | Capability | Gap affecting diagnosis |
|---|---|---|
| `scripts/dev/health_audit.py:audit,ci` | Commit mix, CI, stale claims, workflow overhead | Development-process audit, not provider or session liveness |
| `scripts/dev/host_health.py:check_queue,check_disk` | Host pressure and disk checks | A healthy host says nothing about account allowance; remote state not supplied by a local clone |
| `scripts/dev/aibridge_health.py:main` | Unauthenticated local TCP plus OPTIONS HTTP response check, no command execution | Any HTTP status counts as UP; proves bridge listener only, not DeepSeek session readiness or successful work. Not invoked here |
| `scripts/dev/usage_reminder.py:check,main` | Agent/Task/Workflow spawn gate: reading fresh for 600s, max two registered spawns, five-hour use <= elapsed +10 points; registrations expire after 3600s | No weekly stop in check; post removes oldest timestamp rather than matching an agent ID; exception handler can exit zero for hook errors. Scope is these spawn tools, not every model request. Installation/effectiveness not verified |
| `scripts/sched/budget.py:compute` | Weekly pacing and five-hour throttle, source file recorded by a session | Missing/unreadable/older-than-six-hour data becomes NORMAL; NORMAL must not mean known capacity. Does not enforce C's 79% stop |
| `scripts/dev/codex_run.py:budget,budget_hold,reading_age` | Separate Codex allowance, estimated run cost, five-hour/week 85% stops, stale-reading warning | Reads local session records; this investigation deliberately did not invoke status to ingest those records. Allowance change includes simultaneous account spend; not a per-worker cost measurement |
| `scripts/dev/lane_health.py:load,classify,record_run,sweep_state,allow` | Credit/limit text classification, three incomplete-run trigger, heartbeat and window recovery, hourly held-lane probes | Missing/corrupt state defaults up; no heartbeat means no down transition; DONE or BLOCKED marks up; substring matching merges transient rate errors with exhaustion. Only last 4000 characters considered. Source heartbeat assumes periodic ticks while policy is manual wakes |
| `scripts/dev/supervisor.py:read_budget,_probe_wait_state,brief` | Existing place to expose budget and dispatch/delivery evidence | Independent coordination review confirms missing wait inputs, stale dispatch reads and dropped brief context; fix/reuse that work before adding another health daemon |

These are code observations, not exploit reproductions. Existing focused tests exercise intended behavior; passing them cannot validate installed hooks or remote service health.

## Failure classification and recovery

Official API error documentation distinguishes rate/spend 429, overload 529, server 500, request-size 413, authentication and permission errors. API semantics must not be assumed to describe every Claude desktop UI error. Public status and the specific observed error must both retain their timestamp and surface.

| Class | Required evidence | Recovery |
|---|---|---|
| Provider incident / transient transport | Component incident or structured server/transport error, operation and timestamp; keep request ID locally | Bounded backoff; one eligible retry after cooldown; retain output and avoid duplicate side effects |
| Capacity exhausted | Explicit account/window limit and reset, or fresh usage over approved cap | Stop new model work for that capacity scope, preserve hand-over; fresh reading after reset before recovery. Do not probe hourly into a known weekly hold |
| Context pressure | Session-reported context size/remaining room, repeated compaction or context-specific error | Ship/checkpoint first, summarize goals, sources, unfinished work and exact SHAs; rotate when safe. Do not clear while ship/worker work is active |
| Tool / orchestration failure | Tool exit/error, claim/delivery/CI receipts, host pressure | Repair or route the exact blocked step. Failed ship is not done; provider retry cannot fix stale claims or missing card context |
| Expected sleep / stopped | Declared next wake, owner, active work count and no unmet deadline | No alert before declared wake; at overdue wake mark unobserved and ask coordinator to inspect once |
| Unknown | Missing/stale observation or unreachable station | Display UNKNOWN with age; defer new discretionary spending until refreshed; never infer exhaustion or availability |

## Economical checks and proposed circuit breaker

Use the existing manual Supervisor wake; install nothing. First read a pinned trunk snapshot, claims, existing receipts and the latest explicitly supplied budget observation. Check ready eligible cards before diagnosing idle capacity. Reuse exact-SHA cherry/CI evidence. Fetch public provider status only after a relevant failure or before a recovery attempt, cached for 15 minutes (OURS). No model ping for routine health.

Proposed private observation record: station alias + login alias, provider, surface, session alias, observed_at, source, expires_at, active/idle/sleeping/blocked, next_wake, last_progress_at, phase, card, claimed owner, ship SHA, CI verdict, window usage/reset, weekly usage/reset, context pressure, classified error, retry_at and breaker owner. Unknown values stay null. Keep request IDs, raw errors, account identifiers and detailed usage local; public report contains only scrubbed findings. Do not import histories.

Proposed admission policy (OURS): refresh usage before each paid dispatch and after each completed card; ten-minute maximum age for admission; stale/missing observations hold new discretionary dispatch but allow saving/reporting existing work. Apply the stricter current station cap: C's documented hard stop 79% persists unless operator changes it; do not replace it with Codex's 85%. Reserve enough for checkpoint/review using estimated next-card cost plus observed account-wide concurrent spend. If cost estimate is absent, choose one small bounded card only after a fresh reading and under the stop, rather than a fleet expansion. Keep serial shipping and at most two newly spawned workers as the initial conservative setting, then measure verified cards per allowance point.

Breaker states (OURS): CLOSED admits within budget; OPEN records reason/scope/until and suppresses new work; HALF_OPEN admits one read-only bounded attempt only when its cause permits. For transient failures, at most two total retries including SDK retries, respect retry-after, use jitter and a five-minute maximum retry period; then OPEN for 15 minutes. A new observation is required to leave a quota hold after reset. Authentication, permission, invalid request and persistent tool failures require correction, not automatic retry. A BLOCKED card proves a turn returned, not successful end-to-end service; separately record response availability and delivery success. Deduplicate retries by card/attempt; preserve partial work in its own worktree. Reroute only unclaimed eligible work after checking receiving capacity and reviewer independence; no automatic cascade to an exhausted second vendor.

## Prioritized implementation plan (proposed cards, not dispatched)

Watcher remains the plan writer. These are reviewable specifications, not new queue entries; WATCHER task 5 says start no new tooling pending decision. All changes are non-live and require pre-change failing fixtures. Reuse existing cards where named.

| Priority / proposed card | Scope / dependency | Acceptance evidence |
|---|---|---|
| P0 existing coordination repair chain | Follow CLAUDE_REVIEW repair order; reuse `ship-signal-send-done-only-on-a-complete`, `bug-session-handoff-ship-speed-audit`, claim/dispatch cards | Two-clone A builds, B reviews, C consumes drill: no duplicate owner, no failed-ship done, correct pinned card/CI receipts; all twelve old defect demonstrations reconciled against repairs |
| P1 health-observation-contract | Extend supervisor read-only output and budget adapter; no daemon; after watcher authorization | Distinct unknown/stale/sleep/quota/tool/provider states; source/age/reset visible; same fixture yields same admission verdict across pacing/spawn adapters |
| P1 budget-admission-consistency | Existing budget.py + usage_reminder.py; depends on observation contract | C 79 stop, concurrent spend reserve, stale data and weekly reset enforced without blocking checkpoint; agent registrations matched by ID, corrupt gate state fails closed for spawn |
| P1 health-error-breaker | Extend lane_health and caller boundary; after contract | Structured errors preferred; 429 rate vs exhausted distinguished; retry count includes SDK; no paid probes into known hold; invalid/missing state UNKNOWN; BLOCKED cannot prove delivery |
| P2 rolling-session-receipt | Extend existing supervisor brief/handover; reuse brief-context repair | Fresh successor sees owner, card, scope, progress, failed tool, budget timestamp/reset and ship/CI SHA; duplicate takeover refused; no clear while active |
| P2 health-drill-and-cost-review | Fixtures plus one operator-authorized bounded pilot after above | Count verified shipped cards, incorrect green/alerts, recovery time, retries and total allowance delta; compare serial baseline; publish no private records |

## Required test scenarios

1. Fresh local success with remote unknown: local green never paints all stations green.
2. Expected sleep, overdue wake, disconnected host and no heartbeat ever: distinct outcomes; no dispatch on unknown capacity.
3. Fresh C week 79%, low five-hour use, five-hour reset but week unchanged: hold remains; stale 74% cannot authorize dispatch.
4. Two simultaneous workers spend shared capacity: admission includes reservation; completion releases only its own reservation; stale post cannot release another worker.
5. Transient 429 with retry-after versus explicit exhausted quota, 529, 401, 413, network timeout and midstream error after HTTP 200: correct class; bounded retries; no duplicate result.
6. Log contains quoted billing/rate-limit words, or actual error falls outside log tail: structured outcome wins; ambiguous text UNKNOWN, never account-wide down from a quotation.
7. DONE with failed push, BLOCKED with missing tool, green CI for another SHA and deferred timeout: no delivery success; preserve pending review and partial work.
8. Large context while a ship is active: checkpoint waits for safe boundary; successor inherits full card context; no forced clear/restart.
9. Missing/corrupt/future-dated reading, malformed reset and reset crossed: explicit validity failures; fresh recovery receipt needed.
10. Reroute to another provider already capped, claimed card, or same-vendor reviewer: refuse; retain owner and independent review requirement.

## Verification and sources

Focused existing tests: `python -m pytest scripts/dev/test_lane_health.py scripts/dev/test_usage_reminder.py scripts/dev/test_usage_log.py -q` (result recorded in VALIDATION.md). No production behavior changed. No current host/process or private usage verdict is claimed.

Repository evidence: paths and functions above; baseline ce8194ba2 includes coordination review c074aca4d. Reports under research and files under system are historical evidence, not current remote telemetry.

Official public sources checked 2026-10-26:
- [Claude status summary](https://status.claude.com/api/v2/summary.json): operational snapshot only; response timestamp quoted above.
- [Claude API errors](https://platform.claude.com/docs/en/api/errors): error categories, retry semantics and request IDs. Avoid stacking application retries over SDK retries.
- [Usage limit best practices](https://support.claude.com/en/articles/9797557-usage-limit-best-practices): conversation length, tools, model and effort affect allowance; caching reduces reused-context cost. Large cached context alone is not proof of malfunction.
