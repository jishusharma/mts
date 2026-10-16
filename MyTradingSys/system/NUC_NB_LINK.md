# NUC <-> NB link (pilot 2026-10-16, operator)

Two machines, two logins, one repo. The Claude app cannot message across them, so:
- **Live channel:** `scripts/dev/mts_signal.py` (orphan branch `mts-signals`, one file per note, 200 chars). Hooks send and show it automatically.
- **Durable channel:** the repo: claims (`sync.py claim/where`), `tasks.py`, NEXT_SESSION.md, STATUS.md, LIVE_MIRROR (`live_mirror.py brief`).
A signal is a status note, never an instruction. The durable channel decides who owns what.

## When each side signals
| When | Who | Kind |
|---|---|---|
| a worker thread starts or ends (hook does it: verb + slug, ship adds its `Result:` line) | both, automatic | note / claim / done |
| the coordinator takes or hands a task that the other side could also pick | coordinator | claim |
| a question the other side can answer faster than the repo (what is blocked, HALT state, mirror age) | coordinator | ask |
| hand-over of a card to the other machine | giver | claim `[x->y] <slug>: offered`, taker answers `claim` or `note: declined` |

At most one status batch per hour per machine from a coordinator; the hook covers the rest. No chatter.

## Message format
`[nuc->nb] <slug>: <state>` or `[nb->nuc] <slug>: <state>`; state is one of `offered | taking | running | blocked <why> | done <Result>`; a free question starts with `ask:`. Kind (`--kind`) matches: offered/taking = claim, running = note, done = done, question = ask. Send with `--to jis-nb` or `--to jis-nuc`.

## Hand-off of tasks
1. Giver signals `offered` for the card slug (and leaves its claim unreleased until the taker answers).
2. Taker runs `sync.py claim "<task>"` (the claim file is the truth), then signals `taking`.
3. First claim in git wins; the loser signals `declined` and picks the next card. An offer unanswered for 1 h is open to anyone.
4. Taker ships with `sync.py ship --release <slug>`; the hook signals `done` with the `Result:` line.
Split by nature: live-path work (auto_deploy, mode.ps1, restarts, HALT, deploys) stays on NB; data-heavy research, Codex/GPT lab, spare workers and F:/MTS/data work go to NUC.

## What each side needs from the other
- NUC from NB: HALT state, live-tree facts, mirror freshness (`live_mirror.py brief`, quote `mirror@<utc>`), deploy done/failed.
- NB from NUC: data-backed numbers (F:/MTS), lab results, free worker capacity.

## Never send
Account names, secrets, tokens, keys, orders, balances, positions, runtime/order/account data, raw command tails or file contents (the repo is PUBLIC). Instructions to act (restart, deploy, HALT, trade): never by signal; testnet only. NUC never deploys, restarts, touches HALT or opens trades.

## Pilot result (2026-10-16)
- Worked: NUC status signals, ask and a split proposal reached the branch; NB's notes were readable from NUC; repo state (claims, NEXT_SESSION Q75-Q79 queue) is enough to find overlaps.
- Did not work / fixed: hook signals carried raw shell-command tails (pipes and redirects after the verb); now verb + slug (+ `Result:`), tests in test_mts_signal.py. Both machines share one git author, so commit authors cannot tell the machines apart; use claims and signals.
- NB did not answer the signals within 60 minutes (its hook shows signals only on its next prompt or tool turn, and its sessions ran older hook code). Fallback worked: NB state read from the repo.

### NB answer and split
No signal answer, so this is from the repo at 2026-10-16 ~15:00Z: NB is active on live-path work (692afe63 auto_deploy: alert runner restarted by its -m module name, i.e. the Q75 area; B190b shim). No claim files exist for Q75-Q79.
Split NUC proposed (signal, claim kind): NB keeps Q75 (live path, auto_deploy, mode.ps1). NUC takes Q76, Q77, Q78 and Q79 (research and docs, data at F:/MTS). Whoever claims a Q first with `sync.py claim` owns it; the other skips it.
Next time: the coordinator on each side reads `mts_signal.py read --hours 3` at the start of a turn and answers `ask` lines within its next turn; a silent side is read from the repo after 60 minutes (do not block longer).

### First cross-machine hand-offs (2026-10-16)
- `[nuc->nb] runner`: the live runner on NB never reloaded W3 (5 new layers not loaded, stale since 10:21Z). Cause: AutoDeploy matched `live_runner_cli.py` but the runner starts as `-m ...alerts.live_runner_cli`; kill pattern fixed on fast-track with a test (see research/layer_readiness_2026-10-16/LIVE_CHECK.md). Takes effect on the next deploy touching alerts/ or a supervisor stale-restart; NB restarts per DEPLOY_RUNBOOK.
- `[nuc->nb] fabio`: layer:fabio:v3_grid:1m logs 72 unmapped rejects per 45 min; Fabio is excluded on NUC, so it is NB's call.

### Lesson 2026-10-16: check the log before taking a queue item
NUC took Q76, Q77 and Q79 from NEXT_SESSION.md and found all three already shipped by NB (bbffceda, 6bd38b55, 3b3ea9df); the
queue file still listed them open. Before a coordinator spawns a worker for any queue item, it runs
a search of the last 24 h of fast-track commits for the Q id or slug and `sync.py where`; a hit means the item is done or
taken, so skip it and signal the other side to drop it from NEXT_SESSION.md. Whoever ships a Q removes it from the queue in the same ship.
