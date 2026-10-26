# Token audit (last 1 days, this host)

Source: ~/.claude/projects/*/*.jsonl usage fields, one row per assistant message id.

## By label (means per session)

| label | sessions | turns | first-turn input | cache read | cache write | fresh input | output |
|---|---|---|---|---|---|---|---|
| dispatcher-idle | 10 | 10 | 64965 | 820876 | 43487 | 21 | 3249 |
| dispatcher-kick | 2 | 21 | 65797 | 1717302 | 54820 | 42 | 7765 |
| other | 5 | 25 | 71670 | 3165925 | 105763 | 52 | 19327 |
| relay-session | 1 | 61 | 70165 | 6431898 | 86679 | 130 | 27204 |

## Per session

| started | label | turns | tools | first-turn input | cache read | cache write | output |
|---|---|---|---|---|---|---|---|
| 2026-10-11T13:59:50.378Z | other | 32 | 27 | 69846 | 2764139 | 103399 | 14271 |
| 2026-10-11T18:14:21.394Z | relay-session | 61 | 57 | 70165 | 6431898 | 86679 | 27204 |
| 2026-10-11T20:42:32.787Z | dispatcher-idle | 13 | 21 | 66754 | 946704 | 57160 | 2797 |
| 2026-10-12T05:35:17.794Z | dispatcher-idle | 17 | 17 | 61408 | 1397313 | 75660 | 5249 |
| 2026-10-12T05:35:18.440Z | other | 17 | 19 | 67512 | 2132152 | 102040 | 5425 |
| 2026-10-12T05:35:18.498Z | dispatcher-kick | 31 | 34 | 64761 | 2676977 | 71680 | 13588 |
| 2026-10-12T05:39:10.756Z | dispatcher-idle | 11 | 13 | 66671 | 862057 | 54849 | 1627 |
| 2026-10-12T05:53:52.010Z | dispatcher-idle | 18 | 17 | 62375 | 1349670 | 42750 | 7788 |
| 2026-10-12T06:04:54.836Z | dispatcher-idle | 19 | 21 | 71054 | 1550536 | 47807 | 8520 |
| 2026-10-12T06:40:18.750Z | dispatcher-idle | 4 | 4 | 64997 | 240840 | 20315 | 467 |
| 2026-10-12T13:08:11.584Z | other | 49 | 56 | 82927 | 8286061 | 194141 | 64923 |
| 2026-10-12T14:11:21.164Z | dispatcher-idle | 14 | 15 | 61407 | 1056416 | 69997 | 4030 |
| 2026-10-12T14:28:46.051Z | other | 21 | 23 | 70557 | 1671952 | 49201 | 9119 |
| 2026-10-12T15:43:59.264Z | other | 10 | 13 | 67509 | 975322 | 80034 | 2897 |
| 2026-10-12T18:42:34.931Z | dispatcher-idle | 5 | 4 | 66749 | 316347 | 27328 | 527 |
| 2026-10-12T19:42:36.027Z | dispatcher-idle | 4 | 4 | 66830 | 258762 | 15981 | 570 |
| 2026-10-13T04:59:39.244Z | dispatcher-idle | 4 | 4 | 61407 | 230115 | 23026 | 922 |
| 2026-10-13T04:59:39.353Z | dispatcher-kick | 11 | 11 | 66834 | 757628 | 37961 | 1942 |

## Before / after (b172-trim, written 2026-10-13, first rerun)

Baseline = TOKEN_AUDIT_2026-10-12.md (first-turn input 65188, mean cache read 1671109). Output caps shipped in the relay prompts before the 2026-10-13 kick.

| metric | baseline 2026-10-12 | this rerun (dispatcher-kick) | verdict |
|---|---|---|---|
| kick sessions measured | - | 2 (only 1 after the caps: 2026-10-13T04:59) | NOT ENOUGH, bar is 3+ |
| first-turn input | 65188 | 65797 (post-cap kick 66834) | NOT BELOW baseline |
| mean cache read per kick | 1671109 | 1717302 (post-cap kick 757628, 11 turns) | one short kick, not comparable |

Reading: first-turn input is flat at about 61-67k for every label, so it is the harness prefix (tool schemas, deferred-tool list, skill list, MCP instructions, CLAUDE.md, memory index) and cannot be cut from the prompt files. The only lever so far is fewer turns per kick. The 2026-10-13 kick used 11 turns versus 31 on 2026-10-12.
Cannot be trimmed from inside a scheduled task: tool schemas, skill list, MCP server instructions (App-controlled).
Open: rerun after 3 post-cap kicks (`token_audit.py --days 3`) and fill the table; card stays open.
