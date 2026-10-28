# Token audit (last 7 days, this host)

Source: ~/.claude/projects/*/*.jsonl usage fields, one row per assistant message id.

## By label (means per session)

| label | sessions | turns | first-turn input | cache read | cache write | fresh input | output |
|---|---|---|---|---|---|---|---|
| dispatcher-kick | 4 | 21 | 65188 | 1671109 | 72368 | 44 | 10452 |
| other | 30 | 43 | 66469 | 7013199 | 136619 | 88 | 37410 |

## Per session

| started | label | turns | tools | first-turn input | cache read | cache write | output |
|---|---|---|---|---|---|---|---|
| 2026-10-06T19:30:47.256Z | other | 1 | 0 | 58863 | 0 | 58861 | 281 |
| 2026-10-07T10:51:12.777Z | other | 49 | 47 | 66878 | 4727738 | 84328 | 30738 |
| 2026-10-07T12:49:51.291Z | other | 17 | 18 | 66293 | 1386844 | 50516 | 9597 |
| 2026-10-07T12:53:05.761Z | other | 68 | 75 | 63437 | 7464458 | 91498 | 30477 |
| 2026-10-07T13:57:49.239Z | other | 4 | 5 | 66084 | 257351 | 33510 | 3627 |
| 2026-10-07T14:01:35.991Z | other | 37 | 45 | 63519 | 3977538 | 90585 | 31097 |
| 2026-10-07T16:10:41.364Z | other | 9 | 4 | 73488 | 677987 | 41646 | 5972 |
| 2026-10-07T16:10:41.364Z | other | 7 | 3 | 73488 | 508546 | 33915 | 4446 |
| 2026-10-07T19:08:43.816Z | other | 5 | 1 | 65091 | 318528 | 29896 | 2390 |
| 2026-10-07T21:22:24.499Z | other | 11 | 9 | 69516 | 808832 | 39107 | 6386 |
| 2026-10-07T23:11:49.087Z | other | 79 | 88 | 63775 | 17532486 | 543640 | 91004 |
| 2026-10-08T07:52:18.412Z | other | 45 | 45 | 67066 | 4905109 | 101845 | 38860 |
| 2026-10-08T08:03:34.052Z | other | 61 | 63 | 63978 | 10179306 | 177700 | 81069 |
| 2026-10-08T08:08:26.463Z | other | 17 | 18 | 63769 | 1212416 | 62072 | 6482 |
| 2026-10-08T19:42:41.668Z | other | 36 | 36 | 63912 | 4197043 | 273179 | 39481 |
| 2026-10-09T01:06:26.367Z | other | 86 | 99 | 64782 | 21331793 | 336396 | 173494 |
| 2026-10-09T13:30:24.837Z | other | 18 | 17 | 71417 | 1588190 | 61250 | 8952 |
| 2026-10-09T14:35:16.587Z | other | 17 | 21 | 63752 | 1878264 | 81283 | 5831 |
| 2026-10-09T17:38:34.847Z | other | 42 | 41 | 63318 | 3643385 | 61905 | 14155 |
| 2026-10-09T18:11:02.198Z | other | 36 | 44 | 62644 | 3885439 | 180879 | 25865 |
| 2026-10-09T20:05:30.788Z | other | 272 | 273 | 67545 | 74284250 | 432657 | 206219 |
| 2026-10-09T20:14:03.427Z | other | 44 | 47 | 68735 | 5219958 | 114718 | 49534 |
| 2026-10-09T20:46:54.565Z | other | 43 | 44 | 67646 | 4638883 | 101863 | 26462 |
| 2026-10-09T22:15:24.178Z | other | 39 | 39 | 71908 | 3502414 | 58650 | 17440 |
| 2026-10-10T09:12:15.954Z | other | 45 | 48 | 66417 | 5083418 | 97410 | 18107 |
| 2026-10-10T09:40:52.205Z | other | 48 | 43 | 66397 | 5043832 | 148116 | 31026 |
| 2026-10-11T17:58:15.983Z | other | 30 | 31 | 66519 | 3413964 | 99481 | 26633 |
| 2026-10-11T18:05:52.258Z | other | 53 | 128 | 68601 | 6401905 | 199737 | 59609 |
| 2026-10-11T18:47:48.072Z | dispatcher-kick | 26 | 24 | 64840 | 1904803 | 86254 | 6804 |
| 2026-10-11T19:17:42.014Z | dispatcher-kick | 28 | 27 | 65610 | 2547471 | 117085 | 16030 |
| 2026-10-11T19:39:14.548Z | other | 65 | 77 | 67606 | 9928334 | 304926 | 63309 |
| 2026-10-11T19:47:41.662Z | dispatcher-kick | 18 | 19 | 65616 | 1431996 | 47754 | 10311 |
| 2026-10-11T19:59:26.426Z | other | 29 | 24 | 67651 | 2397764 | 107026 | 13778 |
| 2026-10-11T20:17:41.898Z | dispatcher-kick | 12 | 13 | 64686 | 800168 | 38380 | 8664 |

## Findings (JIS-NUC transcripts, 7 days; Sonnet relay ritual)

- Always-loaded context (first-turn input): 63k-73k tokens in every session, dispatcher or not.
  Mean dispatcher-kick session: 21 turns x ~65k = ~1.37M of its 1.67M cache-read tokens (~82%) is that same
  prefix re-read each turn. Work output is ~10k tokens per kick session; fresh input is ~44.
- No idle-tick transcript exists on this host in the window (idle ticks are not separately logged here),
  so the idle-tick cost is a floor of one ~65k first turn + 3 short turns, estimated, NOT measured.
- Longest non-relay session: 272 turns, 74.3M cache read (2026-10-09T20:05). Cost scales turns x context.

## Ranked cuts (proposed, not applied; follow-up cards b172-trim, b172-template)

| # | driver | cut | expected saving |
|---|---|---|---|
| 1 | ~65k always-loaded prefix x every turn | Trim what loads in unattended runs: project CLAUDE.md (long), memory index, 30+ skill descriptions, MCP server instructions; use a minimal relay CLAUDE/settings profile | up to 30-50% of cache reads per kick session |
| 2 | Turns per kick session (21 mean) | Template the ritual into ONE script call (worktree, sync start, claim, brief) so the model starts at the task, not the setup | ~8-10 turns, ~0.5-0.6M cache read |
| 3 | Re-reading NEXT_SESSION.md (42 lines, long task list) | Hand the session only its ONE task card, not the whole queue | few k per session, fewer wrong picks |
| 4 | Cache writes 38k-117k per kick (context grows via tool output) | Cap tool output (tail/--quiet flags in sync.py/relay.py, no ls/head probes) | ~20-40k write tokens |
| 5 | Open-ended long sessions (272 turns) | Enforce the existing 50k-token / 5-turn hand-off rule with a turn cap in the relay prompt | removes the 10x outliers |

Re-run: `python scripts/dev/token_audit.py --days 7 --out MyTradingSys/research/TOKEN_AUDIT_<date>.md`.
