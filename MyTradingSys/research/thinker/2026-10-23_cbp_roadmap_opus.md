# CBP roadmap (Opus audit draft, relayed by Thinker), 2026-10-23
Source: Opus session, JIS-NB login C. Its turn meter blocked its own Write; Thinker wrote this file from its closing message. Numbers OURS. Unchecked items say NOT_CHECKED.

## Page 1, plain words
The operator is right. CBP should fetch, extract and store; layers ask the store when they need something. The queue, consumer and acks are extra hops nothing in MTS needs, and they are where the scheduler and kill-switch talk came from.
- Keep: one fetcher, one store, the quote check, duplicate removal, the backtest gate (B139) for anything that trades.
- Replace: queue, consumer and acks with one read function `cbp.query(analyst, symbol, since, max_age)`.
- Nothing is scheduled on this machine (login C, JIS-NB).

## 1. Where we are (verified by Opus on JIS-NB)
1. App scheduled-task list is empty; none of 348 Task Scheduler entries mentions CBP or CryptoScrapper.
2. Three unregistered routine files remain under `C:\Users\E-ngineers\.claude\scheduled-tasks\`: `cbp-daily-workflow`, `mts-control-room`, `mts-dispatcher`. They never run. The CBP one still calls the deleted `fetch_latest.ps1`.
3. CBP commit 152726b (2026-10-23 18:27, jishusharma) already adds producer gates, a 15-case golden set, `.github/workflows/golden.yml`, the Krown proof ack and docs. Do not rebuild.
4. CBP working tree has an uncommitted manual run from 22 Oct 10:51 (extractions +240 lines, 24 processed transcripts, consensus/actionable/dashboard rewritten), not logged in `docs/SESSIONS.md`.
5. MTS side referencing CBP in Python: `consumer.py` (105 l), `cbp_adapter.py` (146 l) and their two tests.
NOT_CHECKED: duplicate quote checkers and stores across CBP and `research/*`; D5 text vs this; logins A and B.

## 2. Verdict per component
| Component | Verdict |
|---|---|
| Fetcher, store, extraction | KEEP |
| Quote gate, duplicate removal, golden set + CI | KEEP |
| B139 backtest gate | KEEP, for trading only |
| Schema | SIMPLIFY: the store's row format |
| Freshness | SIMPLIFY: a `max_age` argument |
| `cbp_adapter.py` | SIMPLIFY: fold into the read function |
| `pending.json`, acks, `consumer.py` | DELETE |
| Scheduler / routine, kill criteria | DELETE |
| D5 spec | AMEND |

## 3. Data flow
request -> fetch only if missing -> one LLM pass per new transcript -> quote check + duplicate removal -> one store -> `cbp.query()` -> layers. Orders still pass B139.

## 4. Steps
| Step | What | Turns (OURS) |
|---|---|---|
| R | Operator checks other logins (below) | 0 |
| 0 | Decide the 22 Oct run (D1) | 1 |
| 1 | Count duplicates across CBP and `research/*` | 3 |
| 2 | Write `cbp.query` with a fail-first test | 4 |
| 3 | Keep one quote checker | 3 |
| 4 | Point the existing layer at `cbp.query`; delete consumer and adapter | 3 |
| 5 | Remove queue and acks; amend D5 | 2 |
| 6 | Jason+Michael layer reads `cbp.query` | its own card |
About 16 turns vs about 40 in the ultra plan.

Per-login checklist (R): 1. app > Scheduled: "No scheduled tasks yet". 2. Task Scheduler: search cbp, crypto, mts: nothing. 3. List `~/.claude/scheduled-tasks/`. 4. Report "none" to the coordinator.

## 5. Opus vs Thinker
Agree on everything except: Thinker's shipped list missed 152726b and the 22 Oct run, and the golden set, CI and producer gates already exist.

## 6. Operator decisions (defaults)
- D1, the 22 Oct run: commit as data after it passes the quote check.
- D2, the three leftover routine files: delete them.
- D3, store location: leave at `F:/CryptoScrapper`, MTS reads in place; do not copy into the public MTS repo.

## 7. Scope amendment (operator 2026-10-23, verbatim quotes)
- Window: "we will have a bias from the last 10 days of what the artists are saying. Analyst, I mean" and "5 days to 10 days of data is already good enough". Never more than 10 days.
- Output per analyst: "extracting their quotes, their trades, their pointers, their bias, and filter them in such a way that we have a useful way of using it inside MTS".
- Layers later: "extraction we will do individually, and it will be targeted on what we need to do". Analyst layers (Krown; Jason+Michael) get their own targeted extraction; CBP does not.
- Where it plugs into MTS: "a later question". CBP's job now: "find the value which is in CBP that could be provided to MTS".
Effect on the plan (OURS): `cbp.query` default `since` = 10 days; extraction profile = bias, quotes, trades, pointers only; anything older than 10 days is not extracted or kept in the query path; the 22 Oct run is inside the window (D1 stands). Step 1 adds: measure how many of the 10-day rows are tradable vs bias-only, so the value to MTS is a number, not a belief.
