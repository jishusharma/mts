# MTS-2026-10-08-1900Z-APP-BLD-deploy-push-cleanup

- State: pushed to origin/fast-track at 5122e8a (merge, retention task, runner log, kline refresh, CLAUDE.md quick answers). Live runner + consensus hook deployed by file checkout (staged, uncommitted in the live tree on purpose so the supervisor's ff-only deploy still works); MTS-Supervisor now also starts at logon +90 s; one htf_context_live loop stopped.
- Next: (1) Java `mvn compile` + JVM restart window for the SetupScreener removal and StateCodeEmitter change; (2) check why position_manager was not in the process list at 00:47 IST; (3) confirm a Dumps/consensus row appears after the next Fabio alert / Tom card advance; (4) after the next reboot confirm runner + auto_trader are up within ~2 min of logon.
- Worktree ../mts-push (branch jisnb/push-merge) is the place to merge/gate/push from; never from the live tree.
