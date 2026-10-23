# Ultra pilot review: CBP run, then Krown run (Supervisor C, inside the super session)

Operator ask (2026-10-23): run both ultra pilots inside the super session; record how much they consume, what they do right and
wrong, what to improve: context and compaction, whether the agents are good, how to plan tasks for performance and economy together.

## How it is measured
- Host: Supervisor C session (Opus 5.5, 1M context) launches each run as one Workflow (background); agents are Sonnet, Haiku for
  preflight and meters.
- Usage: a Haiku `meter` agent reads `get_usage` at start, after each phase and at the end (5 h % and weekly %). Other sessions share
  the account (3 Builders were running at launch), so a phase delta is an upper bound, not the run's own cost. Exact per-agent tokens
  come from the Workflow transcript dir (agent-*.jsonl) after the run.
- Per agent: tool calls, problems, improvements (self-reported in a fixed schema), plus my check of its claims against git.
- Host context: `get_usage` context % for this session before and after (compaction = the host's risk, not the agents').

## Baseline (before CBP launch, 2026-10-23 ~12:50Z)
| reading | value |
|---|---|
| 5 h window | 27% (resets 13:40Z) |
| weekly all models | 18% (resets 10-27 20:00Z) |
| weekly Fable | 6% |
| host context | 125.9k / 1M (13%), auto-compact at 97% |
| other load | 3 Builders running (login-roll-call, confluence-s1, Habib) |

## CBP run (wf_810d7427-0bf)
Pending: phase meters, per-agent table, verdict, findings.

## Krown run
Not started: waits for the CBP run to end and for S1 (confluence-s1-context-counts) on trunk.

## Comparison: single background Agents this session (same account, same hour)
| worker | model | tokens | tool calls | minutes | outcome |
|---|---|---|---|---|---|
| Builder: Habib (Qriptal channel) ledger + plan scorer | sonnet | 108.6k | 35 | 34 | shipped 95fcdb20f; 81 rows, 2 eligible; plan study blocked (9 plans all in holdout) |
| Haiku claim check of that ship | haiku | 53.2k | 5 | 1.1 | 5/5 claims confirmed |
Lesson so far: a Haiku re-check costs about half a Sonnet card's tokens in 5 calls; most of it is the injected CLAUDE.md and tool schemas, not the work.

## Findings: right / wrong / improve
Pending.
