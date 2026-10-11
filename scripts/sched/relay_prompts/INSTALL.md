# Recreate the relay tasks on another host (JIS-NUC)

The files here are the JIS-NB prompts (copied 2026-10-11). Recreate with `mcp__scheduled-tasks__create_scheduled_task` (taskId = file name before `.SKILL.md`, prompt = file body).
Paths inside the prompts are JIS-NB paths: replace `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` with the NUC live tree and `mts-refiner` with a NUC worktree.

## Superseded 2026-10-12
The NUC does not copy these prompts and there is no `--standby-hours`: both hosts run a dispatcher and `relay.py kick --peer-quiet-min N`
keeps one out while the other is moving. Rules, the generic prompt and recovery: `TWO_HOST.md` in this folder.
