# Wiring + maintenance-protocol audit (2026-10-01, cloud, read-only)

Session: MTS-2026-10-01-0517Z-CLD-ANA-wiring-maint-audit. Base: 7fbf178 (main).
Scope: software wiring (not devices) and the recurring maintenance protocols. Cloud sees committed files only:
no processes, no gitignored state (.new, journal/, Dumps/, scheduled-task definitions). Every claim cites a file;
inferences are marked INFERENCE.

## 0. Answer
The maintenance protocols are not broken; they have no trigger. Every recurring one ran through a token-spending
scheduled task or a supervisor wake. All of those were switched off at the weekly cap
(SUPERVISOR_LOG.md:212, 2026-09-30 03:50 IST). Restarting them is a manual step with no owner and no date. The
T0 scripts that cost nothing are not scheduled; they run only when a Claude session remembers to run them.

## 1. Module wiring (static: imports + launchers)
| Path | State | Evidence |
|---|---|---|
| Java feed -> math_object_builder -> verdict -> Tom alert | wired, but LONG side blocked | math_object_builder.py:402 still treats book_imbalance 0.0 (no data) as ask-heavy vs LONG; operator-approved fix (SUPERVISOR_INBOX 21:50Z/22:30Z) is not in committed code |
| live_runner_cli (layers) -> alerts -> auto_trader | wired; no launcher, no status | no `mts` verb starts it or checks it (mts.ps1 has no "live_runner"); started by hand (NEXT_SESSION_PLAN:16). Only the hourly check watched "3 runners up" |
| auto_trader -> new_plan -> executor -> position_manager -> trade_ledger | wired + launchable | `mts` verbs at mts.ps1:183-240 |
| daily_loss_monitor | wired + launchable | mts.ps1:232 |
| orphan_watchdog_cli | built + tested; no launcher | only test imports; "orphan watchdog not scheduled" (SUPERVISOR_LOG:160). INFERENCE: it ran from the hourly-check skill, so it is off too |
| cryptocred classify_msb (live, jishu_4) | known bug live | cc_structure.py:81 unchanged; fix "staged as .new, belongs to supervisor" (NEXT_SESSION_HANDOFF.md) |
| tick layer | not wired (by decision) | needs tiers.json + tick data (SUPERVISOR_LOG:170) |
| Fabio v3 | not built | NUC 2201-2203 on HOLD for spec v3.1 (SUPERVISOR_INBOX 22:30Z item 4) |
| MyTradingSys/queue/consumer.py (CBP) | ack-only; no link to auto_trader (by decision) | NEXT_SESSION_HANDOFF.md "CBP SIDE" |
| testnet_status.py | built + gated (step 3s); never run | no research/testnet_status/ directory; schtasks line in SUPERVISOR_INBOX 22:50Z not executed |
| Handoff wiring: cloud -> SUP | dead end | 8 notes in SUPERVISOR_INBOX.md, 0 consumed (SUPERVISOR_LOG has one `- inbox` line, from 09-29). The SUP wake cron that reads it was deleted (SUPERVISOR_LOG:212). The desktop COORD session uses NEXT_SESSION_HANDOFF.md and does not read the inbox; the book_imbalance item is missing from its handoff |

Offline gate on this clone (`run_all_tests.py --quick`): all code steps PASS. Two environment-only failures:
step 4 (pytest not installed here; 198/198 pass after installing it) and step 3c. Step 3c is a real repo gap: the
guide names execution/plans/, journal/ and halt_history/. These directories are gitignored and their .gitkeep
files were never committed (MAINTAINER_REPORT_2026-09-30 s1, "decision needed"). So the gate is red on every clean
checkout.

## 2. Maintenance protocols: what exists and why each is silent
| Protocol | Defined in | Trigger | Last fired | Why silent |
|---|---|---|---|---|
| Hourly builder check (gate replies, runner watchdog, audit backfill) | desktop scheduled task mts-hourly-builder-check; SKILL.md not in repo | Claude app schedule | 2026-09-30 02:42 IST (HOURLY_CHECK_LOG) | disabled at weekly cap; no re-enable owner |
| DSA feeder (gate DSA replies, pack backlog) | scheduled task mts-dsa-feeder | Claude app schedule | 2026-09-30 02:38 IST (HOURLY_CHECK_LOG) | same; also B080 pace bug stalls dsa_worker |
| Supervisor wake every 3 h (reads SUPERVISOR_INBOX) | session cron | Claude session | 2026-09-30 ~03:50 IST | cron deleted at the cap |
| Qwen audit rotation (T056, 7 templates, 95 targets) | audit_rotation.py --backfill | hourly check only | last target audited 2026-09-29T18:12Z | runs only inside the hourly check; NUC thermal hold paused it first (SUPERVISOR_LOG:202) |
| Audit digest | audit_digest.py | by hand | AUDIT_DIGEST.md 2026-09-29T19:39Z | not scheduled |
| T057 declutter inventory | audit_rotation.py --t0 -> research/audits/T0_CHECKS.md | by hand | never: T0_CHECKS.md does not exist | step 1 of T057 never run, so steps 2-4 (approve, archive, doc map, merges) never started |
| Backup archive | declutter_backups.py --apply | maintainer run | 2026-09-30 (32 execution/layer backups left for the area owner) | maintainer runs are ad hoc; 2 runs in total |
| Standing maintainer (declutter, latency, signal-flow gate, lessons) | MAINTAINER_REPORT_* | ad hoc Opus session | 2026-09-30 | no schedule; Opus cost at the cap |
| STATUS.md regenerate | make_status.py | by hand ("read first" in CLAUDE.md) | 2026-09-29 11:11 | not scheduled; every cold session reads a 2-day-old status |
| Token budget tiers (70/85/95%) | SURFACE_POLICY s3 | supervisor applies by hand | at the cap, all-off, 2026-09-30 | BUDGET_HOLD code deferred; no resume rule, so the 95% "suspend" never reverses |
| Session registry + trailer | SURFACE_POLICY s4, sessions/ | each session at boot | 1 record (cloud). Desktop 1733Z used "...-COORD" with no record or trailer | session_registry.py deferred; desktop prompts (DSA_SESSION_PROMPT) do not require it |
| Session-end checklist | 06_SESSION_END_CHECKLIST, 02c | each session close | last sign-off 2026-09-04 | superseded in practice by handoffs; never retired |
| Daily testnet status | testnet_status.py | schtasks proposed | never | schtasks command not run on the desktop |

## 3. Root causes (ranked)
1. **One switch for everything.** Maintenance work that costs nothing (T0 scripts) shares its trigger with work that
   costs tokens (the hourly check). The weekly cap turned off both.
2. **Suspend without resume.** SURFACE_POLICY s3 says ">=95%: suspend". Nothing says when or who resumes. The
   only resume note is SUPERVISOR_LOG:213 ("re-enable ... sidebar > Scheduled"). Reset is Fri 2026-10-02 09:00 UTC.
3. **Two handoff lanes that do not meet.** SUP lane (SUPERVISOR_INBOX/LOG, NEXT_SESSION_PLAN, STATUS.md) and COORD lane
   (NEXT_SESSION_HANDOFF.md, DSA_SESSION_PROMPT, session_log.json). Cloud writes to SUP, and SUP is not running.
   Live-safety fixes (book_imbalance, classify_msb) wait in the lane nobody reads.
4. **Protocol definitions outside git.** Scheduled-task prompts (hourly check SKILL.md, dsa-feeder) and memory files
   are not versioned, so their state is not auditable. "confirm a scheduled task ... before relying on it"
   (LESSONS F) covers only the desktop.
5. **Deferred enforcement.** BUDGET_HOLD, session_registry.py, AUTO_PAUSE owner/expiry and the .gitkeep decision are
   all "deferred" or "decision needed", with no date.

## 4. Smallest fixes (proposals; nothing applied)
| # | Fix | Cost | Owner |
|---|---|---|---|
| F1 | Windows Task Scheduler (not Claude) runs the T0 set daily: make_status.py, audit_rotation.py --t0, audit_digest.py, testnet_status.py, alert_rate_check.py, declutter_backups.py (dry run). Output is committed by the operator or the next session | 0 tokens | operator (one schtasks line each) |
| F2 | SURFACE_POLICY s3 gets a resume line: "on reset (read /usage), re-enable mts-hourly-builder-check, then mts-dsa-feeder; log it in SUPERVISOR_LOG" plus a one-shot reminder at reset time | 1 line | operator approves |
| F3 | One inbox. COORD reads SUPERVISOR_INBOX at boot (DSA_SESSION_PROMPT s3), or cloud also writes NEXT_SESSION_HANDOFF. Re-post book_imbalance + classify_msb as the top open items | 2 lines | operator picks the lane |
| F4 | `mts status` reports live_runner_cli and orphan watchdog; add an `mts runner` start verb | small, mts.ps1 | desktop builder |
| F5 | Commit execution/{plans,journal,halt_history}/.gitkeep (unignore those 3 files) -> gate step 3c green on clean clones | 3 files | execution owner |
| F6 | Version the scheduled-task prompts (copy SKILL.md files into scripts/schedules/) | copy | operator |
| F7 | Retire 06_SESSION_END_CHECKLIST/02c, or point them at the session record; T057 step 3 (one handoff doc) | doc | T057 |

Not verified here (needs the desktop): whether the two scheduled tasks are still disabled; whether live_runner_cli,
auto_trader and daily_loss_monitor are up now; whether book_imbalance/classify_msb .new files exist.
