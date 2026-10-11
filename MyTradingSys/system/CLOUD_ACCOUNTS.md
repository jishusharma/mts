# CLOUD ACCOUNTS AND CREDITS
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Single source for cloud account identity, credits, expiry, GitHub wiring.

## ACCOUNTS

| Account | Claude login | GitHub identity | Claude GitHub App |
|---|---|---|---|
| A (primary, cloud) | jishu.sharma@gmail.com | jishusharma | installed, cloud sessions only |
| B (secondary, cloud) | jishu.awgp | jishu-awgp (to be created) | not installed yet |

Repo owned by: jishusharma/mts (GitHub user jishusharma). One repo.
Never duplicate the repo. Never fork for a second account.

## CREDITS (2026-10-02)

| Pool | Amount | Expires | Applies to |
|---|---|---|---|
| Cloud session credits | 100 USD (fresh grant 2026-10-02) | 2026-11-05 13:29 GMT+5:30 | Cloud sessions only |
| Weekly Pro pool (account B) | resets Fri 14:30 IST | weekly | local claude.exe, mts go, CL |

Cloud credits apply automatically to cloud sessions (CC).
Not eligible for Projects or Routines.
Two pools are separate. Weekly Pro does not feed Cloud.

## GITHUB WIRING: TWO OPTIONS

A. Collaborator path (recommended). Create GitHub user jishu-awgp.
   Add jishu-awgp as a collaborator on jishusharma/mts with write access.
   Under the jishu.awgp Claude account, install the Claude GitHub App,
   scoped to that single repo. Two Claude logins, one repo, one history.

B. Shared credential path (not recommended). Log into GitHub as
   jishusharma inside jishu.awgp's Claude account. Install the Claude
   GitHub App there. Works, but both Claude accounts share one GitHub
   identity; per-account audit is lost.

## RULES

- One GitHub repo. No duplication, no fork for accounts.
- Each Claude account gets its own GitHub App install, scoped to this
  repo only.
- The 'Fix' button in Connectors -> GitHub installs the app on whatever
  GitHub identity the browser is logged into. Do this per account, not
  once.
- Credits are per Claude account. Account A credits do not cover
  account B sessions.

# END

## NOMENCLATURE NOTE (2026-10-02)

CC = Claude Cloud (Claude app, Cloud mode). CL = Claude Local (Claude
app, Code mode). Both replace the former CCR / CCM.

COLLISION: 'CC' collides with the rule-id prefix 'CCR-NN' in
MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md
(Crypto Credible rules). Grep for 'CC' is noisy. Grep with word
boundaries, or use CLD/CLI (SURFACE_POLICY section 1 names) when a
two-letter token must be searched unambiguously.

## Hand steps for the second account (2026-10-09)
Operator does these once; sessions cannot (they need the GitHub owner login):
1. GitHub as `jishusharma`: repo jishusharma/mts -> Settings -> Collaborators -> add `jishu-awgp` with Write; accept the invite as `jishu-awgp`.
2. Each machine that account pushes from (JIS-NB, JIS-NUC, laptop): `gh auth login` as `jishu-awgp`, or the Claude GitHub App installed for that account (Connectors -> GitHub).
3. Per machine, once: `setx MTS_ACCOUNT awgp` (or `sharma`), so claims say who holds a task.
4. NUC only: `git clone https://github.com/jishusharma/mts` into F:\MTSepo (or add a worktree there) and run `sync.py start`; the live-tree marker `.mts_live` must not exist there.
Ritual and per-device rules: PARALLEL.md "Two accounts, three devices".
