# Blind-monitor halt policy (testnet)

Status: adopted 2026-10-17, card `blind-monitor-halt-recovery`. Code: `MyTradingSys/execution/daily_loss_monitor.py`
(`BlindRecovery`, `write_blind_halt`, `halt_kind`); tests: `test_dlm_blind_recovery.py`, `test_dlm_failure_cap.py`.

## Source labels
- **OPERATOR** 2026-10-17 (OPERATOR_DECISIONS.md, section blind-monitor-halt-recovery): "Monitor clears only its own blind
  halt after the account reads cleanly for 30 minutes", with the note "For now - see what should be done for future - the
  correct implementation and then adopt that policy".
- **OURS**: every other number and rule below (flap guard, daily cap, hold file, in-memory window). None has a trader
  transcript source, and none is a trading parameter: they only decide when a halt the monitor itself wrote is lifted.
  Tune them from new halt evidence, not by feel.

## Evidence
Blind halts are written when the monitor fails to read the account 20 times in a row (about 10 min at the 30 s poll).
- 2026-10-06 14:44Z: Deribit HTTP 502 (halt_history `HALT_DAILY_LOSS_2026-10-06_deribit502`).
- 2026-10-07: 19:24Z DNS blip, 3 x getaddrinfo failures, which led to the 20-failure testnet cap; a second halt at 21:50:40Z
  (`HALT_DAILY_LOSS_20261007_215040.txt`).
- 2026-10-12 14:44:49Z: 20 consecutive failures, last `public/auth` HTTP 502 (task card sources).
- Three blind halts in 7 days, all transport-level (502, DNS), none a loss; each stopped testnet trading until a human cleared it.

Gap: the halt_history files themselves live only on the JIS-NB live tree (the repo's `halt_history/` holds just `.gitkeep`),
so this design cites them through the task card and `TESTNET_STATUS_2026-10-07.md`, not by reading the files.

## Rule
1. **Only its own halt.** A blind halt is a HALT_DAILY_LOSS JSON carrying `"kind": "blind"` and `"owner": "daily_loss_monitor"`.
   Everything else (a loss halt, an untagged or torn file, a file owned by someone else) is a loss halt and is never
   auto-cleared. The preflight in `executor.py` reads only existence, date and reason, so the extra keys change nothing there.
2. **Never overwrite a loss halt.** If a loss halt exists when the monitor goes blind, it leaves the file alone.
3. **Clean window: 30 min (OPERATOR, interim).** The clock starts at the first successful read after the last failure.
   A failure, a breach reading (`ok` false) or `breached_today` resets it. The account reading counts the aggregate
   (main plus named subaccounts) exactly as the loss check does, so a real loss in the window blocks the clear.
4. **Non-trade balance moves.** Deposits, withdrawals and transfers do not enter the transaction-log P&L, so they neither
   cause nor block a clear (same source as the loss check).
5. **Memory only.** The window is in process memory: a restart (or a deploy) starts the 30 minutes again.
6. **Flap guard (OURS).** At most 2 auto-clears per UTC day (counted in the monitor state file, `blind_clears`, which resets
   with the day baseline). A blind halt written less than 60 min after the last clear is not auto-cleared. Both stop a
   flaky link from cycling trading on and off; the third blind halt of a day waits for a human.
7. **Stays alive.** On testnet the monitor no longer exits after writing a blind halt; it keeps reading so it can clear.
   `--once` still writes the halt and exits 1.
8. **Mainnet unchanged.** Cap of 3 failures, untagged halt (`HALT_DAILY_LOSS_MAINNET`), process exits 1, never auto-cleared,
   even if a blind-tagged file were somehow present.

## Who is told
The clear is a journal `reconciliation` event (`blind halt auto-cleared`, clean seconds, clears today) and a line on the
monitor's stdout. The halt itself was already logged and printed when written. The Control Room and the testnet status
report already read the journal and `halt_history`; a refused clear (cap, flap, hold) leaves the halt in place, which
those reports already show as an active HALT.

## Human override
- **Pin:** create `execution/HALT_DAILY_LOSS.hold` (any content). While it exists the monitor never auto-clears.
- **Clear by hand:** delete HALT_DAILY_LOSS as before; the monitor re-arms on its next iteration.
- Builders and sessions never create, edit or delete these files; only the operator does.

## Deploy
The live tree runs the old code (exit 1 at the blind halt, no clearing) until the supervisor's next deploy and restart.
