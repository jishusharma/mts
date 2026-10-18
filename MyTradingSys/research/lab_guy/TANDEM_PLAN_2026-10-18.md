# Tandem plan: two super sessions, about 6-7 hours (2026-10-18)

One super session on the NUC (lab) and one on the notebook (live machine), working in tandem, each inside its own login's 5-hour and weekly limits.
Rules come from SUPER_SESSION.md and WORKERS.md; nothing here adds a scheduler (SCHEDULING_POLICY.md): a coordinator works this plan by hand.
Status of this file: PROPOSED until the operator starts the sessions. Board: `MyTradingSys/system/ANNOUNCEMENTS.md`.

## Quota rules (read `mcp__ccd_session_mgmt__get_usage` at boot and at every sync)
- Reading on 2026-10-18 for the NUC login (Pro): 5-hour limit 24 % used (about 2 h 48 m to reset), weekly 54 % used, about 5 d 12 h left. NB login: read at its boot (not known here).
- Three logins (operator 2026-10-18): the Pro login (about 54 % of its week used), the AWGP login (its weekly limit resets tomorrow, 2026-10-19) and the Max login (resets Wednesday, 2026-10-21). So the weekly pool is not the constraint this week; the 5-hour windows and running out of READY WORK are. Spend order: AWGP and Max first where they fit the machine, the Pro login lightly; coordinators read `get_usage` for their own login at boot and every sync.
- Pacing rule: keep working steadily through the crunch (slow beats stalled); never run the queue dry. Each coordinator keeps at least 8 ready cards in its lane (CODEX 7+ already) by asking the Session_Planner pass for more before the queue drops below 4; if a login hits 80 % of its 5-hour window it throttles to coordinator-only and the other login or machine takes the cards. Time the heavy phases so a login that resets soon (AWGP tomorrow, Max Wednesday) carries the later phases.
- Throttle spawns at 60 % of the 5-hour window, coordinator-only at 70-80 %, stop at 80 % (memory five-hour-window-pacing).
- Cheapest first: Haiku for mechanical checks, Sonnet for implementation, no Opus unless the operator names it (model_guard). GPT lab: 10 runs per 5-hour window, week 34 % used on the last reading; Gemini Flash for cheap passes, Argon (weekly-only pool) only for C2/C3.
- If one machine runs low, it posts its remaining cards as desk rows for the other, and idles with a one-line signal; it never idles for a reset while the other has budget (CLAUDE.md).

## Who does what
NUC super (lab side, has GPT, Gemini/Antigravity, F:/MTS/data, Lab_Guy):
- H0-0.5: boot; read board and usage; release stale claims on this machine; post sign-on signal.
- H0.5-2.5 GPT lane, one card at a time (lab.lock): lab-data-pin-hash, lab-machine-checks-extra, lab-weight-enforce. After each run, a Haiku Agent re-derives or spot-checks (not the producer's code); ship each.
- H2.5-4.5: lab-crossvendor-stage, lab-holdout-access-control, lab-formula-spec-text; unblock lab-planted-error-trial when its two predecessors are done.
- H4.5-6.5: planted-error trial (cheap stack vs Argon/GPT high) with the ledger; paired Claude review of the first shared result after the tag exists; Opus review output (operator-run) turned into cards; retro-audit batch 1 (top base results by what stands on them).
- Keep the GPT lane busy at all times (queue 7+); Gemini Flash passes on C0 cards as they appear.
NB super (live side, JIS-NB lane, deploy, Sonnet workers):
- H0-0.5: boot; read board; check HALT state and live health (`live_mirror.py brief`, read only); post sign-on signal.
- H0.5-2: deploy hygiene that does not touch trading: bring the live checkout up to trunk by the manual or coordinator deploy (DEPLOY_RUNBOOK.md) so model_guard fix and ROLES reach it; Defender exclusion stays an operator step.
- H2-4: JIS-NB desk tasks: java-popups (PowerShell launcher, CREATE_NO_WINDOW), outcome-labeler-timeout (measure, fix); fix stale AutoDeploy/scheduler docs; BUGS rows B190-B193.
- H4-6.5: Session_Planner pass on the 34 ready cards: add `weight`, mark lab-touching ones, name reviewer slot; builder-ready cards (11) that touch no lab result; Eagle_Eyes/Doctor runs if the operator opens them.
Both: one writer per set of files, at most 4 workers at once per machine, one `sync.py ship --release` per task, no stash, no live-tree edits except via deploy.

## Sync points (one signal line each, kind note)
Every about 90 minutes and at each phase change: `SYNC <machine> done:<cards> next:<cards> quota:<5h %>/<week %>`. A coordinator that sees the other idle posts work to it as a desk row. At H6.5 both write a hand-over line in NEXT_SESSION.md style and stop; the NUC one also writes the Lab_Guy flow table `research/lab_guy/FLOW_2026-10-18.md`.

## Stop and escalate (either machine)
A HALT change, any order or balance anomaly, a failed deploy gate, a ship gate red twice, weekly cap reached: stop, one signal kind ask, wait for the operator. Never place or cancel orders, never touch HALT files, never read secrets.

## Who needs to know what (the board carries it)
- All sessions: A-20261018-1 (workflow in force, weight tag, treat lab results as UNCHECKED), A-20261018-2 (Q76 numbers).
- NUC super and Lab_Guy: A-20261018-3 (queue order). NB super: A-20261018-4 (routing), java/outcome cards are now JIS-NB desk tasks.
- Operator OK 2026-10-18, now ACTIVE: A-20261018-5 (hold new consumers of unchecked lab bases) and A-20261018-6 (do not rerun gap-g2 as written).

## Start prompts (identical text on both machines; change MACHINE)
```
You are the MACHINE super-session coordinator for the tandem block 2026-10-18 (6-7 hours). Run git fetch origin, read origin/fast-track:MyTradingSys/research/lab_guy/TANDEM_PLAN_2026-10-18.md and origin/fast-track:MyTradingSys/system/ANNOUNCEMENTS.md, then SUPER_SESSION.md and WORKERS.md. Read your login's usage first (get_usage) and follow the quota rules; work your machine's rows of the plan with Haiku/Sonnet workers; post a SYNC signal every about 90 minutes; stop at the stop rules. CLAUDE.md applies.
```
