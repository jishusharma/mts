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
