# Recreate the relay tasks on another host (JIS-NUC)

The files here are the JIS-NB prompts (copied 2026-10-11). Recreate with `mcp__scheduled-tasks__create_scheduled_task` (taskId = file name before `.SKILL.md`, prompt = file body).
Paths inside the prompts are JIS-NB paths: replace `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` with the NUC live tree and `mts-refiner` with a NUC worktree.

## NUC = standby, not second primary
- Create only `mts-dispatcher` (rename `mts-dispatcher-standby`), `mts-relay-a`, `mts-relay-b` (manual-only), NOT `mts-control-room` (its page belongs to the NB account until shared).
- Standby rule (card `relay-two-host-standby` adds `relay.py kick --standby-hours N`): the NUC kicks only when the NB has launched nothing for N hours (default 4). Until that flag ships, leave the NUC dispatcher disabled so the same handoff id is never launched twice.
- Self-pacing step 3b of the prompt works unchanged: BUSY */10, IDLE hourly. On NUC use IDLE = `0 8-22 * * *` to save the Pro budget; BUSY only while the NB is silent.
- Keep `~/.claude/mts-relay-stop` as the kill switch on both hosts.
