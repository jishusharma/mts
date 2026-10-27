# Option A end-to-end proof (2026-10-23, MTS_Doctor session)

Harnesses: `e2e/e2e_a1.py` (old vs new tasks.py + supervisor.plan_lines), `e2e/e2e_a2.py` (real role_loader hook, compaction, reminders, model_guard), both run on old and new code.

## Status
- A1: 869e61ca3 + fix 464110c71 (refine_due keeps the low-buffer rule; fixes E03/E14; fail-first: 2 new tests fail on 869e61ca3). 26/26 edge cases. Also repairs trunk test_tasks red from d3f6b8b11 (6 dsa-audit cards on SONNET with empty tests; review stamps voided, need Lab_Guy re-stamp). NOT SHIPPED: gate timeouts on JIS-NB (stray audit_rotation.py PID 21716, 31k s CPU, not ours); failing steps pass when run alone (Control Room 27 OK 38 s, lane health 33 OK 36 s).
- A2: 0a26d098b merged here, NOT SHIPPED (same timeouts). 11/15 edge cases (old code 8/15). Open: R04, R08, R12, R14 = role_loader and model_guard still disagree. Fix (not applied, untested): explicit_role = ROLE_LINE names + match_roles, exactly one else None; model_guard.role_session reads role_loader.explicit_injected(Path(transcript).stem) first. Then rerun e2e_a2.py, expect 15/15.
- A3: not started (waits on A1 on trunk). Add: lane moves must go through tasks.py validation (d3f6b8b11 is the live example).

## A1 real board
```
INDEPENDENT raw=93 stale=89 fresh=3 parked=1 at=2026-10-23T12:48Z
--- tasks.py status ---
raw 93 | refined 32 | ready 38 | active 0 | blocked 8 | done 337 | dropped 31
REFINE_NEEDED refinable=124 stale_raw=89 parked=1 ready=38 builder_ready=24 buffer=3
--- supervisor.py plan (dry, isolated home) ---
PLAN login=A host=JIS-NB mode=SPEND 5h=10% -> target 49% by 2026-10-23T15:00Z week=20%/95 slots=3 running=0 new=1 (week 20% of cap 95 over 16 window(s) = 4.7 wk pts here, k 0.12 (GUESS) -> room 39 pts of 5 h)
GATES JIS-NB 0/2 busy; free 2 of 2 known
PEERS UNKNOWN (signals not read): shared-lane actions below are NOTE only this wake; do not touch NEXT_SESSION.md
BOARD STOP A-20261018-6: Do not rerun `gap-g2-dax-ask-candles` as written (operator OK 2026-10-18) (no card of that kind)
HANDOVER MyTradingSys/system/handover/SUPERVISOR_A.md on trunk: - Next: ci-1687ee8 worker found d4b59ba4 already on trunk (same fix); nothing shipped. Check CI run on d4b59ba4; if red, new ci-* card. Unstarted: cpu-audit-lap
SPAWN 1: context-conditioned-session-flow-states (Builder, session, own)  [operator turn: sessions, 2 chained cards each; event turn: size-S Agents only]
NOTE GPT lab: 4 CODEX card(s) ready; owner unknown this wake
RUN Session_Planner (Agent, sonnet): refine 89 raw cards
RUN (background) python scripts/dev/supervisor.py wait --timeout 50m --login A   then end the turn
TRANSIT at 2026-10-23T14:40Z: python scripts/dev/supervisor.py handover --login A --note "<one line>"; ship it; successor line: You are Supervisor. Login A. Continue from MyTradingSys/system/handover/SUPERVISOR_A.md
OLD code, real board: REFINE_OK refinable=124 parked=1 ready=38 builder_ready=24 buffer=3
NEW code, real board: REFINE_NEEDED refinable=124 stale_raw=89 parked=1 ready=38 builder_ready=24 buffer=3
```

## A1 edge cases (fixed tree)
| case | result | edge case | old code | new code | stale/lines | expected | exp n |
|---|---|---|---|---|---|---|---|
| E01 | PASS | empty board | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E02 | PASS | operator case: 1 raw 2 h old + 5 ready | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E03 | PASS | 1 raw 30 min old, 0 ready (queue empty, card fresh) | REFINE_NEEDED | REFINE_NEEDED | 0 | REFINE_NEEDED | 0 |
| E04 | PASS | boundary: exactly 1 h old | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E05 | PASS | boundary: 1 h + 1 s old | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E06 | PASS | created missing | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E07 | PASS | created garbage | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E08 | PASS | naive timestamp (no Z) treated as UTC | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E09 | PASS | +05:30 offset, 2 h old in UTC | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E10 | PASS | future-dated (clock skew) | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E11 | PASS | parked by asks, 3 d old | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E12 | PASS | refine_tries=2 (MAX), 3 d old | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E13 | PASS | refine_tries=1, 3 d old | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E14 | PASS | refined state, 3 d old, 0 ready | REFINE_NEEDED | REFINE_NEEDED | 0 | REFINE_NEEDED | 0 |
| E15 | PASS | old ready/active/done cards only | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E16 | PASS | mix: 3 stale, 1 fresh, 1 parked, 1 maxed | REFINE_OK | REFINE_NEEDED | 3 | REFINE_NEEDED | 3 |
| E17 | PASS | 1 raw 2 h + 3 ready DSA-lane only | REFINE_NEEDED | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| P01 | PASS | NORMAL, refine_raw=4 | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |
| P02 | PASS | NORMAL, refine_raw=0 | - | (none) | 0 | no line |  |
| P03 | PASS | NORMAL, refine_raw missing (card load failed) | - | (none) | 0 | no line |  |
| P04 | PASS | mode STOP | - | (none) | 0 | no line |  |
| P05 | PASS | mode SUPERVISOR-ONLY | - | (none) | 0 | no line |  |
| P06 | PASS | CI red | - | (none) | 0 | no line |  |
| P07 | PASS | THROTTLE mode | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |
| P08 | PASS | CRUCIAL-ONLY mode | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |
| P09 | PASS | peers unknown | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |

TOTAL 26 cases, 26 pass, 0 fail

## A1 edge cases (as shipped by the agent, 869e61ca3)
| case | result | edge case | old code | new code | stale/lines | expected | exp n |
|---|---|---|---|---|---|---|---|
| E01 | PASS | empty board | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E02 | PASS | operator case: 1 raw 2 h old + 5 ready | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E03 | FAIL | 1 raw 30 min old, 0 ready (queue empty, card fresh) | REFINE_NEEDED | REFINE_OK | 0 | REFINE_NEEDED | 0 |
| E04 | PASS | boundary: exactly 1 h old | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E05 | PASS | boundary: 1 h + 1 s old | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E06 | PASS | created missing | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E07 | PASS | created garbage | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E08 | PASS | naive timestamp (no Z) treated as UTC | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E09 | PASS | +05:30 offset, 2 h old in UTC | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E10 | PASS | future-dated (clock skew) | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E11 | PASS | parked by asks, 3 d old | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E12 | PASS | refine_tries=2 (MAX), 3 d old | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E13 | PASS | refine_tries=1, 3 d old | REFINE_OK | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| E14 | FAIL | refined state, 3 d old, 0 ready | REFINE_NEEDED | REFINE_OK | 0 | REFINE_NEEDED | 0 |
| E15 | PASS | old ready/active/done cards only | REFINE_OK | REFINE_OK | 0 | REFINE_OK | 0 |
| E16 | PASS | mix: 3 stale, 1 fresh, 1 parked, 1 maxed | REFINE_OK | REFINE_NEEDED | 3 | REFINE_NEEDED | 3 |
| E17 | PASS | 1 raw 2 h + 3 ready DSA-lane only | REFINE_NEEDED | REFINE_NEEDED | 1 | REFINE_NEEDED | 1 |
| P01 | PASS | NORMAL, refine_raw=4 | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |
| P02 | PASS | NORMAL, refine_raw=0 | - | (none) | 0 | no line |  |
| P03 | PASS | NORMAL, refine_raw missing (card load failed) | - | (none) | 0 | no line |  |
| P04 | PASS | mode STOP | - | (none) | 0 | no line |  |
| P05 | PASS | mode SUPERVISOR-ONLY | - | (none) | 0 | no line |  |
| P06 | PASS | CI red | - | (none) | 0 | no line |  |
| P07 | PASS | THROTTLE mode | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |
| P08 | PASS | CRUCIAL-ONLY mode | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |
| P09 | PASS | peers unknown | - | RUN Session_Planner (Agent, sonnet): refine 4 raw cards | 1 | line |  |

TOTAL 26 cases, 24 pass, 2 fail

## OLD
| case | result | edge case | loaded on prompt(s) | after compaction | reminders /12 | model_guard role | agree | out-of-role rule | expected |
|---|---|---|---|---|---|---|---|---|---|
| R01 | PASS | explicit `You are Supervisor.` | Supervisor | Supervisor | 2 | Supervisor | yes | - | re-inject |
| R02 | PASS | this session's bug: fallback from the word revalidat | None | - | 0 | - | yes | - | none |
| R03 | FAIL | fallback from chart words | Eagle_Eyes | Eagle_Eyes | 2 | - | NO | - | none |
| R04 | FAIL | fallback first, then `reload role Eagle_Eyes` | Eagle_Eyes/Eagle_Eyes | Eagle_Eyes | 2 | - | NO | - | re-inject |
| R05 | PASS | lowercase `you are supervisor.` | Supervisor | Supervisor | 2 | Supervisor | yes | - | re-inject |
| R06 | FAIL | trigger phrase `I need a pipeliner` | Pipeliner | Pipeliner | 2 | - | NO | - | re-inject |
| R07 | FAIL | alias with space `You are Eagle Eyes` | Eagle_Eyes | Eagle_Eyes | 2 | - | NO | - | re-inject |
| R08 | FAIL | role after a sentence `Hi. You are Supervisor.` | Supervisor | Supervisor | 2 | - | NO | - | re-inject |
| R09 | PASS | negation `You are not the Supervisor` | None | - | 0 | - | yes | - | none |
| R10 | PASS | mention only `ask the pipeliner` | None | - | 0 | - | yes | - | none |
| R11 | PASS | role line after 3000 chars | None | - | 0 | - | yes | - | none |
| R12 | FAIL | two roles named | None | - | 0 | Supervisor | NO | - | none |
| R13 | PASS | no role, plain question | None | - | 0 | - | yes | - | none |
| R14 | FAIL | explicit role in a LATER prompt | None/Thinker | Thinker | 2 | - | NO | - | re-inject |
| R15 | PASS | subagent-style brief `You are Thinker.` first | Thinker | Thinker | 2 | Thinker | yes | - | re-inject |

OLD: 15 cases, 8 pass, 7 fail

## NEW
| case | result | edge case | loaded on prompt(s) | after compaction | reminders /12 | model_guard role | agree | out-of-role rule | expected |
|---|---|---|---|---|---|---|---|---|---|
| R01 | PASS | explicit `You are Supervisor.` | Supervisor | Supervisor | 2 | Supervisor | yes | yes | re-inject |
| R02 | PASS | this session's bug: fallback from the word revalidat | None | - | 0 | - | yes | - | none |
| R03 | PASS | fallback from chart words | Eagle_Eyes | - | 0 | - | yes | - | none |
| R04 | FAIL | fallback first, then `reload role Eagle_Eyes` | Eagle_Eyes/Eagle_Eyes | Eagle_Eyes | 2 | - | NO | yes | re-inject |
| R05 | PASS | lowercase `you are supervisor.` | Supervisor | Supervisor | 2 | Supervisor | yes | yes | re-inject |
| R06 | PASS | trigger phrase `I need a pipeliner` | Pipeliner | Pipeliner | 2 | Pipeliner | yes | yes | re-inject |
| R07 | PASS | alias with space `You are Eagle Eyes` | Eagle_Eyes | Eagle_Eyes | 2 | Eagle_Eyes | yes | yes | re-inject |
| R08 | FAIL | role after a sentence `Hi. You are Supervisor.` | Supervisor | Supervisor | 2 | - | NO | yes | re-inject |
| R09 | PASS | negation `You are not the Supervisor` | None | - | 0 | - | yes | - | none |
| R10 | PASS | mention only `ask the pipeliner` | None | - | 0 | - | yes | - | none |
| R11 | PASS | role line after 3000 chars | None | - | 0 | - | yes | - | none |
| R12 | FAIL | two roles named | None | - | 0 | Supervisor | NO | - | none |
| R13 | PASS | no role, plain question | None | - | 0 | - | yes | - | none |
| R14 | FAIL | explicit role in a LATER prompt | None/Thinker | Thinker | 2 | - | NO | yes | re-inject |
| R15 | PASS | subagent-style brief `You are Thinker.` first | Thinker | Thinker | 2 | Thinker | yes | yes | re-inject |

NEW: 15 cases, 11 pass, 4 fail