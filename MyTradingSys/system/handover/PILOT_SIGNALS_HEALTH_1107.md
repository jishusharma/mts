# Hand-over: pilot-signals-health-1107 (2026-11-07 ~18:20Z)

Status: NOTHING BUILT. Login C weekly (all models) read 73% at boot; rule is stop at 74%, so this pilot handed over before any code. Run it on login A (week 15%, reset 2026-11-13) or login B.

Goal (operator voice 2026-11-07): a broadcast or ask must be answered within 1 minute, not 60; plus a health check of how we ship.

## Job 1: signals answer within 1 minute
Card: `MyTradingSys/system/tasks/signal-broadcast-wait-and-prio-1107.json` (state raw: fill goal/scope/steps/done_when/tests with `tasks.py fill`, then `tasks.py check`, `tasks.py take`).
1. `mts_signal.py wait [--max M] [--host H]`: one bounded loop, fetch the `mts-signals` branch every 60 s, exit 0 and print the record on the FIRST new inbound signal for this host or login (ask, ack of this host's broadcast, answer, HIGH broadcast); exit 2 on timeout.
2. `broadcast` and `ask` take `--wait M`: run that loop after sending, print the acks table.
3. Prompt hook status lines sorted: open asks first, then HIGH none/told-expired, then by age; cap 3 lines plus "n more: mts_signal.py acks". (Boot today showed 13 unsorted `[MTS BROADCAST ... status]` lines.)
4. `supervisor.py wait` returns within 60 s on a new ask or HIGH broadcast for its host.
5. One line in PARALLEL.md or SUPER_SESSION.md: a broadcast or ask is followed by `mts_signal.py wait` (never fire and move on).
6. Tests (fake signals clone in tmp): `wait` returns on a planted ask and times out otherwise; hook ordering with 5 mixed records. Each must fail on pre-change code first.
7. Ship: `PYTHONIOENCODING=utf-8 python scripts/dev/sync.py ship -m "signals: wait + --wait, sorted status lines, watcher wakes on asks" --result "<measured: wait returned in N s on a planted ask>" --next END: 1-minute signals`. Then one HIGH broadcast with `--cmd "python scripts/dev/mts_signal.py wait --max 1"` and your own `wait --max 10`.

## Job 2: SHIP_HEALTH.md
Output: `MyTradingSys/research/health_2026-11-07/SHIP_HEALTH.md`, tables, each number with its command. Items: (1) ship gate p50/p90 wall time 7 days, failures, `--again` count, "ORPHAN gate tree ... kill failed" (find in sync.py, why the kill fails on Windows, fix as raw card); (2) CI red events on origin/fast-track 7 d, time red, reverts; (3) `artifacts.py stale`; (4) `mts_doctor.py`, `status_board.py` summary; (5) signals: broadcasts none/told > 2 h per host, avg ask-to-answer 3 days; (6) `sync.py where`, tidy, stray python/claude processes; (7) top-5 time sinks, each fix a raw card (`tasks.py new ... --lane SONNET|HAIKU`, `tasks.py fill ... --note`).
Ship `--result "<p50/p90 gate min, n failures, n stale pages>" --next <top card id>`.

## Seed facts already seen at boot (re-measure, do not trust)
- doctor WARN SHIP-TIME: ship_wall n=8 median 140 s, p90 5121 s; gate n=15 median 13.5 min, max 63.4 min.
- doctor WARN HOOK-REG: main checkout 446 commits behind origin/fast-track (main-checkout owner fast-forwards it).
- doctor WARN SIZE-HEADROOM: CLAUDE.md at its size cap, SURFACE_POLICY.md near it (no room to add rules).
- Stale claims (>170 h): hot-wallet-watch-verify-5-eth-addresses, lf-session-timing-gpt-rederive, news-hot-wallet-watch, pizzino-layer-dashboard-where-we-are-lev.
- Open asks at boot: q-7257c1 to jis-laptop told 19 min; broadcasts b-8612ff ... b-fc3654 stuck at told for jis-nuc / jis-laptop (many 1 h+): evidence for the receiver-side problem.
- Login B (JIS-NUC) asked for unclaimed cards (broadcast 1753Z), weekly ~90%.

## Rules that bite
Ultra: `get_usage` first, waves of at most 4 agents, at most 8 total, each result in a file under `research/health_2026-11-07/`. Second ship within 10 min needs `--again`. Record any decision in OPERATOR_DECISIONS.md with an `Answer:` line.
