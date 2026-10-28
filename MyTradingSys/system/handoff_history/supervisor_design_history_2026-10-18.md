# SUPERVISOR.md history (measured overhead, SV1-SV6 table, Astra review), moved out 2026-10-21 (context-load)

## Measured overhead (before), real data
Source: all 9 coordinator transcripts on JIS-NUC 2026-10-15..18 (>= 3 spawns each; Opus 6, Sonnet 3), parsed whole by
`coord_overhead.py` (a turn = one assistant API message; eq tokens = input 1, cache-write 1.25, cache-read 0.1, output 5).
| Category | Turns | Share | Active min | eq tokens |
|---|---|---|---|---|
| status re-derivation (tasks/desk/codex/STATUS/history reads/fetch) | 323 | 19.5% | 48 | 6.6 M (20%) |
| ship + claim/release run by the coordinator itself | 117 | 7.1% | 115 (27.5%) | 2.2 M |
| watch loops (sleep, list_sessions, notifications) | 113 | 6.8% | 40 | 1.9 M |
| bookkeeping (update_plan, ToolSearch, wrap_up) | 106 | 6.4% | 54 (13%) | 2.0 M |
| spawn (start_session / Agent) | 94 | 5.7% | 39 | 2.4 M |
| verify (cherry, CI) + steer + cleanup + read + pacing + brief edits | 166 | 10.0% | 19 | 3.2 M |
| **coordination total** | **919** | **55.6%** | **315 (75%)** | **18.2 M (56%)** |
| own work (edits, tests, scripts) | 430 | 26.0% | 103 | 8.5 M |
| text-only replies to the operator | 305 | 18.4% | (operator time) | 6.1 M |
1,654 turns, 32.8 M eq, 418 active minutes; **9.8 coordination turns per worker spawned**. Trunk, last 72 h: 2,257 commits,
61% overhead (merge 35%, claim 14%, release 13%; `traffic_report.py 72`). Desk: 17 pending, 9 STALE (`desk.py sweep`).
Gate: clean ship 544 s, 2 slots per machine; on 10-18 six shipping sessions queued 2-3 h and ships died at the 600 s tool timeout.
`relay_runs.jsonl` (51 rows, last 2026-10-17) holds no coordinator data: the relay is retired.

## The five changes that cut most of it
| # | Change | Targets | Expected |
|---|---|---|---|
| SV2 | `supervisor.py tick --json` (fetches first, reads trunk refs, not local state): ONE call per wake = dispatch top 8, desk sweep counts, CI state, gate slots busy, each worker's sha on trunk (cherry) and green ref, lane depths (codex/gemini), budget file age | status + verify + read + pacing: 482 turns, 9.7 M eq | 1-2 calls per wake (-80%) |
| SV3 | The supervisor never ships product code (one docs-only ship at hand-over, no gate slot). Its own edits go to a worker, whose turns re-read a ~80k Sonnet context instead of a 200k+ supervisor context; workers ship with `sync.py ship --release <slug>` in the wave order, with cancellable tickets (Failure handling) | ship 115 min (27.5% of active time); gate timeouts | coordinator ship time -> ~0 |
| SV1+SV4 | Role workers: `You are Builder.` + card id; `roles/builder.md` holds the boilerplate brief (no-questions rule, boot, verify line, report format); `supervisor.py brief <card> --role R` prints the start text; `role_loader.py verify` checks the banner in the worker's note | spawn + brief 2.5 M eq; wrong-workflow workers | one parallel start_session message per wave |
| SV5 | `supervisor.py wait` as THE background shell: exits on the first of a listed sha on trunk, CI red, a gate slot free, 50 min | 113 watch turns | 1 shell per wave, 0 sleep turns |
| SV6 | Bookkeeping diet in the role file: all deferred tools in ONE ToolSearch at boot, update_plan once per wave, wrap_up once per operator turn | 106 turns, 13% of active minutes | -70% |
Target after SV1-SV6: coordination under 3 turns per spawn (now 9.8) and under 25% of a super session's eq tokens (now 56%).
Re-measure with the same script (SV6) on the next two super sessions, worker and coordinator cost together, per session, not one pooled
number. The savings are GUESS until then: batching removes repeated context reads, not the work itself.

## Review (GPT-6 Astra via `codex exec -s read-only`, 55.8k tokens, 12 findings) and what was folded in
Accepted: (1) the banner is a version receipt, not proof: renamed, `--sid` binds it to the hook's record, work is proven only by Verification;
(3) cancellable ship tickets, CI repair exempt, 3-builder cap when a review must fit; (4) stuck worker: check slot, detached ship and trunk
before requeue, keep its branch; (5) watcher exits on transitions only, Gemini moves to a Lab_Guy worker so one shell stays one shell;
(6) exact ancestry instead of `git cherry`, a 60 min CI deadline instead of "2 waves"; (7) totals fixed (919 = 55.6%; brief edits were
missing from the table); (8) the "~13% fewer commits" claim dropped (`ship --release` still writes a release commit, sync.py:545); savings
marked GUESS, SV6 measures worker + coordinator per session; (9) host-wide gate budget added as SV7; (10) chained cards revalidated per
card; (11) messages only to own session ids, never Fable, guard hook SV8; (12) hand-over written by a worker or one docs-only ship.
Rejected: (2) "SV1 not implemented": the review read the tree before SV1 landed in this session (9 tests now, all failed on the old code).
(11, part) capability enforcement for builders (testnet only, no deploy/HALT): already CLAUDE.md hard rules plus existing hooks; out of scope.
(12, part) schema-aware registry merges: the gate's registry checks already reject duplicates; no lost row seen in the data read.
(8, part) "delegating the ship only moves the cost": a supervisor turn re-reads a 200k+ context, a worker turn ~80k, so moving it cuts cost.

