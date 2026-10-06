# SCHEDULED WORKER DESIGN - 2026-10-02

DSA session MTS-2026-10-02-1423Z-DSA-COO. Findings only. Plan is Claude''s
deliverable, not here. Numbers tagged UNVERIFIED-WEB unless noted.

## 1. Billing that governs scheduled work

Since 2026-06-15, programmatic Claude use (claude -p, Agent SDK,
scheduled tasks) draws from a monthly Agent SDK credit pool, separate
from the interactive subscription quota. UNVERIFIED-WEB.

| Plan | Monthly Agent SDK credit |
|---|---|
| Pro | $20 |
| Max 5x | $100 |
| Max 20x | $200 |

Credit does not roll over. Overflow bills at API token rates and needs
usage credits enabled. UNVERIFIED-WEB.

On Pro, the whole scheduled-Claude budget is $20/month unless overflow
is enabled. That is the binding number. It caps how many runs per month
any schedule can afford.

## 2. Rate card (2026-10-01, VERIFIED prior session)

| Model | Input | Cache write 5m | Cache read | Output |
|---|---|---|---|---|
| Sonnet 5.5 | $2 | $2.50 | $0.20 | $10 |
| Opus 5.5 | $4 | $5.00 | $0.20 | $20 |
| Haiku 4.5 | $1 | $1.25 | $0.10 | $5 |

Per million tokens. Cache read = 0.1x input price.

## 3. Haiku 4.5 capability

Claude''s own description: "near-frontier intelligence", "the fastest
model with near-frontier intelligence", ~2x Sonnet speed. Best fit:
fast, mechanical, well-scoped. Typical use: triage, classification,
single-file edits, short structured reports, status questions.
UNVERIFIED-WEB (Anthropic model page).

What Haiku does not do well: multi-step reasoning across several
files, live-path safety judgment, design work. Those escalate.

## 4. Three scheduling mechanisms (from Claude Code docs)

| Mechanism | Runs on | Local files | Min interval | Cost basis |
|---|---|---|---|---|
| /loop | in-session | yes | 1 min | same session; context grows without bound |
| Desktop Scheduled Tasks | your machine | yes | 1 min | per-run, Agent SDK credit |
| Cloud Routines | cloud | no | 1 hour | subscription rate limits |

Desktop Scheduled Tasks start a fresh context each run. Per-run cost is
flat over time. /loop is not.

## 5. Event triggers beat polling

Claude Code supports event-driven start (Channels, Agent SDK). A worker
starts on failure, not on a fixed tick. Idle ticks cost nothing.
UNVERIFIED-WEB.

## 6. MTS-specific scheduling candidates

| Candidate | Tier-1 script (no Claude) | Claude on event |
|---|---|---|
| Build health | Build-Check.ps1 | on FAIL |
| Test health | run_all_tests.py --quick | on FAIL |
| Canary | testnet_canary.py (Python) | on RED |
| Snapshot freshness | snapshot-age check | on stale |
| Session records | sessions/*.md scan | on missing/partial |
| Bug row health | BUGS.md row count | on IN-FIX > 14 days |
| Paste size | SESSION_PASTE.txt size | on > 150 KB |
| .new aging | BUILD_REPORT in-flight list | on age > 24h |

All eight are deterministic checks a Python or PowerShell script can
run. None require Claude to detect. Claude''s role is what to do with
the failure.

## 7. Budget caps per invocation

--max-turns N: hard ceiling on agentic iterations. 25 for CI/automation.
--max-budget-usd X: hard dollar cap, SDK-enforced.
Concurrency lock: one run per job.
UNVERIFIED-WEB.

One developer''s headless profile in GitHub Actions: 15k-80k tokens per
run, 0.10-0.60 EUR. At Haiku rates that is roughly $0.015-$0.08 per
run. 100 runs a month fits inside the $20 Pro credit. At Sonnet rates,
100 runs is $0.30-$0.80 each, $30-$80/month. Over the Pro credit.

## 8. Design question for Claude

The operator wants the optimal Haiku-first scheduler stack:

- Which checks stay as Tier-1 scripts (no Claude), which trigger Haiku.
- How many Haiku tiers, at what cadence, on what trigger.
- Where Sonnet and Opus escalation sit, and what fires them.
- Cost model: expected runs/month per tier, expected SDK-credit spend,
  and the point where the $20 Pro credit is exhausted.
- Concurrency: how to guarantee one run per job, given the orphan-process
  and index-sweep failure modes.
- Cache discipline: the prefix that Haiku sees must be byte-stable
  across runs so cache read pricing applies.
- Whether one Haiku worker can handle N checks with the check name as an
  argument, or whether each check gets its own worker.

## 9. Failure modes to design against

- /loop for hours: context unbounded, cost grows per tick. GitHub issue
  reports a loop firing more often than configured and consuming most
  of a day''s allocation. UNVERIFIED-WEB.
- Orphan processes: 78 processes, 5.6 GB RAM, server-side billing
  continues after local cleanup. UNVERIFIED-WEB.
- Concurrent workers on one tree: index-sweep, same failure as
  commit 803e705. Historical MTS event.
- Opus on mechanical work: 2x price for no benchmark gain.
- Silent overflow: exceeds credit, bills at API rates.

## 10. What this note does not contain

- A recommended tier count.
- A run-per-month estimate.
- A cost curve.
- A trigger taxonomy (which event fires which tier).
- A concurrency model.

Those are the plan Claude produces. This note is the input.

# END