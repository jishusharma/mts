# CLOUD ACCOUNTS AND CREDITS
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO; rewritten 2026-10-15 as the one page for Claude logins.
# Single source for login identity, GitHub wiring, credits and expiry. Who does what per machine: HOW_MTS_RUNS.md.

## LOGINS

| Login | GitHub identity | Machines (relay_runs.jsonl, artifacts/registry.json) | Claude GitHub App | Role |
|---|---|---|---|---|
| A: jishu.sharma@gmail.com | jishusharma (repo owner) | Lenovo DESKTOP-F7IU69N (roll call `mts_signal.py who`, 2026-10-25; was JIS-NUC on 2026-10-15) | installed, cloud sessions only | Control Room Inbox and decisions owner (q21); all artifacts belong here |
| B: jishu.awgp | jishu-awgp (write collaborator, checked 2026-10-14) | JIS-NB (inferred 2026-10-15, not checked) | not installed yet | second login; its pages are read-only copies |
| C: jishusharma1985@gmail.com (Claude Max, 2026-10-14) | jishusharma1985 (write invite sent 2026-10-14, accept pending) | JIS-NB and JIS-NUC | not installed yet | third login, same queue and ritual |

Repo owned by: jishusharma/mts (GitHub user jishusharma). One repo. Never duplicate the repo. Never fork for a second login.
All logins take the same queue (NEXT_SESSION.md); whichever has budget runs it. Claims are labelled by the machine's `MTS_ACCOUNT`
(`sharma` or `awgp`, set once per machine), not by the login that is signed in; login C has no value of its own, so its claims carry the machine's value.

Login roll call (operator 2026-10-23): a session's login letter is detected from the app account, not typed. `mts_signal.login()` reads only `oauthAccount.emailAddress` from `~/.claude.json` and matches it to the rows above (the full address, or the part before the @); env `MTS_LOGIN=A|B|C` overrides. Only the letter travels: every signal record carries `login`, `budget` and `supervisor.py plan` use the detected letter (a different `--login` prints `LOGIN MISMATCH`), SessionStart announces `login=<L>`, and `python scripts/dev/mts_signal.py who` lists who is logged in where (and flags `CONFLICT login <L>` when two machines claim one login). Never write an address into a signal, a commit or a log.

## CREDITS AND BUDGET (volatile: verify in the Claude app before relying on a number)

| Pool | Amount | Expires | Applies to |
|---|---|---|---|
| Cloud session credits | 100 USD (fresh grant 2026-10-02); which login holds it: UNSOURCED | 2026-11-05 13:29 GMT+5:30 | Cloud sessions only; not Projects or Routines |
| Weekly pool | one per login, each with its own reset | weekly | local sessions, routines |

Cloud credits apply automatically to cloud sessions (CC); the two pools are separate. Credits are per login: one login's credits do not cover another's sessions.
Reading 2026-10-12 (operator, App usage cards): jishu.sharma about 26 % of its week left (reset Fri 2026-10-16); jishu.awgp had used 4 % (reset 2026-10-18).

## GITHUB WIRING (chosen: collaborator path)
Each login that runs cloud sessions needs its own GitHub identity as a write collaborator on jishusharma/mts and the Claude GitHub App installed
under that login, scoped to this repo only (Connectors -> GitHub; the 'Fix' button installs the app on whatever GitHub identity the browser is logged into,
so do it per login). Two logins, one repo, one history; per-login audit comes from the commit trailer and `relay_runs.jsonl`.

## NOMENCLATURE NOTE (2026-10-02)
CC = Claude Cloud (Claude app, Cloud mode). CL = Claude Local (Claude app, Code mode). Both replace the former CCR / CCM.
COLLISION: 'CC' collides with the rule-id prefix 'CCR-NN' in MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md
(Crypto Credible rules). Grep with word boundaries, or use CLD/CLI (SURFACE_POLICY section 1 names) when a two-letter token must be searched unambiguously.

## Hand steps for the second login (2026-10-09)
Operator does these once; sessions cannot (they need the GitHub owner login):
1. GitHub as `jishusharma`: repo jishusharma/mts -> Settings -> Collaborators -> add `jishu-awgp` with Write; accept the invite as `jishu-awgp`.
2. Each machine that login pushes from (JIS-NB, JIS-NUC, laptop): `gh auth login` as `jishu-awgp`, or the Claude GitHub App installed for that login (Connectors -> GitHub).
3. Per machine, once: `setx MTS_ACCOUNT awgp` (or `sharma`), so claims say who holds a task.
4. NUC only: the work tree is `C:\Users\E-ngineers\IdeaProjects\mts-dsa` (DEPLOY_RUNBOOK.md NUC notes); the live-tree marker `.mts_live` must not exist there.
Ritual and per-device rules: PARALLEL.md "Devices and accounts".

## Login C: jishusharma1985@gmail.com (Claude Max, added 2026-10-14)
Used from JIS-NB and JIS-NUC (Claude Code Win App), same queue and ritual as A and B.
- Local work needs no GitHub step: a session pushes with the machine's own git login (JIS-NB: `jishusharma` via gh), whatever Claude login is signed in.
- Same wiring as B for cloud sessions and per-login audit (operator, once):
  1. Create a GitHub user for jishusharma1985@gmail.com (suggested login `jishusharma1985`). A session may not create accounts.
  2. Any session on JIS-NB then sends the Write invite as `jishusharma`:
     `gh api -X PUT repos/jishusharma/mts/collaborators/<login> -f permission=push`
     Accept the e-mailed invite as that user, then add the login to the table above.
  3. Cloud sessions only: in the Claude app on login C, Connectors -> GitHub, install the Claude GitHub App for that user, scoped to jishusharma/mts.
- Pages: login C has its own pins (artifacts/registry.json key `jishusharma1985`). Its Control Room copy is a read-only mirror
  (published without capabilities); the one Inbox is on jishu.sharma (q21).
- Claude routines (scheduled tasks) are per login, and none may run on any login (SCHEDULING_POLICY.md). To use C's
  budget, the coordinator starts sessions signed in as C; never recreate mts-dispatcher.
- How a session knows it is on C: `Artifact read` of a jishu.sharma or jishu.awgp page url says "not found".

## Which login is on which machine (checked 2026-10-15, decision q21)
Until 2026-10-15 the repo put A on JIS-NB and B on JIS-NUC. A session on JIS-NUC whose Claude login is jishu.sharma@gmail.com
owns the Control Room Ep6gA5 and the other pages then filed under jishu.awgp, and cannot read EoHi2q (then filed under jishu.sharma).
So the NUC app runs login A and the JIS-NB pages belong to another login (B by elimination; a session on JIS-NB confirms with `Artifact list`).
Check before trusting a label: the session's own account email and `Artifact list` decide, not this table.
