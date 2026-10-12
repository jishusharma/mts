# Recreate the relay tasks on another host (JIS-NUC)

The files here are the JIS-NB prompts (copied 2026-10-11). Recreate with `mcp__scheduled-tasks__create_scheduled_task` (taskId = file name before `.SKILL.md`, prompt = file body).
Paths inside the prompts are JIS-NB paths: replace `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` with the NUC live tree and `mts-refiner` with a NUC worktree.

## Superseded 2026-10-12
The NUC does not copy these prompts and there is no `--standby-hours`: both hosts run a dispatcher and `relay.py kick --peer-quiet-min N`
keeps one out while the other is moving. Rules, the generic prompt and recovery: `TWO_HOST.md` in this folder.

## GPT-lane watchdog (2026-10-12)
`mts-lane-watch.SKILL.md` is the hourly Haiku watchdog for `scripts/dev/lane_health.py` (taskId `mts-lane-watch`, cron `15 * * * *`, one host is enough; JIS-NB if the NUC is the thing being watched).
It is the second line: `codex_run.py tick` on JIS-NUC already runs `lane_health.py sweep --apply --ship --beat` every 30 min with no model. The watchdog catches what that cannot: a NUC that is off
(no heartbeat for 3 h). The frontmatter model is only a request (Q40: the App default decides); the task is two Bash calls either way.
