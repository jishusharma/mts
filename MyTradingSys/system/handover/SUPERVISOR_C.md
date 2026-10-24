# Supervisor C notes: Pilot 2 (6 workers, 4 h, rotation on). Rewritten every wake.

Window: start ~18:50Z 2026-10-24, stop starting 22:20Z, hard stop 22:50Z. Login C JIS-NB. Doctor session: local_bf48e37d-ceba-4d0e-94fe-330458b891ac (reports 20:00Z, 21:30Z, stop; at once on CI red / blocker / gate>30 min).
Plan doc: MyTradingSys/research/mts_doctor/PILOT_super_session_2026-10-24.md. Rule: one ship at a time (I ship from the worker's worktree after `git cherry` of previous is empty); workers commit only, never ship, never touch run_extra_tests.py / run_all_tests.py (registrations batched by me in one ship).
ROTATE protocol: on ROTATE from Doctor: no new workers, let running finish, rewrite this file, stop watchers, reply `ROTATE-READY`. Rebuild from this file + card board + git cherry + list_sessions {"linked": true}.

## Frozen card list (2026-10-24 18:50Z, from tasks.py dispatch; shipped already: T04, sim-dashboard-v1, habib-holdout, mid-turn-image)
RUN (6): dsa-audit-05-placebo-nulls (scripts/T05/, T05_*.md) | dsa-audit-06-cost-fill-realism (T06) | dsa-audit-07-stale-verdicts (T07) | dsa-audit-09-live-parity (T09) | t02-f1-review-allowlist-chunk-4 (lookahead_allowlist.tsv, T02/f1_rows.py, T02_F1_chunks.tsv, lookahead_lint.py) | tasks-py-check-rewrites-other-cards-mark (scripts/dev/tasks.py + test_tasks*)
SPARE (2): cbp-add-channel-latest-n-to-fetch-captio (fetch_captions_timed.py, test, .gitignore) | context-conditioned-session-flow-states (new dir research/session_flow_context_2026-10-18/; B-SHARED, needs review)
Excluded: hook-reminder (new hook, freeze spirit), analyst-ingest-roman-x (stale per Doctor), rv05-h2 / bt-engine-wire (deps/critical), JIS-NB machine cards, lab/YT/Gemini/AWS cards.
Disjoint check: T05/T06/T07/T09 = new files in separate dirs; t02 = lint/allowlist files; tasks.py alone. Central files: none held.

## State (rewritten 18:55Z)
Workers running (Sonnet Agents, own worktrees, started ~18:53Z; they commit only, I ship):
- aeff7478879c89c20 dsa-audit-05-placebo-nulls
- a98795da9ab134b19 dsa-audit-06-cost-fill-realism
- a1089c4267107ce94 dsa-audit-07-stale-verdicts
- a401dace18fdc5813 dsa-audit-09-live-parity
- a0e64b1f86498d923 t02-f1-review-allowlist-chunk-4
- a8783e71ee944c683 tasks-py-check-rewrites-other-cards-mark (20-turn cap)
Worktrees: in each worker's final report (find via `sync.py where --all`).
Central-file holders: none. Ship queue: empty. Awaiting verification: none.
Decisions (OURS): ships serialised by me from worker worktrees; test registration batched into one ship at end.
Usage 18:48Z: 5h 13% (reset 21:10Z), week 34%.
Next action: wait for worker completions (notifications), then ship one at a time; Doctor report 20:00Z.
Last Doctor contact: none yet. Reverts 0. Peak workers 6. Max gate wait 0.
