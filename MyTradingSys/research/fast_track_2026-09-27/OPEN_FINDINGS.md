# Open Findings

Comprehensive tracking of all findings from FIX3 and FIX4 efforts. Only rows with status "OPEN" are listed in STATUS.md.

## Findings Table

| ID | Status | Fixed-In Commit | Note |
|---|---|---|---|
| C1 | FIXED | c4c5507 (FIX3) | Transport error handling, OrderStateUnknown, retries |
| C2 | FIXED | c4c5507 (FIX3) | Protective exception handling + fail_closed |
| C3 | FIXED | c4c5507 (FIX3) | Flatten halt + position re-read before cancel |
| H1 | FIXED | c4c5507 (FIX3) | Individual cancel try/except, flatten always runs |
| H2 | FIXED | c4c5507 (FIX3) | Kill switch writes HALT before auth |
| H3 | FIXED | c4c5507 (FIX3) | Daily loss breach handling + 3-failure fallback |
| H4 | FIXED | c4c5507 (FIX3) | Atomic save_state with atomic os.replace |
| H5 | FIXED | c4c5507 (FIX3) | query_failed never re-places, counts toward timeout |
| H6 | FIXED | c4c5507 (FIX3) | Suite helpers refuse HALT mid-run, plan_id <= 24 chars |
| M1 | FIXED | c4c5507 (FIX3) | Valid past date only, strict YYYY-MM-DD format |
| M2 | FIXED | b05c1cf (FIX4) | Any HALT_DAILY_LOSS blocks until operator deletes |
| M3 | FIXED | c4c5507 (FIX3) | utf-8-sig then utf-16 with ValueError handling |
| M4 | FIXED | b05c1cf (FIX4) | HALT re-checked before every create, stop never blocked |
| M5 | FIXED | c4c5507 (FIX3) | fail_closed writes execution/HALT first |
| M6 | FIXED | c4c5507 (FIX3) | plan_id must match ^[A-Za-z0-9_-]{1,24}$, _xlabel raises |
| M7 | FIXED | 879d4af | Unresolved orders on closed/halted plans are soak issue |
| M8 | FIXED | b05c1cf (FIX4) | Single-plan-only contract documented |
| L1 | FIXED | b05c1cf (FIX4) | Position flat comparison uses target fills vs entry fill total |
| L2 | FIXED | b05c1cf (FIX4) | Target OrderStateUnknown sweeps label, remaining not reduced |
| L3 | FIXED | b05c1cf (FIX4) | Market entry B079 post-fill breach -> fail_closed |
| L4 | FIXED | 879d4af | Unprotected-window timer on monotonic() |
| L5 | FIXED | b05c1cf (FIX4) | Sleep after entry-deadline cancel pass |
| L6 | OPEN | 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) | Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet |
| L7 | FIXED | 879d4af | Missing pnl_usd raises ValueError |
