# Deploy the liquidation event log on the Lenovo (operator yes 2026-10-30)

Owner: the Lenovo coordinator (Supervisor A or the operator's Lenovo session). Commit `a0704527f` is in `origin/green/fast-track`.
What it does: `BinanceLiquidationAccumulator` appends every forceOrder event (BTCUSDT, ETHUSDT) to `runtime_data/liq_events/<SYMBOL>.jsonl` (about 150 B per line; est. 1-3 MB a day; log never blocks the feed).

1. Lenovo, live tree `C:\MTS\mts-live`: `sync.py where` clean; copy `MyTradingSys/runtime/orderflow_live/_state.json` to `runtime_data/deploy_backup/<stamp>/`.
2. `git -C C:\MTS\mts-live merge --ff-only origin/green/fast-track` (DEPLOY_RUNBOOK section 1). Never reset or rebase.
3. `mvn -q compile` in the live tree; run `LiquidationEventLogTest` (5 tests).
4. Restart ONLY the statemachine JVM (`Main statemachine <symbol>`, now builds and connects the BTCUSDT and ETHUSDT liquidation accumulators next to StateCodeEmitter), via the loop (DEPLOY_RUNBOOK section 2). Coordinator-run, in a window with NO open position_manager trades. Do not touch position_manager, auto_trader, HALT files or open trades. Scheduler mode (`Scheduler.java`) writes the same files and must not run alongside the statemachine JVM.
5. Check within 30 min: `runtime_data/liq_events/BTCUSDT.jsonl` and `ETHUSDT.jsonl` exist and grow (cwd is the repo root, start-trading-day.ps1 `cd $R`); JVM log has no "event log" or "Liquidation log not started" errors.
6. `mts_signal.py ack <broadcast id> done` with the file size; ship one line to `ISSUES_REGISTER.md`.
Access: the folder is gitignored runtime data; other devices read it through `live_mirror.py publish`, not by share. If a device cannot read it, file a bug card.
