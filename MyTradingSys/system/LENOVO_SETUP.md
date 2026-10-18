# LENOVO SETUP (DESKTOP-F7IU69N, third Claude login jishusharma1985)

Goal: a clean repo clone that syncs from `origin/fast-track`, works on committed data only, and ships with `sync.py ship`. State from DEVICES.md section 8: Lenovo 20L90025RT, Windows 11 Pro, Java 21, Maven 3.9.11, Python 3.14.7, Git 2.24.1 (too old, update), the old clone `C:\Users\e-ngineers\IdeaProjects\BinanceDataFeed` is on `master` and stale: do not reuse it.
Hostname check first (never the username): PowerShell `$env:COMPUTERNAME` must print `DESKTOP-F7IU69N`. If it prints JIS-NB or JIS-NUC you are in an RDP window: stop.
Rules: testnet only, never read `.secrets/` `.env` keys, no scheduled tasks, no live loop on this machine (DEVICES section 3), work in work trees only, never commit to master.

## Operator steps (a Haiku guide session walks you through these)
1. Update Git: `winget upgrade --id Git.Git` (or install from git-scm.com), then reopen PowerShell; `git --version` must be 2.40+.
2. GitHub login on this machine: `gh auth login` as the account that has push rights to `jishusharma/mts` (JIS-NB pushes as `jishusharma`). If only login C has been invited, first accept the invite (CLOUD_ACCOUNTS.md "Login C" steps 1-2, done on JIS-NB by a session). A session cannot create the GitHub user or enter passwords: you do those.
3. Clone to a new folder: `git clone https://github.com/jishusharma/mts.git C:\MTS\mts-lenovo` then `git -C C:\MTS\mts-lenovo checkout fast-track`. (If the repo URL differs, copy the `origin` URL from JIS-NB: `git -C C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed remote get-url origin`.)
4. Machine identity: `setx MTS_ACCOUNT sharma1985` (claims then say who holds a task). Close and reopen the terminal.
5. Sign the Claude Code app in with jishusharma1985@gmail.com, open the folder `C:\MTS\mts-lenovo`, paste the first-message prompt below.
6. MTS Home page: it is an artifact on login C (read `MyTradingSys/system/artifacts/registry.json`, key `jishusharma1985`). Check it opens from the Claude app; a desk row (`send-jishu-sharma-pages-to-the-repo`) is with the NUC for the latest content.

## First-message prompt (paste into the Lenovo Claude Code session)
```
You are an MTS builder session on DESKTOP-F7IU69N (Lenovo laptop), login jishusharma1985. Work only in C:\MTS\mts-lenovo. Never read .secrets/, .env or keys; never run or stop live processes; testnet only.
0. `$env:COMPUTERNAME` must be DESKTOP-F7IU69N. `git --version` must be 2.40+.
1. `python scripts/dev/sync.py start lenovo-<slug>`, then `python scripts/dev/sync.py where`. Read MyTradingSys/research/STATUS.md (regenerate: `python scripts/dev/make_status.py`) and the ACTIVE entries of MyTradingSys/system/ANNOUNCEMENTS.md. Read MyTradingSys/system/PLAN_4H_2026-10-18.md and PARALLEL.md "Devices and accounts".
2. Check the toolchain and report one line each: `python --version` (3.14+), `java -version` (21), `mvn -v`, `git --version`. Run `python scripts/dev/run_all_tests.py --quick` once; if it is red for a missing tool, say which.
3. `python scripts/dev/tasks.py next --lane DSA-NB`: take dsa-audit-02-lookahead-time (code-only), `tasks.py brief <card>`, `python scripts/dev/sync.py claim "<card>"`, work, new tests must fail on pre-change code, `tasks.py done <card> --result "<number/file>"`, `python -u scripts/dev/sync.py ship --release <slug>`, then `git cherry origin/fast-track HEAD` must print nothing.
4. Commit body carries `Result: <...>` and ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Data-bound cards (1m klines, videos, DAX): `desk.py post <title> --need ... --done-when ... --target JIS-NB` instead of guessing. Never rebase, reset, force-push or stash; no chained `cd x && git`: use `git -C <dir>`. One card per session, then stop with a one-line summary.
```
