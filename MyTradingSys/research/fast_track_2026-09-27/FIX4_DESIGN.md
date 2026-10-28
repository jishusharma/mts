# FIX4 design decisions (2026-09-28, coordinator)

Scope: findings left open by FIX3 that need a decision before code. Each decision picks the
fail-safe option; each has a named test that must fail on the current code first.
Implementation order: after NUC tasks 026/028 land (same files), together with M4/L1/L2
(tests already in `testnet/offline/test_fix4_offline.py`).

## M2 - HALT_DAILY_LOSS auto-resumes at 00:00 UTC
Decision: **existence blocks**, whatever the date. Only an operator deleting the file resumes trading.
A past-dated file refuses with "HALT_DAILY_LOSS from <date> still present - operator must review and delete".
Why: daily_loss_monitor's own contract says a hard halt does not auto-resume; a breach at 23:59 must
not resume at 00:00.
Change: executor `_check_halt_files` (the valid_past branch becomes a refusal). The FIX3 M1 tests for a
past date flip from "warns" to "refuses"; update them in the same change.
Test: `test_M2_past_dated_halt_daily_loss_blocks`.

## L3 - market-entry B079 post-fill breach is journaled only
Decision: after the stop is placed, if the real post-fill worst-case loss is below `max_loss_usd`
(more negative), **fail_closed("B079 post-fill: worst-case loss X exceeds cap Y")**. Flattening costs the
spread; running an over-cap position is worse. The stop is already live, so fail_closed's C3 order holds.
Test: `test_L3_market_fill_beyond_cap_flattens` (mark jumps between preflight and fill).

## L6 - daily PnL counts deposits and transfers; breached_today never re-arms
Decision part 1 (re-arm): if `breached_today` is true and HALT_DAILY_LOSS is ABSENT (the operator cleared
it), set `breached_today = False` and journal "re-armed by operator clear". A day still beyond the cap then
halts again on the next poll. That is intended: resuming on a breached day needs an explicit
`--cap-usd` override.
Test: `test_L6_rearms_after_operator_clears_halt`.
Decision part 2 (PnL source): unresolved until confirmed on testnet. Candidate: Deribit account-summary
session P/L fields instead of equity delta. They exclude deposits, but they reset at the exchange
settlement time, not 00:00 UTC. Next step (T2, testnet only): extend `testnet/probe_account_summary.py`
output with every *pl* field, run a 10 USD round trip, and record which fields moved. Decide after that.
Until then, document the limitation in daily_loss_monitor's docstring (no code change).

## Routing
| Item | Tier | Depends on |
|---|---|---|
| M2 + L3 code + tests | Sonnet (T3), Opus diff review | 026/028 applied |
| M4/L1/L2 code (tests exist) | Sonnet (T3), Opus diff review | 026/028 applied |
| L6 part 1 code + test | Qwen draft (T1), Haiku test | 027 applied (soak) - independent file, can go now |
| L6 part 2 probe | Haiku (T2) on testnet | none |
| Testnet re-run of all suites | Haiku (T2) | all of the above |

## RESULT (2026-09-28, JIS-NB, Deribit testnet, code at b05c1cf)
- Offline: staged 127 OK (2 skipped); run_all_tests --quick ALL PASS.
- Testnet: probe PASS (flat, equity 99.99992234); base C1-C6 6/6; G1/G2 4/4; FT-2 T-b..T-e 4/4;
  kill_switch --confirm KILL 0 errors, HALT written then removed; final probe flat, no open orders.
- Still open: L6 part 2 (PnL source; needs the testnet P/L-field probe). NUC 032 (re-arm) is queued.

## L6 part 2 - probe RESULT (2026-09-28, testnet, probe_pl_fields.py, 10 USD round trip)
- balance and equity each fell 6e-06 BTC per trade (fees). total_pl went 0 -> +1e-08 -> 0 and session_rpl
  moved only 1e-08: **neither includes fees**, so total_pl is NOT a valid daily-loss measure (it would
  miss fee bleed). The worker's "use total_pl" recommendation is rejected.
- Decision: keep equity delta (it counts P/L and fees) and correct it for deposits and transfers. Next
  probe (T2, testnet): private/get_transaction_log over the day, sum the entries by type, and confirm that
  deposit/transfer types can be subtracted. Until then the limitation stays documented; no deposits or
  transfers happen on this account today.
- Unverified: the claim that session_* fields reset at ~08:00 UTC settlement (not checked against the docs).

## L6 part 2 - transaction-log probe RESULT and DECISION (2026-09-28, testnet, probe_transaction_log.py, read-only)
- Today's log: 174 entries, all type=trade, sum(change) = -0.00006600 BTC (P/L incl. fees; the worker's
  equity "sanity check" was circular - it inferred start equity from the same sum - so it proves nothing).
- DECISION: daily P/L = sum(change) over today's (00:00 UTC) get_transaction_log entries EXCLUDING only
  money-movement types (deposit, withdrawal, transfer*). Settlement/delivery/funding entries are trading
  P/L and are INCLUDED. This replaces the equity delta and removes the deposit/transfer distortion.
- Implementation: after NUC 032 lands (same file, daily_loss_monitor.py). Test: fake transaction logs with
  trade + transfer + settlement entries -> only the transfer is excluded. Independent check before trusting it:
  compare against day_start_equity from a monitor state file written at 00:00 UTC on a quiet day.
