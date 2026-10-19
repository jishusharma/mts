# PARALLEL - how any number of sessions on any machine work at once

> Scheduled tasks (`MTS-AutoDeploy` etc.) are RETIRED 2026-10-17, see SCHEDULING_POLICY.md: deploys are manual or coordinator-run.

Replaces: commit-only-from-the-desktop (DEVICES section 5), ownership claims in SUPERVISOR_LOG,
`.new` staging, per-session registration in sessions/, and the inbox-per-surface handoffs
(SURFACE_POLICY section 2). Older records stay as history.

## The one idea
GitHub `origin/fast-track` is the only meeting point. Git already merges parallel work and shows
conflicts; we stop re-implementing that with docs. The only thing git cannot protect is the running
system, so the running system gets its own checkout that no session works in.

## Collisions: what is measured, what is enforced (2026-10-12)
Last 7 days: 200 merge commits on fast-track, 29 needed a hand edit; the repeat offenders were NEXT_SESSION.md,
the one-line test list in run_all_tests.py and BUGS.md. Cause: sessions sharing a tree (the main folder holds
other sessions' uncommitted files and unshipped commits) and a handful of hot files everyone edits.
- `sync.py start <slug>` inside a persistent lane tree (`mts-app`, `mts-relay`, `mts-dsa`; see Lane trees below) switches to a fresh branch
  `<host>/<slug>` off origin/fast-track and works there: no new worktree. It refuses when the lane tree is dirty or ahead (`sync.py where`
  shows what is unshipped) and never runs in the live tree. The previous task's branch is deleted once it is fully on origin/fast-track.
- `sync.py start [slug]` elsewhere: in a tree that is dirty or ahead of origin it does NOT work there; it makes
  `../mts-<host>-<slug>` off origin/fast-track and prints `WORKTREE: <path>`; work only there. `--here` opts out.
- `sync.py start <slug>` also prints trunk study folders (`research/`, `research/layer_lab/`) and task cards whose names hold
  every slug word: same task already done = read it and compare, never rebuild or overwrite (2026-10-16: one prompt ran on two
  machines; the second session, in an app worktree that skipped `sync.py start`, found the first one's folder only at ship time).
- `ship`: a collision confined to NEXT_SESSION.md, STATUS.md or BUILD_REPORT.md resolves to origin's text and says so
  (re-apply your edit if it mattered); a collision anywhere else still stops for a human.
- Lists that every session appends to (run_all_tests.py test lists) are one entry per line; a test enforces it.
- `sync.py health` (also in the daily hygiene report): stale claims, overlapping claim areas, shared/dirty trees,
  orphan worktrees, branches never shipped for 24 h.

## Two kinds of checkout
| Checkout | Where | Who changes it | How |
|---|---|---|---|
| Live tree | JIS-NB `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed`, marked by the gitignored file `.mts_live` | manual or coordinator-run deploy only (DEPLOY_RUNBOOK.md; MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md) | gate the green SHA, `git merge --ff-only`, restart what changed |
| Work tree | anything else: an App worktree, `../mts-<slug>`, the NUC or laptop clone, a cloud container | any session | `sync.py start` ... commit ... `sync.py ship` |

`sync.py` refuses to run in the live tree, so a session that opens there is told to make a worktree:
`git worktree add ../mts-<slug> -b <host>/<slug> origin/fast-track`.

## A session's whole protocol
1. `python scripts/dev/sync.py start` (from a work tree, never the live tree) - pull everyone else's work; it prints the open claims.
2. Pick ONE task not in the claims list (`system/NEXT_SESSION.md`, or `tasks.py next`) and
   `python scripts/dev/sync.py claim "<task>" --area <paths>`: it ships a one-file claim at once, so a parallel session on any
   login or device sees it. A claim is refused only when its `--area` paths overlap an open claim's (equal or nested), or the same
   task name is claimed again with no areas to compare; disjoint areas never block. A claim older than 24 h shows STALE: ask, then release.
3. Work. Commit small and often, trailer `MTS-Session: <ID>` (that is the session record; commit history is the registry).
   The body has one line `Result: <what works now, or the number it produced>`. A question for the operator:
   `Operator: <question>`. Other sessions' uncommitted files are not yours - never stash, clean or report them.
4. `python scripts/dev/sync.py ship [--full]` - merges origin/fast-track (never rebase), runs a SMOKE gate, pushes (2026-10-16: the
   full suite runs behind in CI, not in your way). `scripts/dev/gate_select.py` maps the changed paths to gate steps: docs/data only
   = the doc invariants (task-card DoR, INDEX/BUGS, prompt contract, doc size/contract tests), seconds, no gate slot; non-live code =
   the tests of the changed files + the pytest shards + wiring + task cards; live-path files (execution, runtime, scripts/sched, src, .github,
   sync.py, run_all_tests.py, auto_deploy.py) or any path no rule knows = every `--quick` step (fail closed); `--full` forces that.
   Cheap steps and the tests that reference the change run first (precheck, no slot) and the gate stops at the first failure; a
   step that passed on the same clean tree is not rerun (GATE_SPEED.md). Start `ship` with run_in_background and read the output once
   (a foreground tool call dies at 600 s). A rejected push means someone shipped first; it re-merges and retries (re-gating only
   when the incoming commits touch what you ship). A real conflict stops and asks you to resolve it. Ship the last task with `sync.py ship --release <slug>` (the claim file is deleted in the same push; a standalone `sync.py release <slug>` is only for 'nothing to ship');
   `sync.py where` must be clean; overwrite NEXT_SESSION.md if you are the last session of the day (hand-over: RELAY.md; session length: CLAUDE.md SHORT SESSIONS).
5. CI (`.github/workflows/ci.yml`) runs the full gate on both OSes after every push and publishes the passing SHA as `green/fast-track`;
   MTS-AutoDeploy (`scripts/dev/auto_deploy.py`, RETIRED 2026-10-17, see SCHEDULING_POLICY.md) deployed only that branch (fast-track only after 90 min without a green advance, gated by the
   local gate). So a defect reaches testnet never; at worst fast-track is red for one CI cycle. Red CI: `make_status.py` files ONE pinned
   card `ci-<first failing sha7>` (`scripts/dev/ci_red_card.py`, one per failure chain), which tops `tasks.py next`; ship it with your next ship.
6. Worktree hygiene (2026-10-12): a session that made a `../mts-<host>-<slug>` worktree and shipped everything
   ends with `sync.py where` (own tree clean); the next session of any lane runs `sync.py tidy` (dry run) then `tidy --apply`,
   which removes only worktrees (`../mts-<host>-<slug>`, the App's `.claude/worktrees/*`, `../mts-relay-*`) that are clean
   (the pulled mirror and a stray AGENTS.md/.codex do not count), fully on origin/fast-track, idle for 24 h (a just-started
   tree looks identical to a finished one), and hold no ignored data files (`git worktree remove` deletes
   Dumps/, runtime_data/ and fetched klines silently; regenerable caches, empty ignored dirs and settings.local.json do not count).
   Never remove a worktree with uncommitted or unshipped work, a named lane (mts-push, mts-codex-lab ...), or
   the main/live tree. Fetched datasets belong in the primary tree's Dumps/ (never tidied), not in a session
   worktree. 2026-10-12: tidy without these guards removed 15 worktrees on JIS-NUC (see RV03 report).

Claim/release (2026-10-16, TRAFFIC_BUSTERS B1) push one plumbing commit on origin's tip: no merge commit, no gate, never ships your other unshipped commits.

Cloud sessions with a harness branch (`claude/...`) open a PR instead; CI auto-merges it when green.

## Needing the desktop (desk board)
A session blocked on desktop reach (JIS-NB data, a file only it holds, a look at the live tree) does not stop:
`python scripts/dev/desk.py post "<title>" --need "<exact paths/commands>" --done-when "<observable>"`, carries on with
other work, and later `desk.py wait <id>` or reads the result after `sync.py start`. The desktop agent (a Claude
session or the operator) lists open tasks with `mts desk`, claims one (`desk.py take`) and closes it
(`desk.py done <id> --result ...`, or `--failed` with a reason). It is a board for agents, not an executor: nothing
runs a command from task text, and restarts, HALT, orders, deploys and secrets stay with the operator and the coordinator (MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md)
(a declined task closes `--failed` and its `Operator:` line shows in `sync.py news`). Cloud work ships by pull request (above).

## What the operator reads
`python scripts/dev/sync.py news [hours]` - every shipped commit as subject + Result line + folders touched.
No diffs, no PR review. A missing Result line shows as "(not stated)" and is the thing to push back on.

## What still needs a person
- Deploying to the live tree: manual or coordinator-run only (DEPLOY_RUNBOOK.md; MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md). Restarts, HALT, orders: not a builder's (CLAUDE.md hard rules).
- Changes to `execution/` or `layers/alerts/` ship like anything else; they reach the live system only on the
  next manual or coordinator-run deploy (MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md), which restarts just the processes whose files changed.
- Two sessions knowingly on the same file: say so in the commit message; git does the rest.

## Machine-local settings never go in .git/info/exclude
If a path should be ignored, it is ignored for everyone: add it to `.gitignore` and ship it. A local exclude
hides the problem on one machine and breaks the next one.

## Data is not code
Runtime data (orderflow_live, snapshots, klines) is gitignored and lives on JIS-NB. A clone elsewhere sees only
the last committed snapshot; a chart or backtest there that "stops" at an old date is reading that snapshot,
not a broken recorder. Copy data explicitly (DEVICES section 7) before analysing it off the desktop.

## Devices and accounts (ritual: "A session's whole protocol" above)
The account name on a claim is the machine's `MTS_ACCOUNT` (env var, `sharma` or `awgp`, set once per machine) else git `user.name`,
not the signed-in login: read the host, not the name. Logins, GitHub identities, credits and hand steps: CLOUD_ACCOUNTS.md.
Credits are per login, state is not: whichever login has budget picks up `NEXT_SESSION.md`; do not wait for a weekly reset.
Which machine, login, lane and model may touch what: HOW_MTS_RUNS.md.

| Device | Runs | May push fast-track? | Rule |
|---|---|---|---|
| JIS-NB (desktop) | live loop (live tree), Claude sessions, scheduled checks | yes, from work trees only (`../mts-<slug>`) | the live tree is touched only by manual or coordinator-run deploy (MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md); data lives here (gitignored) |
| JIS-NUC | relay sessions, Codex lab, backtests/heavy research on committed data; F:\MTS\data | yes, from its work tree (relay and lab sessions ship from there) | never run the live loop there before the DEVICES section 3 move; data made on JIS-NB is not there until copied |
| DESKTOP-F7IU69N (laptop) | travel: Claude app, own clone, RDP into the others | yes, from its clone | work on committed data only; need JIS-NB files -> `desk.py post` and carry on |
Only one machine runs the live loop at a time (DEVICES section 3).

## Nothing left behind (operator 2026-10-15)
A session ends with its tree clean and shipped: the Stop hook (`scripts/dev/stop_guard.py`) blocks one stop while it is not. `sync.py tidy --apply` (repairs case-broken HEADs, retires finished trees) is run by hand or by the coordinator; its MTS-DailyHygiene schedule is RETIRED 2026-10-17 (SCHEDULING_POLICY.md). Leftovers swept by hand are listed in LEFTOVERS_2026-10-15.md with the restore command.

## Fallback if sync.py is broken (moved from CLAUDE.md Quick answers, 2026-10-15)
Never from the live tree (the folder holding `.mts_live`). `git worktree add ../mts-push -b <host>/<slug> HEAD` (reuse it if present),
`git -C ../mts-push merge origin/fast-track` (the Bash settings deny a bare `git merge`; docs conflicts: take origin's text; STATUS.md:
take origin's, regenerate), `python scripts/dev/run_all_tests.py --quick` there, then `git -C ../mts-push push origin <branch>:fast-track`.
`sync.py ship` does the same plus the retry and the NEXT_SESSION/STATUS/BUILD_REPORT collision rule above.

## Lane trees (operator q20, 2026-10-15)
One persistent worktree per lane: JIS-NB `mts-app`, `mts-relay`, `mts-dsa`; NUC `mts-relay`. A task is a branch inside it (`sync.py start <slug>`), not a tree,
so no stale per-session trees pile up (reason: 26 did on JIS-NB). `tidy` never removes a named lane tree, with or without `--all`. The turn cap
for one task is 10 operator turns or the tool-turn cap (WORKERS.md rule 5, `turn_meter.py`). The MTS-Backup 15-minute snapshot is RETIRED 2026-10-17 (SCHEDULING_POLICY.md): nothing backs a tree up but `sync.py ship`.
