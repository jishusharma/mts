# NUC restart and Supervisor loop: issues register (2026-10-28, Supervisor B, JIS-NUC)

Recorded by Supervisor B from one session. Status: VERIFIED = seen in this session's output; SUSPECTED = inferred, not reproduced.
Severity: H = stops unattended work or duplicates it; M = wastes turns or hides state; L = noise.

## Bugs and errors

| # | Sev | Status | What | Evidence | Owner / fix |
|---|---|---|---|---|---|
| B1 | H | VERIFIED | Transit hand-over registers the one-shot successor wake `fireAt now` while the current Supervisor is alive and a headless Supervisor B from the logon wake also exists. Two Supervisor B sessions ran at once and each started a Builder on `cbp-query-symbol-btcusdt-returns-zero` (a34675 and a884fb9). | hand-over output `MTS-SuccWake-B fireAt 2026-10-28T13:04Z`; trunk hand-over `ac1ec897a` (12:51Z) vs mine | Opus: bug card `bug-supervisor-handoff-duplicates` |
| B2 | H | VERIFIED | Role file says transit at `TRANSIT at` time or 5 h >= 80%, but `plan` printed `TRANSIT NOW (wave 3.3 h >= 3 h)` at 5 h 48%. The Supervisor stopped and marked itself completed, so nothing visibly ran until the operator asked why. | `plan` output 13:04Z and 13:40Z; role file Transit section | same card |
| B3 | H | VERIFIED | Worker agents started with `sync.py start` in a lane tree get no WORKTREE line and commit in the Supervisor's own worktree. The Stop guard then blocks the Supervisor on the workers' files (4 then 6 files), and a worker's fix commit landed on the Supervisor's branch. | Stop hook feedback x4; Builder note "sync.py start did not switch to a branch" | same card |
| B4 | H | VERIFIED | `git init -b` in `test_refresh_main_checkout.py` fails on the NUC's git 2.24 (flag added in 2.28): 7 failures blocked every ship from the NUC. | Builder a884 gate failure Step 3xt | FIXED `6507d8c1e` (test only). Open: upgrade git on the NUC. |
| B5 | M | VERIFIED | `test_logon_wake.py::test_bad_login_refused_and_command_shape` calls `logon("Z")` without the temp-dir env, so every gate run appends `logon: login must be A, B or C` to the real `F:/MTS/succ_wake/logon_wake.log` (3 junk lines at 13:14, 13:17, 13:30Z). It hides real restart lines. | log tail | same card (small fix: use `_env`) |
| B6 | M | VERIFIED | After gate runs the files `TRIAL_LEDGER_BUILT.csv`, `LAYERS.md` and the hand-over file show as modified with no content change (CRLF/LF warning). The Stop guard counts them as unshipped work. | `git diff --numstat` empty, Stop guard x3 | Builder: normalise with `.gitattributes` or have the gate write LF |
| B7 | M | VERIFIED | `sync.py ship`: the context-fold commit carries only the card JSON, so a worker's own files need a manual `git add` and a second ship. | wiring-audit note | Builder |
| B8 | M | VERIFIED | `sync.py ship` waits up to 10 min for CI and the Bash tool kills at 2 min; every ship needs a detached run plus a poll. | planner Noticed, my ships | Builder: print `shipped` first, CI wait optional |
| B9 | M | VERIFIED | `run_all_tests.py --help` runs the whole suite (no argparse help). | I started a 2 min run by asking for help | Builder |
| B10 | M | VERIFIED | Two ship attempts conflicted on `handover/SUPERVISOR_B.md` because two Supervisors wrote it. `--ours` merge needed. | ship output 13:09Z | covered by B1 |
| B11 | M | VERIFIED | CI went red on Step 4d (`test_7b`) because a card quoted the CLAUDE.md cap number; three red runs 12:30-12:37Z until the reword landed. | `health_audit.py` | FIXED upstream |
| B12 | L | VERIFIED | `usage_reminder.py record` prints only `record failed: '--five'` on a wrong call; its argument is `--elapsed`, not the reset time. `supervisor.py wait` rejects `--running` that `plan` accepts. | my failed calls | Builder |
| B13 | L | VERIFIED | Usage gate refuses a spawn when the reading is older than 10 min; one extra `get_usage` + `record` pair each time. | hook error 13:25Z | improvement I2 |

## Restart wake: open items

| # | Sev | Status | What |
|---|---|---|---|
| R1 | H | SUSPECTED | The cold-start `launch_app` (explorer `shell:AppsFolder`) is not proven at a real boot. Check `F:/MTS/succ_wake/logon_wake.log` for an `app` line after the next restart. |
| R2 | H | VERIFIED | Logins A and C have no `MTSLogonWake`: run `python scripts/dev/logon_wake.py install --login <A|C>` from each machine's own primary clone. |
| R3 | M | VERIFIED | The Claude App's own startup task state reads 0 (disabled) and its Run value points at a versioned `WindowsApps\Claude_4.29.0.0...` path that breaks on update. Cause: unclean power loss (Kernel-Power 41 at 23:28, 11:05, 16:23, 17:16 IST). Fix in software: `launch_app`. Fix in hardware: UPS or another socket. |
| R4 | L | VERIFIED | Discord and Edge start at logon from the Run key; the Claude App does not. |

## Wiring audit findings (card extracted-rules-wiring-audit-tom-fabio-habib, commit `bcfd46cfc`)

- TOM-056 and TOM-140 are marked wired (`SetupCandidatesBuilder.java:284,463`) but cite a stitched quote that is not in the transcript; same for TOM-159 and TOM-174.
- TOM-103, 172, 194 and 023 (VWAP as target) were dropped as NO-SOURCE although their quotes verify; TOM-049 (VWAP side as bias) is unused. Rank H for wiring.
- 40 Tom ids have a different quote in `conditions/*.md` than in `TOM_VERBATIM_INDEX.md`; the index's 1:1 claim is false.
- 446 rows: wired 203, unwired-worth-wiring 76, not-worth-wiring 167, NO_QUOTE 17.

## Housekeeping and hygiene

- 68 stale claims (e.g. `ai-behavior-fold-or-archive` 143 h old, `argon-fix-defects-and-re-land` 89 h).
- Main checkout is 943 commits behind origin/fast-track (doctor warns above 50).
- Four stalled background tasks owned by other sessions: a7d41f374b06f4e89 (175 min), b1lx1m5ta (122 min), b5hx9ksb7 (90 min), bkhvuhnr9 (16 min).
- Session_Planner commit `0b57bdf20` has no `Result:` line; `apply-dedupe-audit-findings` still raw (no done-when).
- Session_Planner and wiring-audit notes still owe a Haiku recheck and a diff-only review.
- Cards with raw state not dispatchable: `backtest-pre-us-failed-break-dev-run` waits for its PRE_REG freeze.

## Improvements

- I1: One hand-over writer per login; refuse `handover` when another Supervisor of the login planned in the last 10 min unless `--force`.
- I2: Have `get_usage` write the reading itself (or `plan` accept the percent and record it) so spawn gates never see a stale reading.
- I3: `sync.py start` should always print a WORKTREE for agents (create one in a lane tree when the caller is a worker), so workers never share the Supervisor's tree.
- I4: `sync.py ship` should print `shipped` as soon as origin has the commit and run the CI wait as a separate `ship --wait` verb.
- I5: Claim a card when the Supervisor decides the spawn, not when the worker boots, so two Supervisors cannot pick the same card.
- I6: `logon_wake.py status` should show the last `app` line and the Run-value path age; add a `selftest` that runs `logon --dry` and checks the log.
- I7: Install `logon_wake` on A and C via one broadcast `--cmd` line (CLAUDE.md fleet-wide rule).
- I8: Upgrade git on the NUC (2.24 is from 2019; many scripts assume newer flags).
- I9: Add a UPS or move the NUC to another socket; Kernel-Power 41 four times in 18 h is the root cause of the lost toggles.

## Added after the Opus fix (bug-supervisor-handoff-duplicates)

- B14 (H, VERIFIED by Opus note, not fixed): a Supervisor started by `MTS-SuccWake-<L>` that registers the next wake fire-now gets dropped, because Windows ignores starting a task that is already running and that run's `finally` unregisters the new task. The chain stops after one link. Card: `bug-successor-wake-chain-stops-after-one-link`.
- B15 (M, VERIFIED): pytest's default temp folder is access-denied in the agent sandbox, so preship "own unit tests" fails there while the tests pass with `--basetemp`. Fix: preship passes a basetemp under the repo scratch or the temp dir that is writable.
- B16 (L, VERIFIED): `tasks.py done` is refused for a card still `raw`, so a bug card filed by the operator's word cannot be closed by its fixer. Fix: allow `done` on a raw card whose `approved_by` is set.
- Fixed and shipped by Opus: B1, B2, B3, B5, B6, B10 (`637422a47`, `af2d5b82b`, `2c5731b8a`, `fc12c222f`); B4 `6507d8c1e`; B11 upstream.

## Added by Supervisor B, later in the same window

- B17 (M, FIXED `5451ebbbc`, `d5946cee2`): the stop guard counted commits not reachable from origin even when the tree equalled trunk (merge commits, a duplicate revert). Now compares against the merge-base.
- B14 FIXED `12d90245b` (successor chain survives link 1; first real handover after a reboot is the proof).
- B18 (M, VERIFIED): parallel workers quote each other's shas in their final reports (LC1 and chain-bug Builders swapped; the ship-speed session quoted a merge commit). Supervisor verifies by file (`git log -- <file>`). Workers are now told to quote from `git log -1 -- <file>`.
- B19 (M, VERIFIED): two CI REDs at Step 3la (krown `crosscheck_desk.py`, T06 `gap_frequency.py`): research scripts with forward-index hits shipped without allowlist rows. Both reverted. Fix: builder briefs now say to add rows in the same commit; consider running `lookahead_lint.py --new` in preship for any new research script.
- B20 (L, VERIFIED): `mts_signal.py broadcast` prints 'cut to 200 characters' but delivers; my one ask went out three times.
- B21 (M, VERIFIED): Builder marked `re-state-t10-stability-py-lc1-keep-rows-` done while its done_when (fair-control rows for 12 families) was not met; the Planner's 'annotate only' decision for LC3 and the imbalance filter had been applied to T10, whose card said otherwise. Card reopened. Fix: Builder must compare its diff to done_when before `tasks.py done`.
- Shipped by the ship-speed session: `f6c7c446b` (ship returns when origin has the commit, B8), `223bb7c01` (`ship --result`, `bg_watch.py until`, poll cap 600 s). Open: skip unchanged gate steps (`gate_select.py`, blocked by JIS-NB's stale claim `ship-gate-let-a-new-look-ahead-fail-reac`, 97 h).
- LC1 re-state `10dca8a07`: 0 of 12 families KEEP on the fair control (published 8).
- Wiring audit `bcfd46cfc`: 446 rows. PRE_REG `04112bfe2`: pre-US failed-break freeze (gate inputs n=300, sd=60 bps are estimates).
