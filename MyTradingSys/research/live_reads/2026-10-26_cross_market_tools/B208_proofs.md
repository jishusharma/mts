# B208 proofs: Eagle_Eyes does not get smarter with use (collected 2026-10-27 07:00Z, worktree mts-live-market-reader)

## What the operator asked
"How Eagle_Eyes gets smarter every time it is used?" Answer today: it does not. A lesson lives in one chat and one append-only log, and nothing reads it back.

## Proof 1: the role file carries no lessons, scoring or habits
- `MyTradingSys/system/roles/eagle_eyes.md` is 69 lines. `grep -i "lesson|learn|score|habit"` finds only line 8 (the "running state lives in the log file" sentence).
- The role file has no 79,923 / 79,836 rule, no ladder rule, no "RSI means Malkan 40-60 only", no report-only-flips rule. All of these came from the operator or from my own misses in chat and exist only in the conversation and its summary.
- `git log -- roles/eagle_eyes.md` (last 8 commits, 10-18 to 10-26): stale-text fix, role merges, Think mode v4, retoken after a path rewrite. None adds a learned rule from live use.

## Proof 2: the same mistake repeated three times in one session
- Break call cancelled on a single 5m close above 79,836 at 03:30Z, 05:00Z and 06:10Z. Each reclaim failed within about 20 minutes.
- The lesson was written once in READ.md (section "2026-10-27 04:30Z", line 154: "next time wait for a close above 79,923"). It is free text, and after the first failure it did not stop the second and third cancels.

## Proof 3: lessons sit in an append-only log nobody indexes
- `READ.md` for 10-17 has 13 dated sections from 10-19 to 10-27. The lesson is at line 154 inside the event-4 section. A new session would have to read about 160 lines to find it, and nothing tells it to.
- `events.md` scores divergence events 1 to 4 by hand. No file holds one row per CALL with call, time, level, outcome, hit or miss.

## Proof 4: the data to score calls exists and is not used
- `watch_rows.csv` has 893 rows (one per minute, BTC, ES, NQ, gap, r1h, flags) plus Binance 5m klines. Every break, fade and cancel call can be scored from it mechanically. It is done by hand, once a day at best, or not at all.

## Proof 5: the same misses were found by the operator, not by the role
- Said the BTC triggers still worked during the Yahoo ES stall: wrong (poll() raised before states()). Found when the operator asked about the blind period.
- Said "no 5m close above 79,836 since 05:00Z" while the 05:15Z candle had closed 79,883. Found while writing the next reply.
- Neither check exists as a step. A self-check that reads the klines before asserting a level would have caught both.

## Proof 6: compaction erases habits (see B207)
- Habits kept only in chat ("read charts as they arrive, attach the ladder", "report only flips and 5m-close calls") survive a compaction only if the summary happens to mention them.
