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
