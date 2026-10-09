# PARALLEL - how any number of sessions on any machine work at once

Replaces: commit-only-from-the-desktop (DEVICES section 5), ownership claims in SUPERVISOR_LOG,
`.new` staging, per-session registration in sessions/, and the inbox-per-surface handoffs
(SURFACE_POLICY section 2). Older records stay as history.

## The one idea
GitHub `origin/fast-track` is the only meeting point. Git already merges parallel work and shows
conflicts; we stop re-implementing that with docs. The only thing git cannot protect is the running
system, so the running system gets its own checkout that no session works in.

## Two kinds of checkout
| Checkout | Where | Who changes it | How |
|---|---|---|---|
| Live tree | JIS-NB `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed`, marked by the gitignored file `.mts_live` | supervisor only | deploy in a restart window: stop, `git merge --ff-only origin/fast-track`, gate, restart |
| Work tree | anything else: an App worktree, `../mts-<slug>`, the NUC or laptop clone, a cloud container | any session | `sync.py start` ... commit ... `sync.py ship` |

`sync.py` refuses to run in the live tree, so a session that opens there is told to make a worktree:
`git worktree add ../mts-<slug> -b <host>/<slug> origin/fast-track`.

## A session's whole protocol
1. `python scripts/dev/sync.py start` - pull everyone else's work.
2. Work. Commit small and often, trailer `MTS-Session: <ID>` (that is the session record; commit history is the registry).
   The body has one line `Result: <what works now, or the number it produced>`. A question for the operator:
   `Operator: <question>`. Other sessions' uncommitted files are not yours - never stash, clean or report them.
3. `python scripts/dev/sync.py ship` - merges origin/fast-track (never rebase), runs the `--quick` gate only if
   something other than docs changed, pushes. A rejected push means someone shipped first; it re-merges and
   retries. A real conflict stops and asks you to resolve it.
4. CI runs the full gate on both OSes after every push. Red CI is the next session's first job.

Cloud sessions with a harness branch (`claude/...`) open a PR instead; CI auto-merges it when green.

## Needing the desktop (desk board)
A session blocked on desktop reach (JIS-NB data, a file only it holds, a look at the live tree) does not stop:
`python scripts/dev/desk.py post "<title>" --need "<exact paths/commands>" --done-when "<observable>"`, carries on with
other work, and later `desk.py wait <id>` or reads the result after `sync.py start`. The desktop agent (a Claude
session or the operator) lists open tasks with `mts desk`, claims one (`desk.py take`) and closes it
(`desk.py done <id> --result ...`, or `--failed` with a reason). It is a board for agents, not an executor: nothing
runs a command from task text, and restarts, HALT, orders, deploys and secrets stay with the supervisor
(a declined task closes `--failed` and its `Operator:` line shows in `sync.py news`). Cloud work still uses CLOUD_INBOX.md.

## What the operator reads
`python scripts/dev/sync.py news [hours]` - every shipped commit as subject + Result line + folders touched.
No diffs, no PR review. A missing Result line shows as "(not stated)" and is the thing to push back on.

## What still needs a person
- Deploying to the live tree, restarts, HALT, orders: supervisor only (CLAUDE.md hard rules unchanged).
- Changes to `execution/` or `layers/alerts/` ship like anything else; they reach the live system only on the
  next deploy, so the supervisor reads what changed under execution/ since the live HEAD before deploying.
- Two sessions knowingly on the same file: say so in the commit message; git does the rest.

## Machine-local settings never go in .git/info/exclude
If a path should be ignored, it is ignored for everyone: add it to `.gitignore` and ship it. A local exclude
hides the problem on one machine and breaks the next one.

## Data is not code
Runtime data (orderflow_live, snapshots, klines) is gitignored and lives on JIS-NB. A clone elsewhere sees only
the last committed snapshot; a chart or backtest there that "stops" at an old date is reading that snapshot,
not a broken recorder. Copy data explicitly (DEVICES section 7) before analysing it off the desktop.

## Two accounts, three devices: the ritual (2026-10-09)
Any Claude account on any device runs the same four steps. Nothing else is needed to avoid collisions.
1. `python scripts/dev/sync.py start` (from a work tree, never the live tree) - pulls origin/fast-track and prints open claims.
2. Read `system/NEXT_SESSION.md` (the queue) and pick ONE task not in the claims list.
3. `python scripts/dev/sync.py claim "<task>" --area <paths>` - ships a one-file claim at once, so a parallel session on the
   other account/device sees it. A second claim of the same task is refused. Claims older than 24 h show STALE: ask, then release.
4. Work, commit (`Result:` line), `sync.py ship`, `sync.py release <slug>`, `sync.py where` must be clean, overwrite NEXT_SESSION.md
   if you are the last session of the day. Short sessions: CLAUDE.md.
The account name on a claim is `MTS_ACCOUNT` (env var) else git `user.name`; set `MTS_ACCOUNT=sharma` or `awgp` once per machine.

### Per-device rules
| Device | Runs | May push fast-track? | Rule |
|---|---|---|---|
| JIS-NB (desktop) | live loop (live tree), Claude sessions, scheduled checks | yes, from work trees only (`../mts-<slug>`) | the live tree is touched only by the supervisor deploy; data lives here (gitignored) |
| JIS-NUC | backtests/heavy research on committed data; F:\MTS\data | yes, once its clone has a work tree + git credentials (below) | until credentials exist, NUC output is copied/committed from JIS-NB: write results under `research/<slug>/` and ship from JIS-NB. Never run the live loop there before the DEVICES section 3 move |
| DESKTOP-F7IU69N (laptop) | travel: Claude app, own clone, RDP into the others | yes, from its clone | work on committed data only; need JIS-NB files -> `desk.py post` and carry on |
Only one machine runs the live loop at a time (DEVICES section 3).

### Accounts
One repo (jishusharma/mts), one history. Both Claude accounts push as themselves:
- jishu.sharma (GitHub `jishusharma`, owner): works everywhere out of the box.
- jishu.awgp (GitHub `jishu-awgp`): needs write access, see CLOUD_ACCOUNTS.md "Hand steps". Until granted it cannot push; it hands work over as a file in the thread and another session ships it.
Credits are per account, state is not: whichever account has budget picks up `NEXT_SESSION.md`. When one account is near its weekly limit, the other takes the queue; do not wait for the reset.
