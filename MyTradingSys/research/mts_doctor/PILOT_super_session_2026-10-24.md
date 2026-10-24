# Pilot: one super session, 4 hours, measured (MTS_Doctor, 2026-10-24)

Operator ask (2026-10-24): test the new way of working before running super sessions at full speed, "without burning our tokens".
Why a pilot and not mock tests: the rules (SUPER_SESSION.md D1-D6, smoke gate, revert on red, context rules) are about how sessions behave
together; a mock cannot show cache misses, ship queueing or file clashes. Industry practice for a process change is a short, bounded real run
with numbers written down before it starts, compared with a measured baseline, one change at a time. This file is that plan.

## Baseline (measured 2026-10-24, before the pilot)
| Measure | Baseline | Source |
|---|---|---|
| Local ship gate, all ships after the smoke fix | 69% under 2 min, p90 9.6 min (13 ships) | worktrees' gate_timing.jsonl |
| Local ship gate before the fix | 61% under 2 min, p90 26.7 min (18 ships) | same |
| CI red | 10 of 30 runs on 10-23; 0 since 10-23 19:51Z | `gh run list` |
| Session start context | 75k tokens (system tools 40k, MCP tools 11k, system prompt 10k, skills 6k, memory 4k) | transcripts; `get_usage` categories |
| Context per turn | median 125k; sessions over 200 turns = 39% of all context | context_cost_2026-10-24.md |
| Mid-session cache misses | 126 in 7 days over 134 sessions (~14% of cost) | same |
| Budget at plan time | login C: 5 h 4%, week 27%, resets 2026-10-27 20:00Z | `get_usage` 2026-10-24 ~09:20Z |

## What runs
- One super session per SUPER_SESSION.md (start prompt at its end), coordinator on Sonnet, effort as set by the app (no change).
- **4 Sonnet workers** at once, each on a `ready` card whose files no other worker holds (D3: more than 2 needs one logged line: get_usage this
  turn, 5 h under 60%, own card, own files, last smoke under 5 min). At most 1 live-path card in the pilot.
- No ultracode, no fast mode, no Opus, no model switch mid-session. One change at a time: this pilot tests the workflow; ultracode and
  connector trimming are later pilots, each compared with this one.
- Length: 4 hours from the first worker start.

## Before starting (all must be true)
1. Main checkout fast-forwarded to trunk (card `main-checkout-stale-hooks-2026-10-24`), so the hooks running are the trimmed ones.
   Check: `git -C <main checkout> rev-list --count HEAD..origin/fast-track` = 0.
2. CI green on the trunk tip.
3. **A frozen list of 6 named card ids** in the coordinator's notes file before the first worker starts: each STATE ready, files disjoint,
   runnable on JIS-NB. Independent review (2026-10-24) found only about 4 clean today: `cbp-one-acked-row-through-queue-consumer`,
   `t02-f1-review-allowlist-chunk-4`, `find-gemini-antigravity-quota-command-an`, plus `mid-turn-image-intake-gap` after a refresh; the dsa-audit
   cards need a disjoint-files check. Not for the pilot: `research-top-level-declutter` (moves 183 files), cards needing NUC/desktop data,
   `context-composite-v2-dev-read` (one-shot outcome read). Flagged stale: `bug-guard-blocks-interactive-roles` (model_guard deleted in 43d3bfc8f),
   `hook-reminder-get-usage-before-after-age` (a new hook), `analyst-ingest-roman-x`, `rv05-h2-position-line-evidence`. Session_Planner makes the
   list (card supply is the biggest risk to the run); Doctor only flags.
4. 5 h window under 30% at start.

## Pass / fail (decided now, read at the end by MTS_Doctor)
| # | Measure | Pass |
|---|---|---|
| 1 | Cards from the frozen list shipped and verified (`git cherry` empty, `Result:` line, card done) | at least 5 of the 6 in 4 h |
| 2 | Non-live ship local gate | median under 2 min; wait for a gate slot median under 2 min (`wait_s`) |
| 3 | CI | at most 1 red; red time on trunk under 15 min in total; reverted, not patched forward |
| 4 | Rework (read 24 h after the end) | 0 pilot cards reverted or re-fixed |
| 5 | Cost | 5 h window never over 80%. Weekly % per verified card is recorded only (first number, no threshold) |
| 6 | Context | worker turns median under 60 (sessions and Agents); coordinator mid-session cache rewrites at most 2 |
| 7 | Operator | 0 operator turns needed after the start prompt |
| 8 | Machine | the operator does not report the notebook slow (row 2's gate wait is the measured proxy) |

Pass on all 8: raise to 6 workers in the next run, then try ultracode on one hard card as its own pilot.
Fail on any: the Doctor names the cause from transcripts and git, one fix, rerun the same pilot. Do not change two things at once.

## Next pilots, one change each, each compared with the one before
- **Pilot 2: 6 workers**, same login, if pilot 1 passes.
- **Pilot 3: all three logins** (operator idea 2026-10-24, simplify-tooling hand-over): one super session hands out cards; the other logins take
  them through the repo (cards + `sync.py claim`, the item 9 machinery, kept). Logins do not conflict, tasks do (same files, trunk, live tree,
  ship queue), so lanes split by kind of work: one live-path writer, a research/backtest lane under `research/`, an audit/tooling lane; one
  writer per area by claim; no new rules. One desktop app runs one login, so each extra login is another machine that must be on (NUC, desktop),
  and caches are per machine. Pass rows as pilot 1, plus: 0 claim clashes, and each login's weekly % per verified card.
- **Pilot 4: ultracode on one hard card**, against a normal Sonnet worker on a similar card.

## Stop early if
CI red not reverted in 10 min; 5 h window over 80%; two workers stuck on the same file; the operator says the machine is slow.

## How the Doctor measures at the end
`git log` / `git cherry` for ships; worktrees' gate_timing.jsonl ship rows; `gh run list` for CI; session transcripts for turns, context and
cache rewrites (same method as context_cost_2026-10-24.md, plus the coordinator's subagent transcripts, because workers started on event turns
are background Agents: SUPER_SESSION.md D3/step 4); `get_usage` before and after. Result goes in `REPORT_<date>.md`; row 4 a day later.
Plan reviewed by an independent Sonnet agent 2026-10-24 (card supply, Agent workers, unmeasurable rows); fixes above.
