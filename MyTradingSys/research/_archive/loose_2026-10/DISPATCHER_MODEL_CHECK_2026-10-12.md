Superseded 2026-10-14: the routine model comes only from the App routine settings (memory routine-model-check); a `model:` front matter never applies.

# Dispatcher model check (2026-10-12, JIS-NUC)

Claim under test: `model: sonnet` in ~/.claude/scheduled-tasks/mts-dispatcher/SKILL.md pins every dispatcher run to Sonnet.
Method: every transcript under ~/.claude/projects whose first user turn starts `<scheduled-task name="mts-dispatcher"`,
counted assistant turns by `message.model`. 20 runs, 2026-10-12 00:39-16:47 local.

| Result | Runs |
|---|---|
| claude-sonnet-5-5 only | 14 (6 are 2-turn idle ticks) |
| claude-opus-5-5 only (28-53 turns) | 6 (01:12, 01:38, 14:06, 14:25, 14:38, 15:28 local) |
| one run also had 7 haiku turns | 1 (the 15:28 Opus run) |

Verdict: NOT reliably honoured. Opus runs are full relay sessions, not idle ticks, so they are the expensive ones.
Open question (card: Q40 in NEXT_SESSION.md): is it a fallback after a Sonnet usage limit (the session fallback chain lists Opus next),
or the task's own saved model setting overriding the frontmatter? Evidence not yet gathered: the App's scheduled-task settings
for mts-dispatcher, and whether Opus runs cluster after Sonnet-limit messages in those transcripts.
Cost note: ~6 of 14 non-idle runs on Opus; the project instruction is Sonnet for every session.

## Cause and verdict (JIS-NUC relay session, 2026-10-12 12:50 UTC; all times below UTC)
Evidence (21 dispatcher transcripts, model per assistant turn, plus each run's `model` attachment and cost-state):
- Opus runs are consecutive blocks, not scattered: 10-11 19:17 + 19:47, 10-12 07:17 + 07:47 + 08:17 + 08:47. Runs either side of a block are Sonnet (20:17 after the first; 09:17 after the second).
  The `model` attachment says Opus from the first turn, so the session STARTED on Opus: it is not a mid-run fallback after a limit
  (no limit/overload system entries in any run). Two blocks of 2 and 4 half-hourly ticks is what a launch-time default that
  changed in the App for a while looks like (the App's own model picker / session default applied to scheduled launches), not the frontmatter being ignored per run.
- Frontmatter `model: sonnet` is honoured when the App default is Sonnet (14 of 14 other runs, incl. this one: 09:17, 09:47, 11:47, 12:17, 12:47).
- Pin available to us: none. `update_scheduled_task` has no model field (title/prompt/description/cron/enabled/notify only); `list_scheduled_tasks` shows none.
  Not testable from a session: the App's per-task model setting (UI only).
- Cost: Opus runs 0.91-1.77 USD vs Sonnet 0.79-0.97 USD in cost-state; the 6 Opus runs added about 3-5 USD. Small, bounded, self-healing.
Verdict: CANNOT PIN from code; frontmatter is honoured whenever the App default is Sonnet. Operator-side check (one UI look, no action
needed unless a block repeats): keep the App default model on Sonnet while scheduled tasks run. Detect a repeat with
`python scripts/dev/` model-per-run count above (script logic: first user turn contains `name="mts-dispatcher"`, count `message.model`).
