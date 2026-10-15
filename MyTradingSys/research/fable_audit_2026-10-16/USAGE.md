# Usage meters: Fable 5.1 adversarial review session (2026-10-15, UTC)

Source: `get_usage` (Claude Code Win App, account jishusharma1985, plan Max). Stop rule: all-models weekly +6 points -> write up and ship. Not hit.

| Reading | UTC (approx) | 5-hour | Weekly all models | Weekly Fable | Extra usage | Session context |
|---|---|---|---|---|---|---|
| first (boot) | 2026-10-15T19:24Z | 18 % (resets 22:39Z) | 35 % (resets 10-20 20:00Z) | 3 % | off, 0.00 / 40.00 USD | 88 k / 1 M (9 %) |
| last (before ship) | 2026-10-15T19:42Z | 30 % | 36 % | 6 % | off, 0.00 / 40.00 USD | 194 k / 1 M (19 %) |
| delta | 18 min | +12 | +1 | +3 | 0 | +106 k |

Tool turns: 19 of the lifted 40-turn cap at the last reading (ship + release follow, no model-heavy work). The Fable weekly meter moved
3 points for one review of six questions across ~6 k changed lines incl. five pre-change test runs in a throwaway worktree.

## Other sessions at boot (`list_sessions`, newest first; running = isRunning true)
| Session | State | Branch / cwd |
|---|---|---|
| Super session 2: overnight testnet pipeline (super-2) | idle 19:24Z, remote control | claude/vigorous-cori-1f5764 |
| Gate speed-up: quick ship check; CI runs the full suite (gate-speedup) | RUNNING 19:23Z | claude/sweet-hellman-11e9c1 |
| Fable 5.1 model usage and optimization | idle 19:14Z | claude/fable-5-1-usage-optimization-ea36c5 |
| Mts dispatcher (4 rows 15:08Z..19:08Z) | idle | repo root |
| Fable 5.1 MTS builder pilot (pinned) | idle 18:54Z | claude/fable-5-1-mts-pilot-c833f8 |
| Usage pacer: mts-budget.json into dispatch gate | idle 18:28Z | claude/wizardly-hugle-dfafdb |
| CBP analyst feed (3x daily, Haiku) | idle 17:19Z | CryptoScrapper |
| Coordinator 2: drain ship queue, archive, disk (coord-2) | idle 17:10Z | claude/eloquent-meitner-0c4171 |

Only one other session was running during this review (gate-speedup), so the +1 on the all-models meter is mostly this session plus that one.
