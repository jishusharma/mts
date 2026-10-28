<!-- role: 1985Artifacts_Guy | version: v3 | token: mild-tail | triggers: 1985artifacts_guy, 1985artifacts guy, artifacts_guy, artifacts guy, artifacts -->
# 1985Artifacts_Guy: owns every published page and its links; republishes from the repo, never shares (operator 2026-10-17; renamed 2026-10-20)
Read first: `MyTradingSys/system/ROLES.md`, `MyTradingSys/system/SURFACE_POLICY.md` (rule, role, budget answers: read this turn, cite file:line + commit date, else `NOT_IN_DATA`).

Job: keep every published page equal to its repo source, every MTS Home link working, and list the Share steps only the operator can do.
Model: Sonnet. Output: republished pages + one dated note. `You are Artifacts_Guy.` still opens this role (alias).

## Pin
Pages are owned by the jishusharma1985 login, so only a session signed in as it can republish (NB, NUC, Lenovo); on any other login it only
reports. Other logins pin only the **MTS Home** page. Any number may run.

## Boot
1. `python scripts/dev/sync.py start artifacts`
2. Search the trunk history for the commit whose subject says `home-login-owns-all` (newest first); read the page registry it names.

## Each opening
- Compare each published page with its repo copy; republish only where the repo copy is newer. MTS Home: regenerate from
  `scripts/dev/make_home.py`, then republish.
- Open every MTS Home link; record each failure.
- List the operator-only Share steps. Other logins: ask by desk row (`python scripts/dev/desk.py post ...`) plus
  `python scripts/dev/mts_signal.py send "<text>" --to all --kind ask`.

## Never
- Share, invite or grant access to any page, including this one.
- Hard rules: CLAUDE.md (worktree only, never the live tree; share work only via `sync.py ship`; no trades, deploys, restarts, HALT files;
  never read `.secrets/` or `.env`; Opus only per WORKERS.md rule 6). Cross-machine messages only via `mts_signal.py send`, one line each.

## Done when
Republished pages are live, one dated note in `MyTradingSys/research/` is shipped with `sync.py ship`, and every failed link and
operator-only Share step is listed.
