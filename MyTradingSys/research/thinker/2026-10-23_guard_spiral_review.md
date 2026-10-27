# The guard spiral: 48 h of AI-health fixes in order, 2026-10-23

Source: `git log origin/fast-track --since="50 hours ago"` on the hook and role scripts (37 of 430 commits),
the merged failure review (`2026-10-23_failure_review_merged.md`), and this Supervisor's own blocks today.

## The pattern
Every hook must guess, from transcript text, who started a session, which role it has and whether the operator
is watching. A wrong guess blocks real work, so a fix adds a rule; the rule makes the next wrong guess. 5,952 lines
of hook/coordination code (turn_meter 476, model_guard 536, role_loader 965, supervisor 1,277, shot 1,141,
mts_signal 929, others) and 11 role files run on every message or tool call.

## Chronology (fix -> what it broke next)
| When (IST) | Commit | Fix | What followed |
|---|---|---|---|
| 10-22 17:13 / 17:31 | ce4a04a0f / 9793661a7 | Hooks to background for speed, then back to synchronous | Flip-flop in 18 min |
| 10-22 17:22 | 8b17eb1f6 | offer_guard: Stop hook bounces replies that ask the operator | Real decisions also bounce (today's reply bounced) |
| 10-22 19:59 | 8b4ea32a2 | role_loader: paths never score ("IdeaProjects" loaded Thinker) | Scoring stays fragile: role at char 644 not seen (cause #4) |
| 10-22 20:48 | 59882977d | model_guard: a started session starts workers as Agents | |
| 10-22 23:36 | 779f909a2 | model_guard: role sessions never start_session | Eagle_Eyes started as a background Agent the operator could not see |
| 10-23 19:35 | 3edcc612d | Reversal: interactive roles must be sessions | Still blocked by nested_reason |
| 10-23 21:33 / 21:38 | 3d54646f6 / e61c851df | Guard reads mid-turn typed messages | Needed to start the operator's Opus session at all |
| 10-22 22:55 | fc3f9ebfd | model_guard: role sessions never show buttons | Today: a real operator question blocked |
| 10-23 03:38 | f47d4cae7 | Deny start_session on event turns | One more case where starts fail |
| 10-22 21:55 | c8ff1542a | turn_meter: Thinker mark never overwrites Supervisor | |
| 10-22 23:07 | 4b4f836be | Supervisor unattended budget 6M | |
| 10-23 14:17 | 34fe4a420 | Supervisors exempt from the stop | Exemption never fired: role line not first (cause #3); 49 false stops |
| 10-23 21:50 | 8fb467dea | One role-line detector | Review: a worker escapes its cap by quoting a role line; not accepted |
| 10-23 ~22:00 | (none) | | The operator's Opus session and this Supervisor both stopped by turn_meter: all work halted |

Underneath: cause #1 (the approval card) is drawn by the desktop app, so no hook can remove it, and cause #5 (the main
checkout, where hooks run, never fast-forwards) means fixes on trunk do not run.

## Clean solution (shipped today: step 1)
1. model_guard and turn_meter warn, never block (this commit). Nothing can halt a session any more.
2. Freeze AI-health work: no new guards, rules or guard fixes. Cost control is a habit (Sonnet by default,
   short sessions, one task each, Opus only when named), not enforcement.
3. Remove the parts that fight the platform: offer_guard (Stop bounce), the unattended multi-session machinery
   (supervisor.py six slots, ramp, wake loop), the turn_meter caps. The app needs a click per session (cause #1),
   so unattended fleets cannot work as designed.
4. Keep what earns its cost: the trading code, tests, CI, `sync.py ship`, CLAUDE.md hard rules (testnet only,
   no secrets, public repo), role files as plain text the operator pastes, trunk_lag/broadcast notices.

## Delete everything?
No. The trading system, tests, CI and ship gate are the product and work. Delete the automation of sessions
(steps 1-3), not the system. Expected: no halts, far less spend on meta-work, the operator starts one Sonnet
session per task as he would without any of this.
