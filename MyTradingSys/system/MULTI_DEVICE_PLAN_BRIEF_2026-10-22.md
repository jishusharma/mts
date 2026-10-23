# Multi-device super-session plan: BRIEF for the Opus planner (operator, 2026-10-22)

Written by the MTS Doctor side session from the operator's words. This is a brief, not a plan: the Opus planner validates, corrects and finishes it.

## What the operator said (paraphrase; quotes marked)
- Work has lagged; quotas are going unused ("the quotas for GPT is just going away, unused"); more to do than capacity used.
- AI health is bad: context load not economical; "nothing was wired" and fixes were bad; roles unclear ("which roles exist, which I should use when"); unsure the operator guide (START_HERE.txt) is current.
- The Java engine move to the laptop and remote sessions / the broadcast feature were rough ("nothing went really smooth").
- Simulator work is stuck and is "one of the most important tasks".
- The fundamental rebuild runs from the Fable model were not taken (cards fable-run2-regate-fixes-1to8, fable-run4-setup-angles, fable-run5-grandfather-decision, fable-setups-pack-prep, fable-setups-score).
- Login A is nearly spent: no load on it beyond crucial minimum, otherwise standby; its quota resets "tomorrow, I believe" (UNVERIFIED: check the app usage card, CLOUD_ACCOUNTS.md has 2026-10-12 readings only). Use Gemini and GPT to the full.
- He will start one super session per device (JIS-NB, JIS-NUC, DESKTOP-F7IU69N) from the prompts this plan yields. He has no messenger between devices: pickup must take a few steps.

## Measured facts to build on
- CI: median 12-13 min; Windows leg 11-13 min vs 2m47s Ubuntu; fast-track runs queue serially (57b77eab waited 11 of 25 min). Ranked fixes: `MyTradingSys/system/CI_SPEED_DIAGNOSIS_2026-10-22.md`.
- Role loader guessed the wrong role because `ROLE: <name>` lines are not parsed (only "You are X."). The TURN METER hook blocked Read/Write/Bash in a side session mid-task.
- Open work by lane (tasks.py, ready/refined): SONNET 54, JIS-NB 8, DSA-NB 7, CODEX 5, DSA-NUC 3, OPUS 2, HAIKU 1, DSA 1.
- Devices: JIS-NB desktop (live until cutover), JIS-NUC 24/7 data/Codex lab/DSA, DESKTOP-F7IU69N laptop (next live host, staged: LIVE_HOST_MOVE.md). Logins A jishu.sharma, B jishu.awgp, C jishusharma1985 (Max): machine-to-login mapping in CLOUD_ACCOUNTS.md is partly "inferred"; verify.
- CI was RED at STATUS time (STATUS.md "CI green" line): fix CI first per CLAUDE.md.

## Workstreams to size and assign (draft; Opus to reorder)
1. Live host cutover (laptop coordinator, Login C): needs a CI-green SHA, LIVE_HOST_MOVE.md checklist; operator picks the restart window.
2. CI/ship speed: items 1-3 of the diagnosis (per-SHA concurrency + monotonic mark-green guard with fail-first test; Windows sharding; `sync.py wait-ci`). Any machine, Opus or Sonnet.
3. Context-load and role wiring: role_loader `ROLE:` parse, turn-meter limits for audit roles, one roster, refresh START_HERE.txt so it matches ROSTER.json, lazy-load large files. Audit against `research/context_load/REPORT.md` (2026-10-21).
4. Simulator desk (sim-desk): unstick; state in the 2026-10-21 simulator hand-overs; STATUS.md says SIM parked.
5. Fable fundamental runs: the five cards above, OPUS lane, on the login with budget.
6. GPT and Gemini drain: CODEX lane (codex_run.py, spend guard 10 runs / 5 h) and `gemini_queue.py`; cross-vendor reviews; on JIS-NUC. Goal: no idle quota.
7. Remote sessions and broadcast usability: what broke, a card per defect.
8. Login A: standby; name the 1-2 crucial things only it can do (Control Room Inbox owner, published pages).

## Deliverable asked of the Opus planner
1. Validate and correct this brief against the repo (STATUS.md, tasks.py, ROUTING.md, CLOUD_ACCOUNTS.md, SUPER_SESSION.md, ROSTER.json). Say what is UNVERIFIED (quotas especially).
2. A plan per device and login: who runs what, in what order, which model, expected hours, stop conditions. No scheduler (SCHEDULING_POLICY.md). Zero operator input once started; defaults logged `DECISION (OURS)`.
3. Revalidate the plan once (read it again against the files, fix errors).
4. Three prompt files, short and self-contained: `MyTradingSys/system/SUPER_START_JIS-NB.md`, `SUPER_START_JIS-NUC.md`, `SUPER_START_DESKTOP-F7IU69N.md`. Each starts "You are Supervisor." style line plus the device's task list.
5. Ship with `sync.py ship`. Then the operator's whole pickup per device is ONE pasted line:
   `git pull, then follow MyTradingSys/system/SUPER_START_<HOSTNAME>.md` (put the exact line in `MyTradingSys/system/START_HERE.txt` too). Also hand the three files to the operator with SendUserFile so they reach his phone.
6. Final reply to the operator: at most 8 lines, the three one-line pickups, what needs his decision.
